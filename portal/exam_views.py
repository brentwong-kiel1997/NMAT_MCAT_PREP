"""Views for the mock-exam engine.

House style: @require_GET/@require_POST, Http404 on bad ids, {ok: ...} JSON
APIs. Every stateful route requires a Django login — the shared nginx basic
auth maps everyone to one "guest" profile, which must never own an attempt.
"""

from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from . import content, examsys, insights
from .content import all_bank_items, exam_bank_errors, exam_blueprint, exam_defs
from .examsys import ExamError
from .models import ExamAttempt


def _error_snapshot() -> list[str]:
    return exam_bank_errors()


@require_GET
def exam_list(request):
    all_defs = exam_defs()  # hoisted: each call is a full deepcopy
    defs = []
    for exam_id in sorted(all_defs):
        doc = all_defs[exam_id]
        bp = doc.get("blueprint") or {}
        if not bp.get("blocks"):
            continue
        attempts = []
        if request.user.is_authenticated:
            attempts = list(
                ExamAttempt.objects.filter(profile__username=request.user.username,
                                           exam=exam_id)
                .exclude(status="active").order_by("-started_at")[:5]
            )
        defs.append({"id": exam_id, "doc": doc, "blocks": bp.get("blocks") or [],
                     "attempts": attempts})
    return render(request, "portal/exam_list.html",
                  {"exams": defs, "bank_errors": _error_snapshot()})


@require_GET
def exam_detail(request, exam_id: str):
    doc = exam_defs().get(exam_id)
    bp = (doc or {}).get("blueprint") or {}
    if not doc or not bp.get("blocks"):
        raise Http404("Exam not found")
    active = None
    history = []
    if request.user.is_authenticated:
        active = examsys.active_attempt(request.user.username, exam_id)
        history = list(
            ExamAttempt.objects.filter(profile__username=request.user.username,
                                       exam=exam_id)
            .exclude(status="active").order_by("-started_at")[:10]
        )
    return render(request, "portal/exam_detail.html",
                  {"exam": {"id": exam_id, **doc}, "blocks": bp.get("blocks") or [],
                   "active": active, "history": history,
                   "bank_errors": _error_snapshot()})


@login_required
@require_POST
def exam_start(request, exam_id: str):
    if exam_id not in exam_defs():
        raise Http404("Exam not found")
    mode = "diagnostic" if request.POST.get("mode") == "diagnostic" else "real"
    attempt = examsys.start_attempt(request.user.username, exam_id, mode=mode)
    return redirect("exam_take", exam_id=exam_id, attempt_id=attempt.id)


def _owned_attempt(request, exam_id: str, attempt_id: int) -> ExamAttempt:
    attempt = examsys.get_attempt(request.user.username, attempt_id)
    if not attempt or attempt.exam != exam_id:
        raise Http404("Attempt not found")
    return examsys.maybe_finalize(attempt)


def _plan_block(attempt: ExamAttempt, block_id: str) -> dict:
    """A block from the frozen plan, or 404 for unknown ids."""
    for b in attempt.plan.get("blocks") or []:
        if b["id"] == block_id:
            return b
    raise Http404("Block not found")


@require_GET
def exam_take(request, exam_id: str, attempt_id: int):
    if not request.user.is_authenticated:
        return redirect("login")
    attempt = _owned_attempt(request, exam_id, attempt_id)
    if attempt.status != "active":
        return redirect("exam_result", attempt_id=attempt.id)
    block_id = examsys.current_block(attempt)
    if not block_id:
        return redirect("exam_result", attempt_id=attempt.id)
    if not examsys.block_started(attempt, block_id):
        return redirect("exam_break", exam_id=exam_id, attempt_id=attempt.id,
                        block_id=block_id)
    pos = examsys.block_position(attempt, block_id) or 1
    return redirect("exam_question", exam_id=exam_id, attempt_id=attempt.id,
                    block_id=block_id, pos=pos)


