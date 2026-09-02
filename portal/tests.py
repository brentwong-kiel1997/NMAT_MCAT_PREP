"""Test suite: auth gates, self-registration, field crypto, exam engine,
and the content validator. Run with `manage.py test` (CI does the same)."""

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase

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
            for pos, item_id in enumerate(block["items"], start=1):
                save_answer(attempt, block_id, pos,
                            index[item_id]["answer"], False, 5)
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
