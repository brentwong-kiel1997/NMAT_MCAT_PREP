"""Curriculum-aware study helpers for the Gabay tutor."""

from __future__ import annotations

from . import exams


def build_curriculum_context(
    *,
    exam: str = "",
    subject_slug: str = "",
    section_slug: str = "",
    chapter_title: str = "",
) -> str:
    """Return a compact curriculum brief the model must stay inside."""
    chunks: list[str] = []
    exam = (exam or "").upper().strip()
    subject_slug = (subject_slug or "").strip()
    section_slug = (section_slug or "").strip()
    chapter_title = (chapter_title or "").strip()

    shared = exams.get_shared(subject_slug) if subject_slug else None
    unique = exams.get_nmat_unique(subject_slug) if subject_slug else None
    section = exams.get_mcat_section(section_slug) if section_slug else None

    def outline(entity: dict, header: str) -> None:
        chunks.append(header)
        for group in entity.get("chapters", []):
            chunks.append(f"[{group['heading']}]")
            for item in group["items"]:
                mark = "  <- current chapter" if chapter_title and chapter_title == item["title"] else ""
                points = "; ".join(item.get("points") or [])
                chunks.append(f"- {item['title']}{mark}: {points}")

    if shared:
        outline(shared, f"Shared subject: {shared['name']}")
        chunks.insert(1, f"Positioning: {shared.get('summary', '')}")
    if unique:
        outline(unique, f"NMAT Part 1 subject: {unique['name']}")
        chunks.insert(1, f"Positioning: {unique.get('focus', '')}")
    if section:
        outline(
            section,
            f"MCAT section: {section.get('short', section['name'])} — {section['name']}",
        )
        chunks.insert(1, f"Positioning: {section.get('focus', '')}")

    if not chunks:
        chunks.append(
            "General NMAT / MCAT coaching. Prefer the subjects and chapters "
            "listed on the Gabay site."
        )

    return "\n".join(chunks)


SYSTEM_PROMPT = """You are the Gabay study coach. The user is preparing for both the
Philippine NMAT (CEM) and the US MCAT (AAMC).
Rules:
1. Answer strictly within the user's current subject/chapter outline; if a question is
   outside it, say so explicitly and map it back to the nearest official chapter.
2. Distinguish the exams: NMAT Part 2 is introductory-college depth; the MCAT is
   passage-based reasoning over foundational science. Do not treat guideline-level
   clinical detail as NMAT testable material.
3. Explain intuition first, then mechanism, then common pitfalls. Use standard
   technical terms.
4. When quizzing, ask exactly one question at a time and wait for the answer; grade
   and explain only after the user responds.
5. Never invent "official" CEM/AAMC percentages or fake topics; say when unsure.
6. Keep answers concise and actionable, suitable for reading between drills."""


def tutor_messages(
    *,
    mode: str,
    user_text: str,
    curriculum: str,
    chapter_title: str = "",
) -> list[dict]:
    mode = (mode or "ask").lower()
    chapter_line = (
        f"Current chapter: {chapter_title}"
        if chapter_title
        else "Current chapter: none specified (coach the whole subject)"
    )

    if mode == "explain":
        task = (
            "Explain the current chapter: 3–5 core concepts first, then one mini "
            "example, then 2 common pitfalls. Do not quiz."
        )
    elif mode == "quiz":
        task = (
            "Write one single-best-answer multiple-choice question (A–D) that fits "
            "the current chapter. Output only the stem, the four options, and a "
            "final line reading 'Choose A/B/C/D'. Do not reveal the answer in the "
            "same message."
        )
    elif mode == "grade":
        task = (
            "The user is answering the previous practice question. Judge correct or "
            "incorrect, give the right option with a short explanation, and point to "
            "the outline concept it maps to."
        )
    else:
        task = "Answer the user's question about the current subject/chapter, with analogies where they help."

    user_payload = (
        f"{chapter_line}\n\n"
        f"[Gabay outline]\n{curriculum}\n\n"
        f"[Task]\n{task}\n\n"
        f"[User input]\n{user_text.strip() or '(none)'}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_payload},
    ]