@login_required
@require_GET
def exam_question(request, exam_id: str, attempt_id: int,
                  block_id: str, pos: int):
    attempt = _owned_attempt(request, exam_id, attempt_id)
    if attempt.status != "active":
        return redirect("exam_result", attempt_id=attempt.id)
    _plan_block(attempt, block_id)  # 404 on unknown ids before state checks
    if not examsys.block_started(attempt, block_id):
        return redirect("exam_break", exam_id=exam_id, attempt_id=attempt.id,
                        block_id=block_id)
    blocks = attempt.plan.get("blocks") or []
    block = next(b for b in blocks if b["id"] == block_id)
    if not 1 <= pos <= len(block["items"]):
        raise Http404("Question out of range")
    if examsys.remaining_seconds(attempt, block_id) <= 0:
        examsys.maybe_finalize(attempt)
        return redirect("exam_result", attempt_id=attempt.id)

    index = all_bank_items()
    item_id = block["items"][pos - 1]
    item = index.get(item_id)
    if not item:
        raise Http404("Item missing from bank")
    examsys.set_position(attempt, block_id, pos)
    entry = (attempt.answers or {}).get(item_id) or {}

    # retake variant: present the permuted letters; entry.c stores canonical
    shown_choices = item["choices"]
    shown_letter = entry.get("c") or ""
    vmap = (block.get("vmap") or {}).get(item_id) or {}
    if vmap:
        shown_choices = {shown: item["choices"][original]
                         for shown, original in vmap.items()
                         if original in item["choices"]}
        shown_letter = next((shown for shown, original in vmap.items()
                             if original == shown_letter), "")

    return render(request, "portal/exam_take.html", {
        "attempt": attempt,
        "exam": {"id": exam_id},
        "blk": block,
        "block_idx": examsys.block_index(attempt, block_id),
        "num_blocks": len(blocks),
        "pos": pos,
        "total": len(block["items"]),
        "item": {"id": item["id"], "q": item["q"], "choices": shown_choices,
                 "figure": content.figure_url(item.get("figure", "")),
                 "passage_text": item.get("passage_text", ""),
                 "passage_id": item.get("passage_id", "")},
        "chosen": shown_letter,
        # crossed letters are stored as shown letters (vmap is frozen per
        # attempt, so shown letters are stable across re-renders)
        "crossed": entry.get("x") or [],
        "flagged": bool(entry.get("f")),
        "remaining": examsys.remaining_seconds(attempt, block_id),
        "nav": examsys.navigator(attempt, block_id),
        "is_first": pos == 1,
        "is_last": pos == len(block["items"]),
        # the template's Submit-exam branch keys on these; they were never
        # in the context, so the last block rendered the finish form and the
        # submit API was unreachable from the UI
        "is_last_block": examsys.block_index(attempt, block_id) == len(blocks) - 1,
        "break_before": next(
            (b.get("break_before") for b in blocks
             if b["id"] != block_id
             and examsys.block_index(attempt, b["id"])
             == examsys.block_index(attempt, block_id) + 1), None),
        "next_block": (blocks[examsys.block_index(attempt, block_id) + 1]
                       if examsys.block_index(attempt, block_id) + 1 < len(blocks) else None),
    })


@login_required
@require_GET
def exam_break(request, exam_id: str, attempt_id: int, block_id: str):
    attempt = _owned_attempt(request, exam_id, attempt_id)
    if attempt.status != "active":
        return redirect("exam_result", attempt_id=attempt.id)
    # a break page exists only for the NEXT block (previous one just
    # finished, this one not yet begun) — anything else bounces to the take
    # flow so a stale URL can't park a learner on a break for a block that
    # is running or already done
    if (examsys.current_block(attempt) != block_id
            or examsys.block_started(attempt, block_id)):
        return redirect("exam_take", exam_id=exam_id, attempt_id=attempt.id)
    block = _plan_block(attempt, block_id)
    return render(request, "portal/exam_break.html", {
        "attempt": attempt, "exam": {"id": exam_id}, "blk": block,
        "remaining": examsys.remaining_seconds(attempt, block_id),
    })


@login_required
@require_POST
def exam_begin(request, exam_id: str, attempt_id: int, block_id: str):
    attempt = _owned_attempt(request, exam_id, attempt_id)
    if attempt.status != "active":
        return redirect("exam_result", attempt_id=attempt.id)
    _plan_block(attempt, block_id)
    try:
        examsys.begin_block(attempt, block_id)
    except ExamError:
        # sequence violation (e.g. double-POST of an already-begun next block):
        # land wherever the engine says the learner should be
        return redirect("exam_take", exam_id=exam_id, attempt_id=attempt.id)
    return redirect("exam_question", exam_id=exam_id, attempt_id=attempt.id,
                    block_id=block_id, pos=1)


