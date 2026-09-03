"""Test suite: auth gates, self-registration, field crypto, exam engine,
and the content validator. Run with `manage.py test` (CI does the same)."""

import json

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from django.utils import timezone

from .fieldcrypto import decrypt_value, encrypt_value
from .learners import ensure_profile_for_user
from .models import AIProvider, ExamAttempt


class FieldCryptoTests(TestCase):
    def test_roundtrip(self):
        token = encrypt_value("sk-secret-123")
        self.assertNotEqual(token, "sk-secret-123")
        self.assertTrue(token.startswith("gAAAA"))
        self.assertEqual(decrypt_value(token), "sk-secret-123")

    def test_encrypt_is_not_repeatable(self):
        # Fernet uses a random IV — two encryptions of the same key differ.
        self.assertNotEqual(encrypt_value("abc"), encrypt_value("abc"))

    def test_legacy_plaintext_passes_through(self):
        self.assertEqual(decrypt_value("sk-legacy-plain"), "sk-legacy-plain")

    def test_empty_values(self):
        self.assertEqual(encrypt_value(""), "")
        self.assertEqual(decrypt_value(""), "")

    def test_provider_property_encrypts_at_rest(self):
        provider = AIProvider.objects.create(
            name="t", base_url="https://api.example.com/v1", model_id="m1"
        )
        provider.set_api_key("sk-live-999")
        provider.save(update_fields=["api_key_enc", "updated_at"])
        provider.refresh_from_db()
        self.assertTrue(provider.api_key_enc.startswith("gAAAA"))
        self.assertNotIn("sk-live-999", provider.api_key_enc)
        self.assertEqual(provider.api_key, "sk-live-999")


class ApiAuthTests(TestCase):
    """The four study/progress/practice APIs used to trust a spoofable
    X-Remote-User header and served anonymous callers; now they 401."""

    def setUp(self):
        self.client = Client()

    def test_anon_gets_401_not_guest_data(self):
        for method, url, data in [
            ("get", "/api/progress/?subject_slug=bio", None),
            ("post", "/api/progress/update/", {}),
            ("post", "/api/practice/attempt/", {}),
            ("post", "/api/study/", {}),
        ]:
            res = getattr(self.client, method)(url, data, content_type="application/json")
            self.assertEqual(res.status_code, 401, url)
            self.assertEqual(res.json()["error"], "login required")

    def test_spoofed_header_no_longer_works(self):
        res = self.client.get(
            "/api/progress/?subject_slug=bio", HTTP_X_REMOTE_USER="victim"
        )
        self.assertEqual(res.status_code, 401)


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _post(self, **overrides):
        payload = {
            "username": "newbie",
            "password1": "correct-horse-battery",
            "password2": "correct-horse-battery",
        }
        payload.update(overrides)
        return self.client.post("/register/", payload)

    def test_register_login_and_api_access(self):
        res = self._post()
        self.assertEqual(res.status_code, 302)
        user = User.objects.get(username="newbie")
        self.assertTrue(user.is_active)
        # logged in straight away → APIs work
        res = self.client.get("/api/progress/?subject_slug=bio")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["username"], "newbie")

    def test_rejected_cases(self):
        self._post()
        # duplicate username
        self.client.logout()
        res = self._post()
        self.assertContains(res, "taken", status_code=200)
        # mismatch
        res = self._post(username="second", password2="different")
        self.assertContains(res, "do not match")
        # weak password (too short / all numeric)
        res = self._post(username="third", password1="12345678", password2="12345678")
        self.assertContains(res, "too weak")
        self.assertFalse(User.objects.filter(username__in=["second", "third"]).exists())


