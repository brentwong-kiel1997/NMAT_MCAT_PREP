"""AI-generated practice sets ("AI drill") for weak chapters and misses.

Two modes:
  chapter — grounded in a chapter's notes/points + tutorial key points/pitfalls
  misses  — grounded in the learner's OWN wrong items (stems, correct answers,
            explanations, and the option they picked)

Hard contract for generated content:
  - 3-5 items, exactly A-D choices, unique texts, answer inside choices
  - validated server-side (with one error-feedback retry); invalid output
    never reaches a learner
  - stored in AiQuiz and clearly labelled AI-generated; judged client-side
    and NEVER fed into official accuracy statistics
Budget: each generation spends one coach-budget call and is additionally
capped at 10 generations/day (portal.ratelimit).
"""

from __future__ import annotations

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from . import insights
from .models import AiQuiz
from .ratelimit import hit

_MAX_SETS_PER_DAY = 10
_QUESTIONS_WANTED = 4


def _chapter_grounding(chapter_id: str) -> tuple[str, str]:
    """(chapter title, grounding prose) for a library chapter."""
    from .content import chapters_store, tutorial_for

    ch = chapters_store().get(chapter_id) or {}
    title = ch.get("title") or chapter_id
    tut = tutorial_for(ch.get("discipline", ""), ch.get("title", "")) or {}
    parts = [
        # truncate the JOINED string — [:500] on the list capped elements,
        # not characters, leaving the budget unbounded as content grows
        "Chapter points: " + ("; ".join(ch.get("points") or []))[:500],
        "Key points: " + ("; ".join(tut.get("key_points") or []))[:500],
        "Recorded pitfalls: " + ("; ".join(tut.get("pitfalls") or []))[:400],
    ]
    return title, "\n".join(parts)


def _miss_grounding(username: str, chapter_id: str | None) -> tuple[str, str]:
    """(scope title, grounding prose) from the learner's own wrong items."""
    from .learners import get_or_create_profile
    from .content import all_bank_items

    profile = get_or_create_profile(username)
    wrong = insights.wrong_questions(profile, limit=30)
    if chapter_id:
        wrong = [w for w in wrong if w.get("chapter_id") == chapter_id]
    bank = all_bank_items()
    practice_store = {}
    from .content import store

    for ch in store()["chapters"].values():
        for q in ch.get("practice") or []:
            practice_store[q.get("id")] = q
    lines = []
    for w in wrong[:6]:
        q = bank.get(w["question_id"]) or practice_store.get(w["question_id"]) or {}
        if not q:
            continue
        lines.append(
            f"- Stem: {q.get('q', '')[:220]} | correct: {q.get('answer')} "
            f"({str(q.get('explain', ''))[:160]}) | learner picked: {w.get('chosen')}"
        )
    if not lines:
        return "", ""
    title = (f"{chapter_id} misses" if chapter_id
             else f"{len(lines)} recent misses across chapters")
    return title, "The learner recently missed:\n" + "\n".join(lines)


def _build_prompt(mode: str, grounding_title: str, grounding: str,
                  difficulty: str) -> str:
    difficulty_line = {
        "easy": "Difficulty: EASY — single-step recall, obvious distractors.",
        "challenge": ("Difficulty: CHALLENGE — multi-step reasoning, distractors "
                      "built from subtle misconceptions."),
    }.get(difficulty, "Difficulty: STANDARD — exam-typical single best answer.")
    return (
        "You are an NMAT/MCAT item writer for the Gabay prep platform. Write "
        f"{_QUESTIONS_WANTED} NEW multiple-choice practice questions grounded "
        "ONLY in the source material below"
        + (" and the learner's own misses (same skill, fresh numbers/context — "
           "never copy the missed stems)" if mode == "misses" else "")
        + ". Match official style: single best answer, plausible distractors "
        "that each encode one specific error. " + difficulty_line + "\n\n"
        "Return STRICT JSON only — no markdown fences, no commentary:\n"
        '{"questions": [{"q": "stem", "choices": {"A": "...", "B": "...", '
        '"C": "...", "D": "..."}, "answer": "B", "explain": "why B is right '
        'and what each distractor mistakes"}]}\n\n'
        f"Source material — {grounding_title}:\n{grounding}"
    )