@login_required
@require_POST
def exam_finish_block(request, exam_id: str, attempt_id: int, block_id: str):
    """Close this block's clock and move on. The next block's timer starts
    only when its own Begin is pressed, so breaks stay untimed."""
    attempt = _owned_attempt(request, exam_id, attempt_id)
    if attempt.status != "active":
        return redirect("exam_result", attempt_id=attempt.id)
    _plan_block(attempt, block_id)
    reloaded = None
    try:
        reloaded = examsys.finish_block(attempt, block_id)
    except ExamError:
        pass
    # finish_block may finalize (and returns the reloaded row) — reading the
    # stale in-memory copy here sent the wrong redirect on last-block submits
    if reloaded is not None:
        attempt = reloaded
    if attempt.status != "active":
        return redirect("exam_result", attempt_id=attempt.id)
    nxt = examsys.current_block(attempt)
    if not nxt:
        return redirect("exam_result", attempt_id=attempt.id)
    return redirect("exam_break", exam_id=exam_id, attempt_id=attempt.id,
                    block_id=nxt)


@login_required
@require_POST
def exam_answer_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    try:
        attempt_id = int(payload.get("attempt_id") or 0)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "bad attempt_id"}, status=400)
    attempt = examsys.get_attempt(request.user.username, attempt_id)
    if not attempt:
        return JsonResponse({"ok": False, "error": "unknown attempt"}, status=404)
    block_id = str(payload.get("block_id") or "")
    try:
        pos = int(payload.get("pos") or 0)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "bad pos"}, status=400)
    chosen = payload.get("chosen")
    flagged = bool(payload.get("flagged"))
    crossed = payload.get("crossed")
    if crossed is not None and not isinstance(crossed, list):
        crossed = None
    try:
        elapsed = int(payload.get("elapsed_seconds") or 0)
    except (TypeError, ValueError):
        elapsed = 0
    try:
        result = examsys.save_answer(attempt, block_id, pos, chosen, flagged, elapsed,
                                     crossed=crossed)
    except ExamError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    if result.get("ok"):
        return JsonResponse(result)
    status = 409 if result.get("error") == "expired" else 400
    return JsonResponse(result, status=status)


@login_required
@require_POST
def exam_submit_api(request):
    # JSON from the exam page's fetch(); form-encoded fallback so the noscript
    # submit button still works without JavaScript
    if request.content_type and "json" not in request.content_type:
        try:
            attempt_id = int(request.POST.get("attempt_id") or 0)
        except (TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "bad attempt_id"}, status=400)
    else:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
        try:
            attempt_id = int(payload.get("attempt_id") or 0)
        except (TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "bad attempt_id"}, status=400)
    attempt = examsys.get_attempt(request.user.username, attempt_id)
    if not attempt:
        return JsonResponse({"ok": False, "error": "unknown attempt"}, status=404)
    if attempt.status == "active":
        if examsys.current_block(attempt) is not None:
            # unfinished blocks remain — the exam is not submittable yet
            return JsonResponse({"ok": False, "error": "blocks-remaining",
                                 "next_block": examsys.current_block(attempt)},
                                status=409)
        attempt = examsys.finalize(attempt, reason="submitted")
    return JsonResponse({"ok": True, "attempt_id": attempt.id,
                         "status": attempt.status})


