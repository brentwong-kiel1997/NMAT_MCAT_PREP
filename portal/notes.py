"""Chapter note accessors, backed by the content/ YAML reader (portal.content)."""

from __future__ import annotations

from . import content

# kept under its historical private name for straggler callers
_chapter_id = content._chapter_id


def notes_for(slug: str, chapter_title: str) -> list[dict[str, str]]:
    return content.notes_for(slug, chapter_title)


def attach_notes(subject: dict) -> dict:
    return content.attach_notes(subject)


def flashcards_for(slug: str, limit: int = 40) -> list[dict]:
    return content.flashcards_for(slug, limit)
