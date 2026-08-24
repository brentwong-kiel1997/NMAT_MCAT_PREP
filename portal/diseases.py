"""Disease library accessors, backed by the content/ YAML reader."""

from __future__ import annotations

from .content import all_diseases, get_disease

__all__ = ["all_diseases", "get_disease"]