@login_required
@require_GET
def exam_result(request, attempt_id: int):
    attempt = examsys.get_attempt(request.user.username, attempt_id)
    if not attempt:
        raise Http404("Attempt not found")
    attempt = examsys.maybe_finalize(attempt)
    if attempt.status == "active":
        # mid-exam: the answer key must never be reachable
        return redirect("exam_take", exam_id=attempt.exam, attempt_id=attempt.id)
    score = attempt.score or {}

    review = []
    index = all_bank_items()
    chapters_store = content.store()["chapters"]
    difficulty = insights.item_difficulty_map()
    responses = {r.item_id: r for r in attempt.responses.all()}
    for block in attempt.plan.get("blocks") or []:
        for pos, item_id in enumerate(block.get("items") or [], start=1):
            item = index.get(item_id)
            if not item:
                continue
            r = responses.get(item_id)
            entry = (attempt.answers or {}).get(item_id) or {}
            chosen = (r.chosen if r else entry.get("c")) or ""
            # retake variants: show the letter the learner actually clicked,
            # folded back through the attempt's permutation
            vmap = (block.get("vmap") or {}).get(item_id) or {}
            if chosen and vmap and chosen in vmap.values():
                shown = next((s for s, o in vmap.items() if o == chosen), chosen)
            else:
                shown = chosen
            chapter = chapters_store.get(item.get("chapter") or {})
            # retake variants permute shown letters: fold the choice texts
            # through vmap exactly as exam_question does, so the review's
            # highlighted "correct" row matches the letters the learner saw
            shown_choices = item["choices"]
            if vmap:
                shown_choices = {shown: item["choices"][original]
                                 for shown, original in vmap.items()
                                 if original in item["choices"]}
            review.append({
                "choices": shown_choices,
                "pos_global": len(review) + 1,
                "block": block["id"],
                "pos": pos,
                "field_test": item_id in (block.get("field_test") or []),
                "q": item["q"],
                "answer": (next((s for s, o in vmap.items()
                                    if o == item["answer"]), item["answer"])
                             if vmap else item["answer"]),
                "chosen": shown,
                "correct": bool(chosen) and chosen == item["answer"],
                "explain": item.get("explain", ""),
                # retake variants permute shown letters: fold the distractor
                # keys through the same map so each note sits under the
                # option text it explains (was: canonical letters against a
                # permuted choice list)
                "distractors": ({shown: item["distractors"][original]
                                 for shown, original in vmap.items()
                                 if original in (item.get("distractors") or {})}
                                if vmap else item.get("distractors") or {}),
                "passage_text": item.get("passage_text", ""),
                "flagged": bool(entry.get("f")),
                "time_spent": (r.time_spent if r else entry.get("s")) or 0,
                "difficulty": difficulty.get(item_id),
                "skill": item.get("skill") or "",
                "chapter": item.get("chapter") or "",
                "chapter_title": (chapter or {}).get("title", ""),
                "discipline": (chapter or {}).get("discipline", ""),
            })

    # NMAT report vocabulary: per-subtest SS estimates + APT/SA/GPS composites
    # (see examsys.gps_estimate — planning estimates only, CEM equates forms
    # and evaluates on percentile rank).
    report_vocab = None
    if attempt.exam == "nmat":
        report_vocab = examsys.gps_estimate(score)
        if report_vocab:
            for b in score.get("blocks") or []:
                for sub in b.get("subtests") or []:
                    n, correct = sub.get("items") or 0, sub.get("correct") or 0
                    if n <= 0:
                        continue
                    # same accuracy model as the interpreter/gps_estimate
                    z = (correct / n - 0.6) / 0.12
                    sub["ss_est"] = max(200, min(800, round(500 + 100 * z)))
                    sub["pct"] = round(100 * correct / n)

    # MCAT per-skill accuracy (AAMC SIRS): aggregate the review rows by their
    # bank `skill` tag (s1-s4; present on science-bank items once tagged).
    skill_rows: dict[str, dict] = {}
    for r in review:
        sk = r.get("skill") or ""
        if sk in ("s1", "s2", "s3", "s4"):
            slot = skill_rows.setdefault(sk, {"skill": sk, "correct": 0, "items": 0})
            slot["correct"] += 1 if r["correct"] else 0
            slot["items"] += 1

    skill_names = {"s1": "Knowledge of Scientific Concepts",
                   "s2": "Scientific Reasoning and Problem-Solving",
                   "s3": "Reasoning About Design and Execution",
                   "s4": "Data-Based and Statistical Reasoning"}
    skill_accuracy = [
        {"skill": sk, "name": skill_names[sk],
         "pct": round(100 * slot["correct"] / slot["items"])}
        for sk, slot in sorted(skill_rows.items()) if slot["items"] >= 3
    ]

    return render(request, "portal/exam_result.html", {
        "attempt": attempt,
        "score": score,
        "review": review,
        "report_vocab": report_vocab,
        "skill_accuracy": skill_accuracy,
        "exam_name": (exam_defs().get(attempt.exam) or {}).get("name", attempt.exam),
    })


