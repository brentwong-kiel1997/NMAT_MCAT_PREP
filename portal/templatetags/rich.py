"""Tiny inline-rich-text filter for tutorial prose.

Escapes everything first, then maps two markers to HTML:
  **bold**   → <strong>   (key terms)
  ==mark==   → <mark>     (must-not-miss exam takeaways)
No other syntax is recognized; content stays plain-text authored.
"""

from __future__ import annotations

import re
from html import escape

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_MARK = re.compile(r"==(.+?)==", re.DOTALL)


@register.filter
def rich(value) -> str:
    text = escape(str(value))
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _MARK.sub(r"<mark>\1</mark>", text)
    return mark_safe(text)