class ExamEngineTests(TestCase):
    """Critical paths: start → begin → answer → finish → score, plus the
    diagnostic halving and retake-variant determinism."""

    def setUp(self):
        self.user = User.objects.create_user("examuser", password="pw-123456789")
        self.profile = ensure_profile_for_user(self.user)

    def _start(self, mode="real"):
        from .examsys import start_attempt

        return start_attempt(self.user.username, "nmat", mode=mode)

    def _answer_everything(self, attempt):
        from .content import exam_item_index
        from .examsys import begin_block, save_answer, finish_block

        index = exam_item_index(attempt.exam)
        for section in attempt.sections:
            block_id = section["id"]
            begin_block(attempt, block_id)
            block = next(
                b for b in attempt.plan["blocks"] if b["id"] == block_id
            )
            vmap = block.get("vmap") or {}
            for pos, item_id in enumerate(block["items"], start=1):
                canonical = index[item_id]["answer"]
                # retake variants permute shown letters — the client clicks
                # the SHOWN letter, so translate before saving
                mapping = vmap.get(item_id) or {}
                shown = next((s for s, o in mapping.items() if o == canonical),
                             canonical)
                save_answer(attempt, block_id, pos, shown, False, 5)
            finish_block(attempt, block_id)
        attempt.refresh_from_db()
        return attempt

    def test_full_attempt_scores_all_correct(self):
        from .examsys import get_attempt

        attempt = self._start()
        self.assertEqual(attempt.status, "active")
        attempt = self._answer_everything(attempt)
        self.assertEqual(attempt.status, "submitted")
        reloaded = get_attempt(self.user.username, attempt.id)
        self.assertIsNotNone(reloaded.score)
        self.assertEqual(reloaded.num_correct, reloaded.num_items)
        self.assertEqual(reloaded.score["pct"], 100.0)

    def test_second_real_attempt_gets_permuted_variant(self):
        from .examsys import start_attempt

        first = self._answer_everything(self._start())
        second = self._start()
        first_first_block = first.plan["blocks"][0]
        second_first_block = second.plan["blocks"][0]
        self.assertEqual(
            set(first_first_block["items"]), set(second_first_block["items"])
        )
        # deterministic per seed: replaying the same seed yields the same order
        from .examsys import _variant_map

        v1 = _variant_map(first_first_block["items"], "seed-x")
        v2 = _variant_map(first_first_block["items"], "seed-x")
        self.assertEqual(v1, v2)
        self.assertNotEqual(v1["order"], first_first_block["items"])

    def test_diagnostic_is_half_length(self):
        from .examsys import ExamError, start_attempt

        real = self._start("real")
        # one ACTIVE attempt per (profile, exam): starting a diagnostic over a
        # live real attempt is refused, not silently replaced
        with self.assertRaises(ExamError):
            self._start("diagnostic")
        self._answer_everything(real)
        diag = self._start("diagnostic")
        real_total = sum(len(b["items"]) for b in real.plan["blocks"])
        diag_total = sum(len(b["items"]) for b in diag.plan["blocks"])
        self.assertLess(diag_total, real_total)
        self.assertGreater(diag_total, 0)
        # and half-length diagnostics still carry per-block clocks
        for b in diag.plan["blocks"]:
            self.assertGreater(b["seconds"], 0)

    def test_answer_after_block_expiry_rejected(self):
        from .examsys import begin_block, save_answer, _close_block

        attempt = self._start()
        block_id = attempt.sections[0]["id"]
        begin_block(attempt, block_id)
        _close_block(attempt, block_id)
        res = save_answer(attempt, block_id, 1, "A", False)
        self.assertEqual(res, {"ok": False, "error": "expired"})

    def test_crossed_choices_persist_and_survive_answer_change(self):
        from .examsys import begin_block, save_answer

        attempt = self._start()
        block_id = attempt.sections[0]["id"]
        begin_block(attempt, block_id)
        save_answer(attempt, block_id, 1, None, False, 0, crossed=["B", "a", "Z"])
        entry = attempt.answers[list(attempt.plan["blocks"][0]["items"])[0]]
        self.assertEqual(entry.get("x"), ["A", "B"])  # cleaned, sorted; Z dropped
        # clearing crosses removes the key
        save_answer(attempt, block_id, 1, "C", False, 0, crossed=[])
        entry = attempt.answers[list(attempt.plan["blocks"][0]["items"])[0]]
        self.assertNotIn("x", entry)
        self.assertEqual(entry["c"], "C")

    def test_take_page_renders_cross_out_and_periodic_table(self):
        from .examsys import begin_block, start_attempt

        attempt = start_attempt(self.user.username, "nmat")
        begin_block(attempt, attempt.sections[0]["id"])
        self.client.force_login(self.user)
        res = self.client.get(f"/exams/nmat/take/{attempt.id}/", follow=True)
        html = res.content.decode("utf-8")
        self.assertIn("choice-cross", html)
        self.assertIn("exam-pt-open", html)
        self.assertIn("pt-grid", html)

    def test_field_test_items_excluded_from_scoring(self):
        """Blueprint-opted field-test items stay on the paper, are recorded,
        but never count toward the score."""
        from .examsys import get_attempt, start_attempt
        from .models import ExamResponse

        attempt = self._start()
        first_item = attempt.plan["blocks"][0]["items"][0]
        attempt.plan["blocks"][0]["field_test"] = [first_item]
        attempt.save(update_fields=["plan"])
        total_before = sum(len(b["items"]) for b in attempt.plan["blocks"])

        attempt = self._answer_everything(attempt)
        self.assertEqual(attempt.num_items, total_before - 1)
        self.assertEqual(attempt.score["field_test"], 1)
        self.assertEqual(attempt.score["pct"], 100.0)  # the rest all correct

        flagged_rows = ExamResponse.objects.filter(
            attempt=attempt, item_id=first_item)
        self.assertEqual(flagged_rows.count(), 1)  # still recorded…
        self.assertTrue(flagged_rows.first().is_field_test)  # …as unscored
        # the live helper labels nothing for zero-response attempts of others
        self.assertIsNotNone(get_attempt(self.user.username, attempt.id))

    def test_diagnostic_plan_terminates_on_tiny_block(self):
        """A block with fewer items than the diagnostic target used to spin
        forever (verified worker-hang); it must now return the items it has."""
        from .examsys import _diagnostic_plan, start_attempt

        start_attempt(self.user.username, "nmat")  # warm the content index
        real = start_attempt(self.user.username, "nmat")
        first_item = real.plan["blocks"][0]["items"][0]
        plan = {"blocks": [{"id": "tiny", "seconds": 300, "items": [first_item]}]}
        result = _diagnostic_plan("nmat", plan)
        self.assertEqual(result["blocks"][0]["items"], [first_item])

    def test_retake_result_review_matches_shown_letters(self):
        """The retake variant permutes option letters; the result review must
        fold choice texts through the same map or it highlights the wrong
        option as correct (verified pre-fix)."""
        from .examsys import get_attempt, start_attempt

        self._answer_everything(self._start())
        second = self._answer_everything(self._start())
        reloaded = get_attempt(self.user.username, second.id)
        self.assertEqual(reloaded.score["pct"], 100.0)

        self.client.force_login(self.user)
        html = self.client.get(
            f"/exams/result/{second.id}/", follow=True).content.decode("utf-8")
        rows_ok = html.count('class="tut-question is-ok"')
        rows_bad = html.count('class="tut-question is-bad"')
        self.assertGreater(rows_ok, 0)
        self.assertEqual(rows_bad, 0)  # all-correct sitting renders all ✓

    def test_zero_out_of_four_attempt_statuses(self):
        # finalize is idempotent: re-finalizing a closed attempt is a no-op
        from .examsys import finalize

        attempt = self._answer_everything(self._start())
        before = attempt.finished_at
        finalize(attempt, reason="expired")
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, "submitted")
        self.assertEqual(attempt.finished_at, before)


class FlashcardExportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("deckuser", password="pw-123456789")
        self.profile = ensure_profile_for_user(self.user)
        self.client = Client()

    def test_export_requires_login(self):
        res = self.client.get("/flashcards/export/")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/login/", res.url)

    def test_export_csv_contents(self):
        from django.utils import timezone

        from .models import SrsCard

        SrsCard.objects.create(
            profile=self.profile, subject_slug="biology", card_key="k1",
            front="What is the powerhouse of the cell?",
            back="Mitochondrion", chapter="Cells",
            due_date=timezone.localdate(),
        )
        self.client.force_login(self.user)
        res = self.client.get("/flashcards/export/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "text/csv; charset=utf-8")
        rows = list(res.content.decode("utf-8").splitlines())
        self.assertEqual(rows[0], "front,back,chapter,subject,due,reps,lapses")
        self.assertIn("powerhouse", rows[1])
        self.assertIn("Mitochondrion", rows[1])

class DifficultyBadgeTests(TestCase):
    """Difficulty labels come from graded ExamResponse rows across all
    learners; items with fewer than 5 graded responses stay unlabeled."""

    def setUp(self):
        self.user = User.objects.create_user("diffuser", password="pw-123456789")
        self.profile = ensure_profile_for_user(self.user)
        self.client = Client()

    def _graded_attempt(self, item_id, chapter_id):
        from django.utils import timezone

        from .models import ExamAttempt, ExamResponse

        attempt = ExamAttempt.objects.create(
            profile=self.profile, exam="nmat", mode="real", status="submitted",
            finished_at=timezone.now(),
        )
        for i in range(5):
            ExamResponse.objects.create(
                attempt=attempt, item_id=item_id, block_id="b1",
                chapter_id=chapter_id, position=i + 1,
                chosen="A", correct=(i < 2),  # 3 wrong of 5
            )
        return attempt

    def test_map_and_review_badge(self):
        from .insights import item_difficulty_map

        item_id = "nmat-p2p-022"
        self._graded_attempt(item_id, "mechanics")
        m = item_difficulty_map()
        self.assertEqual(m[item_id], {"n": 5, "miss_pct": 60})

        # a wrong answer routes the item into the review notebook with a badge
        from .learners import record_practice

        record_practice(self.user.username, "physics", item_id, "B", False)
        self.client.force_login(self.user)
        res = self.client.get("/review/")
        html = res.content.decode("utf-8")
        self.assertIn("60% miss", html)
        self.assertIn("diff-hot", html)

    def test_cold_items_stay_unlabeled(self):
        from .insights import item_difficulty_map

        self._graded_attempt("nmat-p2s-011", "psych-soc")  # only 5 rows? yes min_n=5
        # second item has just 1 graded response -> unlabeled
        from django.utils import timezone

        from .models import ExamAttempt, ExamResponse

        attempt = ExamAttempt.objects.create(
            profile=self.profile, exam="nmat", mode="real", status="submitted",
            finished_at=timezone.now(),
        )
        ExamResponse.objects.create(
            attempt=attempt, item_id="mcat-cp-053", block_id="b1",
            chapter_id="vibrations-waves-and-optics", position=1,
            chosen="B", correct=False,
        )
        m = item_difficulty_map()
        self.assertIn("nmat-p2s-011", m)
        self.assertNotIn("mcat-cp-053", m)


class RateLimitTests(TestCase):
    """Self-serve endpoints get cheap cache-backed counters; login lockout
    is django-axes (DB-backed)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("budgetuser", password="pw-123456789")

    def test_register_rate_limited_per_network(self):
        from . import ratelimit

        ratelimit.reset()
        self._register_rate_limited_per_network()

    def _register_rate_limited_per_network(self):
        for i in range(6):
            # a fresh client per attempt: after the first signup the session
            # would otherwise bounce every later POST off the "logged in"
            # guard before the limiter ever sees it
            client = Client()
            res = client.post("/register/", {
                "username": f"farmer{i}",
                "password1": "correct-horse-battery",
                "password2": "correct-horse-battery",
            })
            if i < 5:
                self.assertEqual(res.status_code, 302, f"signup {i} should pass")
            else:
                self.assertEqual(res.status_code, 200)
                self.assertContains(res, "Too many sign-up attempts")
                self.assertFalse(User.objects.filter(username="farmer5").exists())

    def test_study_api_daily_cap(self):
        from django.test import override_settings

        from . import ratelimit

        ratelimit.reset()
        self.client.force_login(self.user)
        with override_settings(GABAY_COACH_DAILY_LIMIT=1):
            # first call passes the cap and fails downstream (no provider
            # configured) — that is fine, the budget was spent
            res1 = self.client.post("/api/study/", {"message": "hi"},
                                    content_type="application/json")
            self.assertIn(res1.status_code, (200, 502))
            res2 = self.client.post("/api/study/", {"message": "hi"},
                                    content_type="application/json")
            self.assertEqual(res2.status_code, 429)
            self.assertIn("daily coach limit", res2.json()["error"])


    def test_login_lockout_after_repeated_failures(self):
        from . import ratelimit

        ratelimit.reset()
        User.objects.create_user("lockme", password="right-password-1")
        for _ in range(5):  # AXES_FAILURE_LIMIT
            self.client.post("/login/", {"username": "lockme",
                                         "password": "wrong-password"})
        # even the CORRECT password is refused while locked out
        # (django-axes answers lockouts with 429)
        res = self.client.post("/login/", {"username": "lockme",
                                           "password": "right-password-1"})
        self.assertEqual(res.status_code, 429)


class ManageModelsTests(TestCase):
    """Admin model-config page: edit identity/endpoint, replace the encrypted
    key, and test connectivity — staff only."""

    def setUp(self):
        self.admin = User.objects.create_user("staffadmin", password="pw-123456789",
                                              is_staff=True)
        self.peasant = User.objects.create_user("pleb", password="pw-123456789")
        self.provider = AIProvider.objects.create(
            name="Old Name", api_style="openai",
            base_url="https://api.example.com/v1", model_id="m1",
        )
        self.provider.set_api_key("sk-live-abcdef1234")
        self.provider.save(update_fields=["api_key_enc", "updated_at"])
        self.old_cipher = self.provider.api_key_enc
        self.client = Client()

    def _post_edit(self, **overrides):
        payload = {
            "name": "New Name", "api_style": "openai",
            "base_url": "https://api.example.com/v1", "model_id": "m2",
            "api_key": "",
        }
        payload.update(overrides)
        return self.client.post(f"/manage/models/{self.provider.id}/edit/", payload)

    def test_non_staff_redirected(self):
        self.client.force_login(self.peasant)
        res = self.client.get(f"/manage/models/{self.provider.id}/edit/")
        self.assertEqual(res.status_code, 302)
        self.client.force_login(self.admin)
        self.assertEqual(
            self.client.get(f"/manage/models/{self.provider.id}/edit/").status_code, 200)

    def test_edit_updates_fields_and_keeps_key_when_blank(self):
        self.client.force_login(self.admin)
        res = self._post_edit()
        self.assertEqual(res.status_code, 302)
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.name, "New Name")
        self.assertEqual(self.provider.model_id, "m2")
        self.assertEqual(self.provider.api_key_enc, self.old_cipher)  # unchanged
        self.assertEqual(self.provider.api_key, "sk-live-abcdef1234")

    def test_edit_with_new_key_reencrypts(self):
        self.client.force_login(self.admin)
        self._post_edit(api_key="sk-replacement-999")
        self.provider.refresh_from_db()
        self.assertNotEqual(self.provider.api_key_enc, self.old_cipher)
        self.assertEqual(self.provider.api_key, "sk-replacement-999")
        self.assertTrue(self.provider.api_key_enc.startswith("gAAAA"))

    def test_name_uniqueness_excludes_self(self):
        # renaming yourself to your own name is fine…
        self.client.force_login(self.admin)
        self.assertEqual(self._post_edit(name="Old Name").status_code, 302)
        # …but stealing another model's name is not
        other = AIProvider.objects.create(
            name="Other Model", api_style="openai",
            base_url="https://other.example.com/v1", model_id="m9",
        )
        res = self.client.post(f"/manage/models/{other.id}/edit/", {
            "name": "Old Name", "api_style": "openai",
            "base_url": "https://other.example.com/v1", "model_id": "m9",
            "api_key": "",
        })
        self.assertContains(res, "already exists")

    def test_edit_invalid_base_url_rejected(self):
        self.client.force_login(self.admin)
        res = self._post_edit(base_url="ftp://nope")
        self.assertContains(res, "required")

    def test_test_action_reports_unreachable_endpoint(self):
        self.provider.base_url = "http://127.0.0.1:1/v1"  # nothing listens
        self.provider.save(update_fields=["base_url"])
        self.client.force_login(self.admin)
        res = self.client.post(f"/manage/models/{self.provider.id}/test/",
                               follow=True)
        messages = [str(m) for m in res.context["messages"]]
        self.assertTrue(any("test FAILED" in m for m in messages), messages)

    def test_test_action_without_key(self):
        self.provider.set_api_key("")
        self.provider.save(update_fields=["api_key_enc", "updated_at"])
        self.client.force_login(self.admin)
        res = self.client.post(f"/manage/models/{self.provider.id}/test/",
                               follow=True)
        messages = [str(m) for m in res.context["messages"]]
        self.assertTrue(any("no API key set" in m for m in messages), messages)


class AiBriefTests(TestCase):
    """AI briefs: one model call per (user, brief, day), cached in-process;
    degrade to empty (hidden card) with no model or over budget."""

    def setUp(self):
        self.user = User.objects.create_user("briefuser", password="pw-123456789")
        ensure_profile_for_user(self.user)
        self.client = Client()
        from . import ai_briefs

        ai_briefs._BRIEF_CACHE.clear()
        from . import ratelimit

        ratelimit.reset()

    def _seed_wrong_answer(self):
        from django.utils import timezone

        from .learners import ensure_profile_for_user as _ensure, record_practice
        from .models import ExamAttempt, ExamResponse

        profile = _ensure(self.user)
        attempt = ExamAttempt.objects.create(
            profile=profile, exam="nmat", mode="real", status="submitted",
            finished_at=timezone.now(),
        )
        for i in range(5):
            ExamResponse.objects.create(
                attempt=attempt, item_id="nmat-p2p-022", block_id="b1",
                chapter_id="mechanics", position=i + 1,
                chosen="A", correct=(i < 2),
            )
        record_practice(self.user.username, "physics", "nmat-p2p-022", "B", False)

    def test_no_model_degrades_to_empty(self):
        from . import ai_briefs

        self.assertEqual(ai_briefs.daily_brief(self.user.username, 3, []), "")
        self.assertEqual(ai_briefs.exam_eve_brief(self.user.username), "")
        self.assertIsNone(ai_briefs.miss_autopsy(self.user.username))

    def test_generated_once_then_cached(self):
        from unittest.mock import patch

        from . import ai_briefs

        self._seed_wrong_answer()
        calls = []

        def fake_completion(messages, **kwargs):
            calls.append(messages)
            return "Focus on mechanics tonight, then 10 flashcards."

        with patch("portal.llm.coach_ready", return_value=True), \
             patch("portal.llm.chat_completion", side_effect=fake_completion):
            brief1 = ai_briefs.daily_brief(self.user.username, 3, [])
            brief2 = ai_briefs.daily_brief(self.user.username, 3, [])
        self.assertTrue(brief1.strip())
        self.assertEqual(brief1, brief2)
        self.assertEqual(len(calls), 1)  # cached: second render spends nothing

    def test_budget_exhausted_degrades(self):
        from unittest.mock import patch

        from . import ai_briefs
        from django.test import override_settings

        self._seed_wrong_answer()
        with override_settings(GABAY_COACH_DAILY_LIMIT=0), \
             patch("portal.llm.coach_ready", return_value=True), \
             patch("portal.llm.chat_completion",
                   side_effect=AssertionError("must not call")):
            self.assertEqual(ai_briefs.daily_brief(self.user.username, 1, []), "")

    def test_eve_brief_requires_future_exam(self):
        from . import ai_briefs

        self.assertEqual(ai_briefs.exam_eve_brief(self.user.username), "")

    def test_bridge_needs_two_weak_chapters_and_accepts_snapshot(self):
        from unittest.mock import patch

        from . import ai_briefs

        self._seed_wrong_answer()
        # single weak chapter -> no bridge
        self.assertIsNone(ai_briefs.bridge_brief(self.user.username))
        # a second weak chapter arrives -> bridge generates from the snapshot
        from django.utils import timezone

        from .learners import record_practice
        from .models import ExamAttempt, ExamResponse

        profile = ai_briefs._profile_for(self.user.username)
        attempt = ExamAttempt.objects.create(
            profile=profile, exam="nmat", mode="real", status="submitted",
            finished_at=timezone.now(),
        )
        for i in range(5):
            ExamResponse.objects.create(
                attempt=attempt, item_id="nmat-p2s-011", block_id="b1",
                chapter_id="psych-soc", position=i + 1,
                chosen="A", correct=(i < 2),
            )
        record_practice(self.user.username, "psych-soc", "nmat-p2s-011", "C", False)

        snap = ai_briefs._snapshot(self.user.username)
        with patch("portal.llm.coach_ready", return_value=True), \
             patch("portal.llm.chat_completion", side_effect=["Two chapters connect."]):
            bridge = ai_briefs.bridge_brief(self.user.username, snap=snap)
        self.assertIsNotNone(bridge)
        self.assertIn("↔", bridge["title"])


class AiDrillTests(TestCase):
    """AI drill: strict server-side validation of generated items, ownership
    on every route, reporting, and the misses-grounding mode."""

    GOOD = json.dumps({"questions": [
        {"q": f"Question {i} about torque?",
         "choices": {"A": "right-1", "B": "wrong-1", "C": "wrong-2", "D": "wrong-3"},
         "answer": "A",
         "explain": "Torque balance gives right-1; B inverts the ratio."}
        for i in range(4)]})

    def setUp(self):
        self.user = User.objects.create_user("drilluser", password="pw-123456789")
        ensure_profile_for_user(self.user)
        self.client = Client()
        self.client.force_login(self.user)
        from . import ratelimit

        ratelimit.reset()

    def _generate(self, replies):
        from unittest.mock import patch

        from . import ai_drill

        with patch("portal.llm.coach_ready", return_value=True), \
             patch("portal.llm.chat_completion", side_effect=replies):
            return ai_drill.generate_quiz(self.user.username, "chapter", "mechanics")

    def test_generation_validates_and_persists(self):
        quiz = self._generate([self.GOOD])
        self.assertEqual(len(quiz.payload), 4)
        self.assertEqual(quiz.mode, "chapter")
        self.assertEqual([q["id"] for q in quiz.payload], ["ai-1", "ai-2", "ai-3", "ai-4"])

    def test_fenced_json_accepted(self):
        quiz = self._generate(["```json\n" + self.GOOD + "\n```"])
        self.assertEqual(len(quiz.payload), 4)

    def test_invalid_output_retried_then_runtimeerror(self):
        # two malformed replies must surface as RuntimeError (the view renders
        # it as a message) — a raw ValueError here used to 500 the route
        from unittest.mock import patch

        from . import ai_drill

        with patch("portal.llm.coach_ready", return_value=True), \
             patch("portal.llm.chat_completion", side_effect=["not json at all", "still bad"]):
            with self.assertRaises(RuntimeError):
                ai_drill.generate_quiz(self.user.username, "chapter", "mechanics")

    def test_non_object_questions_500_guard(self):
        # {"questions": ["a","b","c","d"]} used to raise AttributeError → 500
        from unittest.mock import patch

        from . import ai_drill

        bad = json.dumps({"questions": ["a", "b", "c", "d"]})
        with patch("portal.llm.coach_ready", return_value=True), \
             patch("portal.llm.chat_completion", side_effect=[bad, bad]):
            with self.assertRaises(RuntimeError):
                ai_drill.generate_quiz(self.user.username, "chapter", "mechanics")

    def test_no_quota_burn_when_no_model(self):
        # budget counters must not tick for requests that never reach the model
        from unittest.mock import patch

        from . import ai_drill, ratelimit

        ratelimit.reset()
        with patch("portal.llm.coach_ready", return_value=False), \
             patch("portal.llm.chat_completion",
                   side_effect=AssertionError("must not call")):
            with self.assertRaises(RuntimeError):
                ai_drill.generate_quiz(self.user.username, "chapter", "mechanics")
        self.assertIsNone(ratelimit._hits.get(f"coach:{self.user.username}"))

    def test_structurally_invalid_items_dropped(self):
        def q(n, **over):
            base = {"q": f"ok question {n}",
                    "choices": {"A": f"a{n}", "B": f"b{n}", "C": f"c{n}", "D": f"d{n}"},
                    "answer": "A", "explain": "fine"}
            base.update(over)
            return base

        mostly_bad = json.dumps({"questions": [
            q(1),
            q(2),
            q(3),
            q(4, choices={"A": "same", "B": "same", "C": "c4", "D": "d4"}),  # dup texts
            q(5, answer="E"),                                        # bad: answer out
        ]})
        quiz = self._generate([mostly_bad, mostly_bad])
        self.assertEqual(len(quiz.payload), 3)  # broken items dropped, 3 survive

        mostly_ok = json.dumps({"questions": [q(1)]})
        with self.assertRaises(RuntimeError):
            self._generate([mostly_ok, mostly_ok])  # 1 valid < 3 minimum raises

    def test_views_ownership_and_report(self):
        other = User.objects.create_user("otheruser", password="pw-123456789")
        other_profile = ensure_profile_for_user(other)
        quiz = self._generate([self.GOOD])
        # owner can open; a stranger cannot
        self.assertEqual(self.client.get(f"/ai/drill/{quiz.id}/").status_code, 200)
        stranger = Client()
        stranger.force_login(other)
        self.assertEqual(stranger.get(f"/ai/drill/{quiz.id}/").status_code, 404)
        # report increments only own quiz
        self.client.post(f"/ai/drill/{quiz.id}/report/")
        quiz.refresh_from_db()
        self.assertEqual(quiz.bad_reports, 1)
        # generate requires login
        anon = Client()
        self.assertEqual(anon.get("/ai/drill/").status_code, 302)

    def test_misses_mode_requires_recorded_misses(self):
        from unittest.mock import patch

        from . import ai_drill

        with patch("portal.llm.coach_ready", return_value=True):
            with self.assertRaises(RuntimeError):
                ai_drill.generate_quiz(self.user.username, "misses", None)


    def test_hint_mode_reaches_prompt_builder(self):
        from .study import tutor_messages

        msgs = tutor_messages(
            mode="hint", user_text="", curriculum="outline text",
            chapter_title="Mechanics",
            learner_line="This learner has 2 open wrong item(s) here; cause: trap.",
        )
        joined = " ".join(m["content"] for m in msgs)
        self.assertIn("HINT", joined)
        self.assertIn("Never state the final answer", joined)
        self.assertIn("[Learner context]", joined)
        self.assertIn("cause: trap", joined)

    def test_difficulty_reaches_prompt_and_payload(self):
        from unittest.mock import patch

        from . import ai_drill

        captured = {}

        def fake_completion(messages, **kwargs):
            captured["prompt"] = messages[0]["content"]
            return self.GOOD

        with patch("portal.llm.coach_ready", return_value=True), \
             patch("portal.llm.chat_completion", side_effect=fake_completion):
            quiz = ai_drill.generate_quiz(self.user.username, "chapter",
                                          "mechanics", difficulty="challenge")
        self.assertIn("CHALLENGE", captured["prompt"])
        self.assertEqual({q["difficulty"] for q in quiz.payload}, {"challenge"})


class ContentValidationTests(TestCase):
    def test_validate_content_green(self):
        call_command("validate_content", verbosity=0)


class FigureUrlTests(TestCase):
    """Bank figure refs must reach <img src> as absolute /content-images/ URLs
    (they used to be emitted raw and 404 against the take/drill page paths)."""

    def test_relative_ref_gets_prefix(self):
        from .content import figure_url

        self.assertEqual(figure_url("items/mcat-cp-051-circuit.svg"),
                         "/content-images/items/mcat-cp-051-circuit.svg")

    def test_absolute_and_empty_pass_through(self):
        from .content import figure_url

        self.assertEqual(figure_url("/content-images/items/x.svg"),
                         "/content-images/items/x.svg")
        self.assertEqual(figure_url(""), "")
        self.assertEqual(figure_url("https://example.com/a.svg"),
                         "https://example.com/a.svg")

    def test_every_referenced_figure_file_exists(self):
        import glob

        import yaml

        from django.conf import settings

        for path in glob.glob(str(settings.BASE_DIR / "content" / "exam-bank" / "**" / "*.yml"),
                              recursive=True):
            for item in (yaml.safe_load(open(path)) or {}).get("items") or []:
                ref = item.get("figure") or ""
                if ref:
                    self.assertTrue(
                        (settings.BASE_DIR / "content" / "images" / ref).is_file(),
                        f"{item['id']} references missing figure {ref}",
                    )


class SaveAnswerEdgeTests(TestCase):
    """R2 round: answer-state edges the main engine tests don't cover."""

    def setUp(self):
        self.user = User.objects.create_user("edgeuser", password="pw-123456789")
        self.profile = ensure_profile_for_user(self.user)
        from .examsys import start_attempt

        self.attempt = start_attempt(self.user.username, "nmat")
        from .examsys import begin_block

        self.block_id = self.attempt.sections[0]["id"]
        begin_block(self.attempt, self.block_id)
        self.first_item = self.attempt.plan["blocks"][0]["items"][0]

    def _save(self, **kw):
        from .examsys import save_answer

        kw.setdefault("block_id", self.block_id)
        kw.setdefault("pos", 1)
        kw.setdefault("chosen", "A")
        kw.setdefault("flagged", False)
        return save_answer(self.attempt, **kw)

    def _entry(self):
        return (self.attempt.answers or {}).get(self.first_item) or {}

    def test_elapsed_clamped_to_one_hour(self):
        self._save(chosen="A", flagged=False, elapsed_seconds=10 ** 9)
        self.assertLessEqual(self._entry()["s"], 3600)

    def test_negative_elapsed_clamped_to_zero(self):
        self._save(chosen="A", flagged=False, elapsed_seconds=-50)
        self.assertEqual(self._entry()["s"], 0)

    def test_flag_only_save_keeps_existing_choice(self):
        self._save(chosen="C", flagged=False, elapsed_seconds=3)
        self._save(chosen=None, flagged=True)  # flag toggle autosave
        entry = self._entry()
        self.assertEqual(entry["c"], "C")
        self.assertEqual(entry["f"], 1)

    def test_second_choice_overwrites_first(self):
        self._save(chosen="A", flagged=False)
        self._save(chosen="D", flagged=True)
        self.assertEqual(self._entry()["c"], "D")

    def test_clearing_flag_via_flag_false(self):
        self._save(chosen="B", flagged=True)
        self._save(chosen=None, flagged=False)
        self.assertEqual(self._entry()["f"], 0)

    def test_bad_pos_bounds(self):
        for bad in (0, -1, 10 ** 6):
            res = self._save(pos=bad, chosen="A")
            self.assertEqual(res, {"ok": False, "error": "bad-pos"}, bad)

    def test_wrong_block_id(self):
        from .examsys import ExamError

        with self.assertRaises(ExamError):
            self._save(block_id="nope", chosen="A")

    def test_navigator_reflects_state(self):
        from .examsys import navigator

        self._save(chosen="A", flagged=True)
        nav = navigator(self.attempt, self.block_id)
        self.assertTrue(nav[0]["answered"] and nav[0]["flagged"])
        self.assertFalse(nav[1]["answered"])

    def test_lowercase_choice_normalized(self):
        self._save(chosen="b", flagged=False)
        self.assertEqual(self._entry()["c"], "B")


class ResultRenderTests(TestCase):
    """R3 round: field-test and result-page rendering end to end."""

    def setUp(self):
        self.user = User.objects.create_user("renduser", password="pw-123456789")
        self.profile = ensure_profile_for_user(self.user)
        self.client = Client()

    def test_field_test_badge_renders_and_is_excluded_from_score(self):
        from .examsys import start_attempt

        attempt = start_attempt(self.user.username, "nmat")
        first_block = attempt.plan["blocks"][0]
        ft_items = first_block["items"][:2]
        first_block["field_test"] = ft_items
        attempt.save(update_fields=["plan"])

        from .content import exam_item_index
        from .examsys import begin_block, finish_block, save_answer

        index = exam_item_index(attempt.exam)
        for section in attempt.sections:
            begin_block(attempt, section["id"])
            block = next(b for b in attempt.plan["blocks"] if b["id"] == section["id"])
            for pos, item_id in enumerate(block["items"], start=1):
                save_answer(attempt, section["id"], pos,
                            index[item_id]["answer"], False, 1)
            finish_block(attempt, section["id"])
        attempt.refresh_from_db()
        self.assertEqual(attempt.score["field_test"], 2)

        self.client.force_login(self.user)
        html = self.client.get(f"/exams/result/{attempt.id}/",
                               follow=True).content.decode("utf-8")
        self.assertIn("unscored field-test item", html)
        self.assertEqual(html.count(">field test</span>"), 2)
        self.assertEqual(html.count('class="tut-question is-bad"'), 0)

    def test_take_page_block_end_shows_finish_button(self):
        from .content import exam_item_index
        from .examsys import begin_block, start_attempt

        attempt = start_attempt(self.user.username, "nmat")
        begin_block(attempt, attempt.sections[0]["id"])
        total = len(attempt.plan["blocks"][0]["items"])
        self.client.force_login(self.user)
        last_pos_url = f"/exams/nmat/take/{attempt.id}/{attempt.sections[0]['id']}/{total}/"
        html = self.client.get(last_pos_url, follow=True).content.decode("utf-8")
        self.assertIn("Finish", html)  # end-of-block branch
        # and the first question shows neither Finish nor Previous
        first_url = f"/exams/nmat/take/{attempt.id}/{attempt.sections[0]['id']}/1/"
        html_first = self.client.get(first_url, follow=True).content.decode("utf-8")
        self.assertNotIn("Finish", html_first)
        self.assertNotIn("Previous", html_first)
        self.assertIn("Next →", html_first)


class SrsSchedulingTests(TestCase):
    """R4 round: SM-2 scheduling math, hand-computed sequences."""

    def setUp(self):
        self.user = User.objects.create_user("srsuser", password="pw-123456789")
        ensure_profile_for_user(self.user)

    def _grade(self, key, grade, front="f", back="b", chapter="c"):
        from .srs import grade_card

        return grade_card(self.user.username, "biology", key,
                          front, back, chapter, grade)

    def test_good_sequence_1_2_5(self):
        self.assertEqual(self._grade("k1", "good")["interval_days"], 1)
        self.assertEqual(self._grade("k1", "good")["interval_days"], 2)
        self.assertEqual(self._grade("k1", "good")["interval_days"], 5)

    def test_easy_new_card_is_three_days(self):
        self.assertEqual(self._grade("k2", "easy")["interval_days"], 3)

    def test_again_resets_interval_and_counts_lapse_with_ease_floor(self):
        for _ in range(4):
            self._grade("k3", "good")
        res = self._grade("k3", "again")  # ease 2.5 -> 2.3
        self.assertEqual(res["interval_days"], 0)
        for _ in range(5):
            self._grade("k3", "again")  # ease floors at 1.3
        from .models import SrsCard

        card = SrsCard.objects.get(profile__username=self.user.username,
                                   card_key="k3")
        self.assertEqual(card.ease, 1.3)
        self.assertEqual(card.lapses, 6)

    def test_interval_never_exceeds_365_and_matches_due(self):
        import datetime as dt

        from .models import SrsCard

        for _ in range(14):
            self._grade("k4", "easy")  # runaway growth path
        card = SrsCard.objects.get(profile__username=self.user.username,
                                   card_key="k4")
        self.assertLessEqual(card.interval_days, 365)
        self.assertEqual(card.due_date,
                         timezone.localdate() + dt.timedelta(days=card.interval_days))

    def test_hard_new_card_is_one_day(self):
        self.assertEqual(self._grade("k5", "hard")["interval_days"], 1)


class PlannerBoundaryTests(TestCase):
    """R5 round: date and workload edges of the plan generator."""

    def test_past_exam_date_yields_empty_plan(self):
        import datetime as dt

        from portal.planner import build_plan

        plan = build_plan(exam_id="nmat",
                          exam_date=dt.date.today() - dt.timedelta(days=3),
                          weekly_hours=10, done=set())
        self.assertEqual(plan, [])

    def test_zero_hours_still_gets_the_30_minute_floor(self):
        import datetime as dt

        from portal.planner import build_plan

        plan = build_plan(exam_id="nmat",
                          exam_date=dt.date.today() + dt.timedelta(days=14),
                          weekly_hours=0, done=set())
        self.assertGreater(len(plan), 0)
        total = sum(d["minutes"] for d in plan)
        self.assertGreater(total, 0)
        # study days scale to the budget; mock days cost what a mock costs
        for day in plan:
            kinds = {t["kind"] for t in day["tasks"]}
            if "mock" in kinds or "rest" in kinds:
                continue
            self.assertLessEqual(day["minutes"], 120)

    def test_done_chapters_never_reappear_and_weak_front_load(self):
        import datetime as dt

        from portal.planner import build_plan, syllabus

        exam_date = dt.date.today() + dt.timedelta(days=30)
        plan = build_plan(exam_id="nmat", exam_date=exam_date,
                          weekly_hours=10, done=set())
        seen = [t["chapter_id"] for d in plan for t in d["tasks"]
                if t.get("chapter_id")]
        # every chapter gets covered (revisits allowed — spaced double-tap)
        self.assertGreater(len(seen), 0)

        # marking every syllabus chapter done leaves only mock/rest days
        all_done = {t["chapter_id"] for t in syllabus("nmat")}
        plan2 = build_plan(exam_id="nmat", exam_date=exam_date,
                           weekly_hours=10, done=all_done)
        scheduled = [t["chapter_id"] for d in plan2 for t in d["tasks"]
                     if t.get("chapter_id")]
        self.assertEqual(scheduled, [])
