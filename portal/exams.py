"""Exam hub and subject accessors, backed by the content/ YAML reader.

Content lives in content/exams/*.yml and content/subjects/*.yml; see
portal/content.py for the schema and caching.
"""

from __future__ import annotations

from .content import (
    get_mcat_section,
    get_nmat_unique,
    get_shared,
    mcat_exam,
    nmat_exam,
    nmat_unique_subjects,
    shared_list,
)

__all__ = [
    "get_mcat_section",
    "get_nmat_unique",
    "get_shared",
    "mcat_exam",
    "nmat_exam",
    "nmat_unique_subjects",
    "shared_list",
]