# ---- spaced-repetition flashcards ------------------------------------------

@login_required
@require_GET
def flashcards_export(request):
    """Export the learner's whole SRS deck: CSV (default) or a ready-to-open
    Anki package (.apkg) with ?format=apkg."""
    import csv

    from .models import SrsCard

    def _safe(cell):
        # neutralise spreadsheet formula injection (=, +, -, @ prefixes)
        text = str(cell)
        return "'" + text if text.startswith(("=", "+", "-", "@", "\t", "\r")) else text

    cards = (SrsCard.objects.filter(profile__username=request.user.username)
             .order_by("subject_slug", "chapter", "front"))

    if request.GET.get("format") == "apkg":
        import os
        import tempfile

        import genanki

        model = genanki.Model(
            1607392319,
            "Gabay card",
            fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Source"}],
            templates=[{
                "qfmt": "{{Front}}",
                "afmt": "{{Front}}<hr id=answer>{{Back}}<br><br><small>{{Source}}</small>",
            }])
        import hashlib

        stable = int(hashlib.md5(request.user.username.encode()).hexdigest()[:8], 16)
        deck = genanki.Deck(
            2059400110 + stable % 1000,
            f"Gabay — {request.user.username}")
        for c in cards:
            source = " · ".join(x for x in (c.subject_slug, c.chapter) if x)
            deck.add_note(genanki.Note(
                model=model,
                fields=[c.front, c.back, source],
                tags=[t for t in (c.subject_slug,) if t]))
        fd, apkg_path = tempfile.mkstemp(suffix=".apkg")
        os.close(fd)
        try:
            genanki.Package(deck).write_to_file(apkg_path)
            with open(apkg_path, "rb") as fh:
                payload = fh.read()
        finally:
            os.unlink(apkg_path)
        response = HttpResponse(payload, content_type="application/octet-stream")
        response["Content-Disposition"] = 'attachment; filename="gabay-flashcards.apkg"'
        return response

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="gabay-flashcards.csv"'
    writer = csv.writer(response)
    writer.writerow(["front", "back", "chapter", "subject", "due", "reps", "lapses"])
    for c in cards:
        writer.writerow([_safe(c.front), _safe(c.back), _safe(c.chapter),
                         _safe(c.subject_slug), c.due_date, c.reps, c.lapses])
    return response


@login_required
@require_GET
def flashcards_hub(request):
    from .srs import due_queue, srs_stats, _subjects_with_decks
    from .content import labels

    subject = request.GET.get("subject") or ""
    queue = due_queue(request.user.username, subject or None)
    stats = srs_stats(request.user.username)
    decks = [{"slug": s, "label": labels().get(s, s)} for s in _subjects_with_decks()]
    return render(request, "portal/flashcards.html", {
        "decks": decks, "active_subject": subject,
        "due": queue["due"], "new_cards": queue["new"],
        "stats": stats,
    })


@login_required
@require_POST
def flashcard_grade_api(request):
    import json as _json

    from .srs import card_key, deck_for, grade_card
    try:
        payload = _json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    subject_slug = str(payload.get("subject_slug") or "").strip()[:80]
    grade = str(payload.get("grade") or "").strip().lower()
    if grade not in ("again", "hard", "good", "easy"):
        return JsonResponse({"ok": False, "error": "bad grade"}, status=400)
    # card identity is verified against the content deck — the client never
    # dictates front/back text. Learner-created miss cards (exam:* keys,
    # error-correction fronts) have no deck entry; they verify against the
    # learner's OWN SrsCard row instead.
    key = str(payload.get("key") or "").strip()[:64]
    card = next((c for c in deck_for(subject_slug) if c["key"] == key), None)
    if card:
        front, back, chapter = card["front"], card["back"], card["chapter"]
    else:
        from .models import SrsCard as _Card

        row = _Card.objects.filter(
            profile__username=request.user.username, card_key=key).first()
        if not row:
            return JsonResponse({"ok": False, "error": "Unknown card"}, status=404)
        front, back, chapter = row.front, row.back, row.chapter
    return JsonResponse(grade_card(
        request.user.username, subject_slug, key,
        front, back, chapter, grade))
