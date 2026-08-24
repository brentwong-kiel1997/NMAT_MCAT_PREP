"""Practice MCQ accessors, backed by the content/ YAML reader."""

from __future__ import annotations

from . import content
from .content import all_practice_slugs, practice_catalog, practice_for

# Subject display labels from content/catalog.yml. Bound at import time;
# deploys restart Gunicorn, so edits land with the next deploy.
LABELS = content.labels()

__all__ = ["LABELS", "all_practice_slugs", "practice_catalog", "practice_for"]