def _extract_json(text: str) -> dict:
    """Parse the model's JSON out of a possibly fenced/commented reply."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found in model reply")
    return json.loads(text[start:end + 1])


def validate_questions(questions, max_items: int = 5) -> list[dict]:
    """Structural validation; raises ValueError describing every problem.
    Tolerates a model returning non-objects or unhashable choice values."""
    problems: list[str] = []
    clean: list[dict] = []
    if not isinstance(questions, list) or not questions:
        raise ValueError("model returned no questions array")
    seen_stems: set[str] = set()
    for n, q in enumerate(questions[:max_items], 1):
        if not isinstance(q, dict):
            problems.append(f"item {n}: not an object")
            continue
        stem = str(q.get("q") or "").strip()[:2000]
        choices_raw = q.get("choices")
        if not isinstance(choices_raw, dict):
            problems.append(f"q{n}: choices not an object")
            continue
        choices = {str(k).strip().upper()[:1]: str(v).strip()[:2000]
                   for k, v in choices_raw.items()}
        answer = str(q.get("answer") or "").strip().upper()[:1]
        explain = str(q.get("explain") or "").strip()[:2000]
        if not stem:
            problems.append(f"q{n}: empty stem")
            continue
        if stem[:80].lower() in seen_stems:
            problems.append(f"q{n}: duplicate stem")
            continue
        seen_stems.add(stem[:80].lower())
        if set(choices) != {"A", "B", "C", "D"}:
            problems.append(f"q{n}: choices not exactly A-D")
            continue
        if len(set(choices.values())) != 4:
            problems.append(f"q{n}: duplicate option texts")
            continue
        if answer not in choices:
            problems.append(f"q{n}: answer {answer!r} not in choices")
            continue
        if not explain:
            problems.append(f"q{n}: missing explanation")
            continue
        clean.append({"q": stem, "choices": choices, "answer": answer,
                      "explain": explain})
    if len(clean) < 3:
        raise ValueError("; ".join(problems) or "fewer than 3 valid questions")
    return clean


def generate_quiz(username: str, mode: str, chapter_id: str | None,
                  difficulty: str = "standard") -> AiQuiz:
    """Generate (with one error-feedback retry), validate, persist, return.
    All failure paths raise RuntimeError — the view renders them as messages."""
    from django.conf import settings

    from .learners import get_or_create_profile
    from .llm import chat_completion, coach_ready

    # cheap, side-effect-free checks FIRST — the budget counters must not burn
    # quota for a request that can never reach the model
    if not coach_ready():
        raise RuntimeError("No AI model is configured — ask an admin to add one.")
    if mode == "misses":
        title, grounding = _miss_grounding(username, chapter_id or None)
        if not grounding:
            raise RuntimeError("No recorded misses to build variants from yet.")
    else:
        mode = "chapter"
        title, grounding = _chapter_grounding(chapter_id or "")
        if not grounding.strip():
            raise RuntimeError("Unknown chapter — pick one from the list.")

    if not hit(f"aidrill:{username}:{timezone.localdate()}",
               _MAX_SETS_PER_DAY, 86400):
        raise RuntimeError("Daily AI-drill limit reached (10 sets) — back tomorrow.")
    if not hit(f"coach:{username}:{timezone.localdate()}",
               settings.GABAY_COACH_DAILY_LIMIT, 86400):
        raise RuntimeError("Daily coach limit reached — the AI drill is back tomorrow.")

    prompt = _build_prompt(mode, title, grounding, difficulty)
    questions = None
    last_error: Exception | None = None
    # two passes total: fresh attempt, then one repair pass that shows the
    # model its mistake. ANY validation failure raises RuntimeError so the
    # view degrades gracefully (a ValueError here used to 500 the route).
    for temperature in (0.5, 0.2):
        try:
            raw = chat_completion([{"role": "user", "content": prompt}],
                                  max_tokens=1600, temperature=temperature)
            questions = validate_questions(_extract_json(raw).get("questions"))
            break
        except (ValueError, TypeError, AttributeError, KeyError,
                json.JSONDecodeError) as exc:
            last_error = exc
            prompt = (f"{prompt}\n\nYour previous reply was rejected: {exc}. "
                      "Return the corrected STRICT JSON now.")
    if questions is None:
        raise RuntimeError(
            "The model's replies were malformed twice — please try again "
            f"later. (Last error: {last_error})")

    for n, q in enumerate(questions, 1):
        q["id"] = f"ai-{n}"
        q["chapter"] = title
        q["difficulty"] = difficulty
    return AiQuiz.objects.create(
        profile=get_or_create_profile(username),
        chapter_id=chapter_id or "", mode=mode, payload=questions,
    )


# ---- views -------------------------------------------------------------------

@login_required
@require_GET
def ai_drill_index(request):
    from .insights import wrong_chapters
    from .learners import get_or_create_profile

    profile = get_or_create_profile(request.user.username)
    weak = wrong_chapters(profile, limit=8)
    recent = AiQuiz.objects.filter(profile=profile)[:8]
    return render(request, "portal/ai_drill.html", {
        "weak": weak,
        "recent": recent,
        "max_sets": _MAX_SETS_PER_DAY,
    })


@login_required
@require_POST
def ai_drill_generate(request):
    from .content import chapters_store

    mode = "misses" if request.POST.get("mode") == "misses" else "chapter"
    chapter_id = str(request.POST.get("chapter_id") or "").strip()[:120]
    difficulty = request.POST.get("difficulty") or "standard"
    if difficulty not in ("easy", "standard", "challenge"):
        difficulty = "standard"
    if mode == "chapter" and chapter_id not in chapters_store():
        messages.error(request, "Pick a chapter from the list.")
        return redirect("ai_drill_index")
    try:
        quiz = generate_quiz(request.user.username, mode, chapter_id or None,
                             difficulty=difficulty)
    except RuntimeError as exc:
        messages.error(request, f"AI drill: {exc}")
        return redirect("ai_drill_index")
    messages.success(request, "AI quiz generated — not counted in official stats.")
    return redirect("ai_drill_quiz", quiz_id=quiz.id)


@login_required
@require_GET
def ai_drill_quiz(request, quiz_id: int):
    from .learners import get_or_create_profile
    from .views import _json_for_script

    profile = get_or_create_profile(request.user.username)
    quiz = get_object_or_404(AiQuiz, pk=quiz_id, profile=profile)
    items_json = _json_for_script(quiz.payload)
    return render(request, "portal/ai_quiz.html", {
        "quiz": quiz,
        "items_json": items_json,
        "total": len(quiz.payload),
    })


@login_required
@require_POST
def ai_drill_report(request, quiz_id: int):
    from .learners import get_or_create_profile

    profile = get_or_create_profile(request.user.username)
    quiz = get_object_or_404(AiQuiz, pk=quiz_id, profile=profile)
    AiQuiz.objects.filter(pk=quiz.pk).update(bad_reports=F("bad_reports") + 1)
    messages.success(
        request,
        "Thanks — reported. AI items stay out of official statistics; reports "
        "flag low-quality sets for review.",
    )
    return redirect("ai_drill_quiz", quiz_id=quiz.id)
