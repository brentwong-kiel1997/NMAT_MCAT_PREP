"""Programmatic SVG generators for NMAT Part-1 figure items.

Every figure is original geometric art we generate from parameters — the
same parameters that define the question and its options, so figure and
key can never disagree. Output: content/images/items/<key>.svg
"""

from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "content" / "images" / "items"

ARROW = 'marker-end="url(#arr)"'
DEFS = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs>')


def _wrap(body: str, w: int = 300, h: int = 300) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">{DEFS}'
            f'<rect width="{w}" height="{h}" fill="#fafafa"/>{body}</svg>')


# ---------- mirror image (vertical axis flip of a letter-like glyph) ------
def mirror_letter(letter: str) -> str:
    """Render `letter` and its vertical mirror side by side."""
    glyphs = {"b": "d", "d": "b", "p": "q", "q": "p"}
    flipped = glyphs.get(letter.lower(), letter.upper())
    body = (f'<text x="90" y="190" font-size="120" font-family="serif" '
            f'text-anchor="middle">{letter}</text>'
            f'<line x1="150" y1="20" x2="150" y2="280" stroke="#3b5bdb" '
            f'stroke-dasharray="6 4"/>'
            f'<text x="210" y="190" font-size="120" font-family="serif" '
            f'text-anchor="middle" fill="#3b5bdb">{flipped}</text>')
    return _wrap(body)


# ---------- rotation series frame -----------------------------------------
def rot_frame(quarter_turns: int, shape: str = "arrow") -> str:
    """One frame of a rotation series: `shape` turned `quarter_turns` x 90° cw."""
    ang = quarter_turns * 90
    if shape == "arrow":
        body = (f'<g transform="rotate({ang} 150 150)">'
                f'<line x1="60" y1="150" x2="230" y2="150" stroke="#333" '
                f'stroke-width="5" {ARROW}/></g>')
    elif shape == "flag":  # L-with-dot style composite
        body = (f'<g transform="rotate({ang} 150 150)">'
                f'<path d="M120 60 h30 v150 h-30 z" fill="#3b5bdb"/>'
                f'<path d="M150 60 h60 v30 h-60 z" fill="#c77800"/></g>')
    else:  # triangle pointer
        pts = "150,70 220,210 80,210"
        body = (f'<g transform="rotate({ang} 150 150)">'
                f'<polygon points="{pts}" fill="none" stroke="#333" stroke-width="4"/></g>')
    return _wrap(f'<circle cx="150" cy="150" r="120" fill="none" '
                 f'stroke="#ddd"/>{body}')


# ---------- hidden figure (target inside clutter) -------------------------
def hidden_figure(target: str = "square") -> str:
    clutter = ('<line x1="20" y1="30" x2="280" y2="90" stroke="#bbb"/>'
               '<line x1="30" y1="270" x2="270" y2="200" stroke="#bbb"/>'
               '<line x1="150" y1="10" x2="150" y2="290" stroke="#bbb"/>'
               '<line x1="10" y1="150" x2="290" y2="150" stroke="#bbb"/>'
               '<line x1="60" y1="20" x2="240" y2="280" stroke="#ccc"/>')
    if target == "square":
        tgt = ('<rect x="90" y="90" width="120" height="120" fill="none" '
               'stroke="#b00020" stroke-width="4"/>')
    elif target == "triangle":
        tgt = ('<polygon points="150,50 230,240 70,240" fill="none" '
               'stroke="#b00020" stroke-width="4"/>')
    else:  # T
        tgt = ('<path d="M70 60 h160 M150 60 v180" fill="none" '
               'stroke="#b00020" stroke-width="5"/>')
    return _wrap(clutter + tgt)


# ---------- figure grouping cell ------------------------------------------
def group_cell(shape: str, filled: bool) -> str:
    if shape == "circle":
        base = '<circle cx="150" cy="150" r="90" '
    elif shape == "square":
        base = '<rect x="65" y="65" width="170" height="170" '
    else:
        base = '<polygon points="150,50 245,215 55,215" '
    style = ('fill="#333"' if filled else 'fill="none" stroke="#333" stroke-width="4"')
    return _wrap(f'<{base} {style}/>')


# ---------- sequence frame (dots/shading progression) ---------------------
def seq_frame(dots: int, shaded: bool, rot: int = 0) -> str:
    parts = [f'<rect x="40" y="40" width="220" height="220" fill="none" '
             f'stroke="#333" stroke-width="3" transform="rotate({rot} 150 150)"/>']
    for k in range(dots):
        ang = math.radians(rot + k * (360 / max(dots, 1)))
        cx = 150 + 80 * math.cos(ang)
        cy = 150 + 80 * math.sin(ang)
        fill = "#333" if shaded else "none"
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="14" fill="{fill}" '
                     f'stroke="#333" stroke-width="3"/>')
    return _wrap("".join(parts))


# ---------- writer ---------------------------------------------------------
def write(key: str, svg: str) -> str:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{key}.svg"
    path.write_text(svg, encoding="utf-8")
    rel = f"items/{key}.svg"
    return rel
