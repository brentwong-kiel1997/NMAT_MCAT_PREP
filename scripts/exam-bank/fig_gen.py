"""Programmatic SVG generators for NMAT Part-1 figure items.

Every figure is original geometric art we generate from parameters — the
same parameters that define the question and its options, so figure and
key can never disagree. Output: content/images/items/<key>.svg
"""

from __future__ import annotations

import math
from pathlib import Path

# this file lives at <repo>/scripts/exam-bank/fig_gen.py, so the repo root is
# three levels up — the art must land in <repo>/content/images/items/
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "content" / "images" / "items"

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
    # base already opens the element ("<circle …") — no extra "<" here, which
    # used to emit invalid `<<circle …/>` markup
    return _wrap(f'{base} {style}/>')


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


# ---------- MCAT science-figure primitives --------------------------------
# Same house style as the Part-1 art: #333 ink on #fafafa, generated from the
# same numbers that appear in the stem so figure and key cannot disagree.
INK = "#333"
FAINT = "#bbb"


def _esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _txt(x, y, s, size=11, anchor="middle", fill=INK, bold=False, rotate=None) -> str:
    tr = f' transform="rotate({rotate} {x:.0f} {y:.0f})"' if rotate is not None else ""
    weight = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-family="sans-serif" '
            f'fill="{fill}" text-anchor="{anchor}"{weight}{tr}>{_esc(s)}</text>')


def _line(x1, y1, x2, y2, color=INK, width=2, dash=None, arrow=False) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    a = f" {ARROW}" if arrow else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{width}"{d}{a}/>')


def _mpoly(pts, color=INK, width=2.5, dash=None) -> str:
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dd}/>'


def _dot(x, y, r=3.5, color=INK) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"/>'


def _axes(x0, y0, x1, y1, xticks=(), yticks=(), xlabel="", ylabel="", size=10) -> str:
    """Bare axes with arrow heads. (x0, y0) is the origin; ticks are
    (pixel, label) pairs."""
    parts = [_line(x0, y0, x1 + 10, y0, arrow=True, width=2),
             _line(x0, y0, x0, y1 - 10, arrow=True, width=2)]
    for px, label in xticks:
        parts.append(_line(px, y0, px, y0 + 4, width=1.5))
        parts.append(_txt(px, y0 + 15, label, size=size))
    for py, label in yticks:
        parts.append(_line(x0, py, x0 - 4, py, width=1.5))
        parts.append(_txt(x0 - 7, py + 3, label, size=size, anchor="end"))
    if xlabel:
        parts.append(_txt((x0 + x1) / 2, y0 + 36, xlabel, size=11))
    if ylabel:
        parts.append(_txt(x0 - 36, (y0 + y1) / 2, ylabel, size=11, rotate=-90))
    return "".join(parts)


def _resistor_h(x1, x2, y, n=6, amp=8) -> str:
    step = (x2 - x1) / n
    pts = [(x1, y)]
    for i in range(n):
        pts.append((x1 + step * (i + 0.5), y - amp if i % 2 == 0 else y + amp))
    pts.append((x2, y))
    return _mpoly(pts, width=2.5)


def _resistor_v(y1, y2, x, n=6, amp=8) -> str:
    step = (y2 - y1) / n
    pts = [(x, y1)]
    for i in range(n):
        pts.append((x - amp if i % 2 == 0 else x + amp, y1 + step * (i + 0.5)))
    pts.append((x, y2))
    return _mpoly(pts, width=2.5)


# ---------- chem-phys: series/parallel circuit ----------------------------
def cp_circuit() -> str:
    """12 V battery, 4.0 Ohm in series with the 6.0 Ohm || 3.0 Ohm pair."""
    top, bottom, left = 60, 205, 70
    node_a, node_b = 95, 168
    br1, br2 = 295, 375
    body = []
    # left wire with the battery
    body.append(_line(left, top, left, 118))
    body.append(_line(54, 118, 86, 118, width=3))          # long plate (+)
    body.append(_line(62, 133, 78, 133, width=5))          # short plate (-)
    body.append(_line(left, 133, left, bottom))
    body.append(_txt(46, 130, "12 V", size=12, anchor="end", bold=True))
    # top wire with the series resistor
    body.append(_line(left, top, 165, top))
    body.append(_resistor_h(165, 245, top))
    body.append(_line(245, top, br2, top))
    body.append(_txt(205, 44, "4.0 Ω", size=12, bold=True))
    body.append(_line(120, top - 12, 152, top - 12, arrow=True, width=1.8))
    body.append(_txt(110, top - 8, "I", size=12, bold=True))
    # bottom wire
    body.append(_line(br2, bottom, left, bottom))
    # parallel section
    body.append(_line(br1, node_a, br2, node_a))
    body.append(_line(br1, node_b, br2, node_b))
    body.append(_line(br2, top, br2, node_a))
    body.append(_line(br2, node_b, br2, bottom))
    body.append(_dot(br2, node_a))
    body.append(_dot(br2, node_b))
    body.append(_line(br1, node_a, br1, 118))
    body.append(_resistor_v(118, 145, br1))
    body.append(_line(br1, 145, br1, node_b))
    body.append(_txt(br1 - 16, 136, "6.0 Ω", size=12, anchor="end", bold=True))
    body.append(_line(br2, node_a, br2, 118))
    body.append(_resistor_v(118, 145, br2))
    body.append(_line(br2, 145, br2, node_b))
    body.append(_txt(br2 + 10, 136, "3.0 Ω", size=12, anchor="start", bold=True))
    return _wrap("".join(body), w=440, h=260)


# ---------- chem-phys: Lineweaver-Burk plots ------------------------------
def _lb_axes(y_max: float, ytick_vals) -> str:
    x0, y0, x1, y1 = 90, 212, 385, 30
    # pixel mapping: 1/[S] in -3..6 mM^-1, 1/v in 0..y_max
    def xp(v):
        return x0 + (v + 3) * (x1 - x0) / 9.0

    def yp(v):
        return y0 - v / y_max * (y0 - y1)

    xticks = [(xp(-2), "-2"), (xp(0), "0"), (xp(2), "2"), (xp(4), "4"), (xp(6), "6")]
    yticks = [(yp(v), f"{v:.3f}") for v in ytick_vals]
    frame = _axes(x0, y0, x1, y1, xticks=xticks, yticks=yticks, size=9,
                  xlabel="", ylabel="1/v")
    return frame, xp, yp


def cp_lb_plot() -> str:
    """Uninhibited double-reciprocal line: intercepts 0.025 and -2.0."""
    y_max = 0.11
    frame, xp, yp = _lb_axes(y_max, (0.025, 0.05, 0.075, 0.1))
    body = [frame]
    slope = 0.0125
    body.append(_line(xp(-2), yp(0), xp(6), yp(slope * 6 + 0.025), width=3))
    body.append(_dot(xp(-2), yp(0)))
    body.append(_dot(xp(0), yp(0.025)))
    body.append(_txt(196, yp(0.025) - 10, "y-intercept = 1/Vmax = 0.025",
                     size=10, anchor="start"))
    body.append(_txt(xp(-2) - 18, yp(0) + 32, "x-intercept = −1/Km = −2.0",
                     size=10, anchor="start"))
    body.append(_txt(266, 118, "slope = Km/Vmax", size=10, rotate=-32))
    body.append(_txt(385 + 12, yp(0) + 36, "1/[S] (1/mM)", size=11, anchor="end"))
    return _wrap("".join(body), w=420, h=260)


def cp_lb_inhibitor() -> str:
    """Competitive inhibitor: same y-intercept, doubled slope."""
    y_max = 0.19
    frame, xp, yp = _lb_axes(y_max, (0.025, 0.05, 0.1, 0.15))
    body = [frame]
    body.append(_line(xp(-2), yp(0), xp(6), yp(0.0125 * 6 + 0.025), width=3))
    body.append(_line(xp(-1), yp(0), xp(6), yp(0.025 * 6 + 0.025), width=3, dash="7 4"))
    body.append(_dot(xp(0), yp(0.025)))
    body.append(_txt(306, 166, "no inhibitor", size=10, anchor="start"))
    body.append(_txt(196, 60, "+ competitive inhibitor", size=10, anchor="start"))
    body.append(_txt(200, 198, "same 1/Vmax", size=10, anchor="start"))
    body.append(_line(xp(-1), yp(0), xp(-1), yp(0) + 4, width=1.5))
    body.append(_txt(xp(-1), yp(0) + 15, "-1", size=9))
    return _wrap("".join(body), w=420, h=260)


# ---------- chem-phys: weak-acid titration curve --------------------------
def cp_titration() -> str:
    """0.100 M NaOH into 20.0 mL of 0.100 M acetic acid (pKa 4.76)."""
    x0, y0, x1, y1 = 70, 212, 385, 28
    points = [(0, 2.87), (5, 4.28), (10, 4.76), (15, 5.24), (18, 5.86), (19, 6.30),
              (19.9, 7.30), (20, 8.70), (21, 11.39), (22, 11.69), (25, 12.05), (30, 12.30)]

    def xp(v):
        return x0 + v / 30.0 * (x1 - x0)

    def yp(ph):
        return y0 - ph / 14.0 * (y0 - y1)

    ticks = [(xp(v), str(v)) for v in (0, 10, 20, 30)]
    yticks = [(yp(v), str(v)) for v in (2, 4, 6, 8, 10, 12)]
    body = [_axes(x0, y0, x1, y1, xticks=ticks, yticks=yticks,
                  xlabel="mL of 0.100 M NaOH added", ylabel="pH")]
    body.append(_mpoly([(xp(v), yp(p)) for v, p in points], width=3))
    # half-equivalence
    body.append(_line(xp(10), y0, xp(10), yp(4.76), dash="4 3", width=1.2, color=FAINT))
    body.append(_line(x0, yp(4.76), xp(10), yp(4.76), dash="4 3", width=1.2, color=FAINT))
    body.append(_dot(xp(10), yp(4.76)))
    body.append(_txt(xp(10) + 10, yp(3.4), "half-equivalence: pH = pKa = 4.76",
                     size=10, anchor="start"))
    # equivalence
    body.append(_line(xp(20), y0, xp(20), yp(8.7), dash="4 3", width=1.2, color=FAINT))
    body.append(_line(x0, yp(8.7), xp(20), yp(8.7), dash="4 3", width=1.2, color=FAINT))
    body.append(_dot(xp(20), yp(8.7)))
    body.append(_txt(xp(20) - 12, yp(8.7) - 26, "equivalence: 20.0 mL, pH 8.7",
                     size=10, anchor="end"))
    return _wrap("".join(body), w=420, h=260)


# ---------- chem-phys: projectile velocity components ---------------------
def cp_velocity_time() -> str:
    """Horizontal launch at 15.0 m/s from 20.0 m: vx constant, vy = g t."""
    x0, y0, x1, y1 = 70, 212, 385, 28
    t_flight = 2.02

    def xp(t):
        return x0 + t / 2.5 * (x1 - x0)

    def yp(v):
        return y0 - v / 25.0 * (y0 - y1)

    ticks = [(xp(v), f"{v:.1f}") for v in (0.5, 1.0, 1.5, 2.0)]
    yticks = [(yp(v), str(v)) for v in (5, 10, 15, 20)]
    body = [_axes(x0, y0, x1, y1, xticks=ticks, yticks=yticks,
                  xlabel="time (s)", ylabel="velocity (m/s)")]
    body.append(_line(xp(0), yp(15), xp(t_flight), yp(15), width=3))
    body.append(_mpoly([(xp(t), yp(9.8 * t)) for t in (0, 0.5, 1.0, 1.5, t_flight)], width=3))
    body.append(_txt(xp(0.08), yp(15) - 24, "vx = 15.0 m/s", size=10, anchor="start"))
    body.append(_txt(xp(0.08), yp(15) - 12, "(constant)", size=10, anchor="start"))
    body.append(_txt(150, 178, "vy = g·t", size=10, rotate=-35))
    body.append(_line(xp(t_flight), y0, xp(t_flight), yp(19.8), dash="4 3", width=1.2, color=FAINT))
    body.append(_dot(xp(t_flight), yp(19.8)))
    body.append(_txt(xp(t_flight) - 8, yp(19.8) - 6, "v_y = 19.8 m/s", size=10, anchor="end"))
    body.append(_txt(xp(t_flight), y0 + 15, "2.02", size=10))
    return _wrap("".join(body), w=420, h=260)


# ---------- bio: pedigree -------------------------------------------------
def _ped_symbol(kind: str, cx: int, cy: int, affected: bool) -> str:
    fill = INK if affected else "#fff"
    if kind == "square":
        base = (f'<rect x="{cx - 14}" y="{cy - 14}" width="28" height="28" fill="{fill}" '
                f'stroke="{INK}" stroke-width="2.5"/>')
    else:
        base = (f'<circle cx="{cx}" cy="{cy}" r="14" fill="{fill}" stroke="{INK}" '
                f'stroke-width="2.5"/>')
    return base


def bb_pedigree() -> str:
    """Two generations of the retinal-degeneration pedigree (autosomal recessive)."""
    y1, y2 = 72, 162
    i1, i2 = 250, 330
    kids = [("II-1", "square", 130, True), ("II-2", "circle", 210, False),
            ("II-3", "square", 290, False), ("II-4", "circle", 370, True),
            ("II-5", "square", 450, False)]
    spouse_x, sib_x = 40, 210   # II-6 (married in) joined to II-2 by a routed line
    body = []
    # generation I
    body.append(_ped_symbol("square", i1, y1, False))
    body.append(_ped_symbol("circle", i2, y1, False))
    body.append(_line(i1 + 14, y1, i2 - 14, y1, width=2.5))
    body.append(_txt(i1, y1 - 24, "I-1", size=11, bold=True))
    body.append(_txt(i2, y1 - 24, "I-2", size=11, bold=True))
    # drop to the sibship line
    mid = (i1 + i2) / 2
    sib_y = 118
    body.append(_line(mid, y1 + 14, mid, sib_y, width=2.5))
    body.append(_line(kids[0][2], sib_y, kids[-1][2], sib_y, width=2.5))
    for label, kind, cx, aff in kids:
        body.append(_line(cx, sib_y, cx, y2 - 14, width=2.5))
        body.append(_ped_symbol(kind, cx, y2, aff))
        body.append(_txt(cx, y2 + 34, label, size=11, bold=True))
    # II-2 x II-6: routed connector (nothing else occupies this corner)
    body.append(_ped_symbol("square", spouse_x, y2, False))
    body.append(_txt(spouse_x, y2 + 34, "II-6", size=11, bold=True))
    body.append(_line(spouse_x, y2 + 14, spouse_x, y2 + 58, width=2.5))
    body.append(_line(spouse_x, y2 + 58, sib_x, y2 + 58, width=2.5))
    body.append(_line(sib_x, y2 + 58, sib_x, y2 + 14, width=2.5))
    # generation labels
    body.append(_txt(20, y1 + 5, "I", size=13, bold=True))
    body.append(_txt(20, y2 + 5, "II", size=13, bold=True))
    # legend, top left
    body.append(_ped_symbol("square", 40, 26, True))
    body.append(_txt(58, 30, "affected", size=10, anchor="start"))
    body.append(_ped_symbol("square", 130, 26, False))
    body.append(_txt(148, 30, "unaffected", size=10, anchor="start"))
    return _wrap("".join(body), w=500, h=230)


# ---------- bio: Michaelis-Menten saturation curves -----------------------
def _mm(Km: float, Vmax: float, s: float) -> float:
    return Vmax * s / (Km + s)


def bb_saturation() -> str:
    """v vs [S] for control (Km 0.5, Vmax 100), Compound X, Compound Y."""
    x0, y0, x1, y1 = 70, 212, 385, 28
    ss = [i * 0.25 for i in range(33)]  # 0 .. 8 mM

    def xp(s):
        return x0 + s / 8.0 * (x1 - x0)

    def yp(v):
        return y0 - v / 110.0 * (y0 - y1)

    ticks = [(xp(v), str(v)) for v in (0, 2, 4, 6, 8)]
    yticks = [(yp(v), str(v)) for v in (25, 50, 75, 100)]
    body = [_axes(x0, y0, x1, y1, xticks=ticks, yticks=yticks,
                  xlabel="[S] (mM)", ylabel="v (µmol/(min·mg))")]
    body.append(_line(x0, yp(100), x1, yp(100), dash="3 4", width=1.2, color=FAINT))
    body.append(_line(x0, yp(50), x1, yp(50), dash="3 4", width=1.2, color=FAINT))
    body.append(_mpoly([(xp(s), yp(_mm(0.5, 100, s))) for s in ss], width=3))
    body.append(_mpoly([(xp(s), yp(_mm(2.0, 100, s))) for s in ss], width=3))
    body.append(_mpoly([(xp(s), yp(_mm(0.5, 50, s))) for s in ss], width=3, dash="7 4"))
    body.append(_txt(150, 48, "no inhibitor", size=10, anchor="start"))
    body.append(_txt(262, 120, "Compound X (Km 2.0)", size=10, anchor="start"))
    body.append(_txt(300, 150, "Compound Y (Vmax 50)", size=10, anchor="start"))
    return _wrap("".join(body), w=420, h=260)


# ---------- bio: glycolysis flow diagram ----------------------------------
def bb_glycolysis() -> str:
    """Boxes-and-arrows summary: 2 ATP invested, 4 ATP + 2 NADH harvested."""
    cx = 150
    steps = [(46, "Glucose", "6 C"), (110, "Fructose-1,6-bisphosphate", "6 C"),
             (174, "2 × glyceraldehyde-3-phosphate", "2 × 3 C"),
             (232, "2 × pyruvate", "2 × 3 C")]
    body = []
    for y, label, sub in steps:
        body.append(f'<rect x="{cx - 110}" y="{y - 20}" width="220" height="40" '
                    f'fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
        body.append(_txt(cx, y - 2, label, size=11, bold=True))
        body.append(_txt(cx, y + 13, sub, size=9, fill="#666"))
    # arrow gaps match the box edges: 66->90, 130->154, 194->212
    arrows = [(66, 90, "2 ATP invested"), (130, 154, "cleaved into two 3-C sugars"),
              (194, 212, "4 ATP + 2 NADH produced")]
    for y1, y2, note in arrows:
        body.append(_line(cx, y1, cx, y2 - 3, width=2.5, arrow=True))
        body.append(_txt(cx + 12, (y1 + y2) / 2 + 4, note, size=10, anchor="start"))
    body.append(_txt(388, 96, "investment", size=10, anchor="end", fill="#666"))
    body.append(_txt(388, 110, "phase", size=10, anchor="end", fill="#666"))
    body.append(_txt(388, 168, "payoff", size=10, anchor="end", fill="#666"))
    body.append(_txt(388, 182, "phase", size=10, anchor="end", fill="#666"))
    return _wrap("".join(body), w=460, h=260)


# ---------- bio: oxygen-hemoglobin dissociation curves --------------------
def bb_o2hb() -> str:
    """Bohr shift: exercise moves the curve right (P50 26 -> 40 mmHg)."""
    x0, y0, x1, y1 = 70, 212, 385, 28
    n = 2.8

    def curve(p50):
        pts = []
        p = 1.0
        while p <= 100:
            sat = p ** n / (p50 ** n + p ** n) * 100
            pts.append((p, sat))
            p += 1.0
        return pts

    def xp(p):
        return x0 + p / 100.0 * (x1 - x0)

    def yp(s):
        return y0 - s / 100.0 * (y0 - y1)

    ticks = [(xp(v), str(v)) for v in (20, 40, 60, 80, 100)]
    yticks = [(yp(v), str(v)) for v in (25, 50, 75, 100)]
    body = [_axes(x0, y0, x1, y1, xticks=ticks, yticks=yticks,
                  xlabel="pO2 (mmHg)", ylabel="Hb O2 saturation (%)")]
    body.append(_line(x0, yp(50), x1, yp(50), dash="3 4", width=1.2, color=FAINT))
    body.append(_mpoly([(xp(p), yp(s)) for p, s in curve(26)], width=3))
    body.append(_mpoly([(xp(p), yp(s)) for p, s in curve(40)], width=3, dash="7 4"))
    body.append(_dot(xp(26), yp(50)))
    body.append(_dot(xp(40), yp(50)))
    body.append(_txt(108, 60, "resting", size=10, anchor="start"))
    body.append(_txt(108, 74, "P50 ≈ 26", size=10, anchor="start", fill="#666"))
    body.append(_txt(215, 138, "exercise (right shift)", size=10, anchor="start"))
    body.append(_txt(215, 152, "P50 ≈ 40", size=10, anchor="start", fill="#666"))
    return _wrap("".join(body), w=420, h=260)


# ---------- psych-soc: demographic transition line chart ------------------
def ps_demographic_transition() -> str:
    """Country X crude birth and death rates, 1900-2020."""
    years = [1900, 1920, 1940, 1960, 1980, 1990, 2020]
    cbr = [42, 41, 40, 34, 22, 18, 12]
    cdr = [38, 30, 20, 12, 10, 9, 9]
    x0, y0, x1, y1 = 70, 212, 385, 28

    def xp(y):
        return x0 + (y - 1900) / 120.0 * (x1 - x0)

    def yp(r):
        return y0 - r / 50.0 * (y0 - y1)

    ticks = [(xp(y), str(y)) for y in (1900, 1940, 1980, 2020)]
    yticks = [(yp(v), str(v)) for v in (10, 20, 30, 40, 50)]
    body = [_axes(x0, y0, x1, y1, xticks=ticks, yticks=yticks,
                  xlabel="year", ylabel="rate per 1,000")]
    # shaded natural-increase gap over 1900-1940
    gap = [(xp(y), yp(r)) for y, r in zip(years[:3], cbr[:3])]
    gap += [(xp(y), yp(r)) for y, r in zip(years[2::-1], cdr[2::-1])]
    fill = (" " .join(f"{x:.1f},{y:.1f}" for x, y in gap))
    body.append(f'<polygon points="{fill}" fill="#ddd" stroke="none" opacity="0.7"/>')
    body.append(_mpoly([(xp(y), yp(r)) for y, r in zip(years, cbr)], width=3))
    body.append(_mpoly([(xp(y), yp(r)) for y, r in zip(years, cdr)], width=3, dash="7 4"))
    body.append(_txt(228, yp(40) - 8, "birth rate", size=10, anchor="start"))
    body.append(_txt(228, yp(12) - 8, "death rate", size=10, anchor="start"))
    body.append(_txt(xp(1920), 46, "gap = rapid growth", size=9, fill="#666"))
    return _wrap("".join(body), w=420, h=260)


# ---------- psych-soc: Milgram obedience bar chart ------------------------
def ps_obedience_bars() -> str:
    """Percent of participants going to 450 V in each Milgram variation."""
    conds = [("Yale\nbaseline", 65), ("Bridgeport\noffice", 48),
             ("orders by\nphone", 20), ("peers refuse\nfirst", 10)]
    x0, y0, x1, y1 = 70, 212, 385, 28
    n = len(conds)
    slot = (x1 - x0) / n
    bar_w = slot * 0.58

    def yp(v):
        return y0 - v / 70.0 * (y0 - y1)

    yticks = [(yp(v), str(v)) for v in (10, 20, 30, 40, 50, 60, 70)]
    body = [_axes(x0, y0, x1, y1, yticks=yticks, ylabel="% to 450 V")]
    for i, (label, val) in enumerate(conds):
        bx = x0 + slot * i + (slot - bar_w) / 2
        body.append(f'<rect x="{bx:.1f}" y="{yp(val):.1f}" width="{bar_w:.1f}" '
                    f'height="{y0 - yp(val):.1f}" fill="#fff" stroke="{INK}" '
                    f'stroke-width="2.5"/>')
        body.append(_txt(bx + bar_w / 2, yp(val) - 8, f"{val}%", size=11, bold=True))
        for j, part in enumerate(label.split("\n")):
            body.append(_txt(bx + bar_w / 2, y0 + 16 + j * 12, part, size=10))
    return _wrap("".join(body), w=420, h=260)


# ---------- writer ---------------------------------------------------------
def write(key: str, svg: str) -> str:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{key}.svg"
    path.write_text(svg, encoding="utf-8")
    rel = f"items/{key}.svg"
    return rel


# MCAT exam-bank figures: key -> generator. Each figure carries only numbers
# that already appear in the item's stem/passage, so art and key cannot drift.
MCAT_FIGURES = {
    "mcat-cp-051-circuit": cp_circuit,
    "mcat-cp-001-lb-plot": cp_lb_plot,
    "mcat-cp-005-lb-inhibitor": cp_lb_inhibitor,
    "mcat-cp-007-titration": cp_titration,
    "mcat-cp-013-velocity-time": cp_velocity_time,
    "mcat-bb-001-pedigree": bb_pedigree,
    "mcat-bb-006-saturation": bb_saturation,
    "mcat-bb-049-glycolysis": bb_glycolysis,
    "mcat-bb-057-o2hb": bb_o2hb,
    "mcat-ps-056-transition": ps_demographic_transition,
    "mcat-ps-028-milgram": ps_obedience_bars,
}


def write_mcat_figures() -> dict[str, str]:
    return {key: write(key, gen()) for key, gen in MCAT_FIGURES.items()}


if __name__ == "__main__":
    for key, rel in sorted(write_mcat_figures().items()):
        print(f"{rel}")


# ===========================================================================
# 4-panel composite sheets for the figure-grouping items
#
# The inductive items used to carry their four figures as words inside the
# stem ("Four figures are shown. A. a square ..."). Each now gets one sheet:
# a 2x2 grid whose panels A-D are labelled with the choice letters, so the
# choices act as the legend for the picture.
# ===========================================================================
PANEL = 300          # each cell is PANEL x PANEL
GAP = 14             # gutter between cells and around the sheet
PANEL_LABELS = ("A", "B", "C", "D")
STROKE = 'fill="none" stroke="#333" stroke-width="4"'


# ---------- cell compositor ------------------------------------------------
def panel(letter: str, body: str, x: int = 0, y: int = 0) -> str:
    """One PANEL x PANEL cell: plate, the drawing, its letter in the corner."""
    return (f'<g transform="translate({x} {y})">'
            f'<rect width="{PANEL}" height="{PANEL}" fill="#fafafa" stroke="#ddd"/>'
            f'{body}'
            f'<text x="{PANEL - 16}" y="{PANEL - 16}" font-size="34" '
            f'font-family="serif" font-weight="bold" text-anchor="end" '
            f'fill="#3b5bdb">{letter}</text></g>')


def sheet(bodies: dict) -> str:
    """2x2 composite of four drawings keyed by their panel letter."""
    edge = PANEL + GAP
    spots = {"A": (GAP, GAP), "B": (GAP + edge, GAP),
             "C": (GAP, GAP + edge), "D": (GAP + edge, GAP + edge)}
    size = 2 * PANEL + 3 * GAP
    body = "".join(panel(L, bodies[L], *spots[L]) for L in PANEL_LABELS)
    return _wrap(body, size, size)


# ---------- primitives (panel-local coordinates, centre 150 150) -----------
def _sheet_ring(n: int, cx: float, cy: float, r: float, rot: float = -90.0) -> list:
    """`n` points evenly spaced on a circle, first one at angle `rot`."""
    return [(cx + r * math.cos(math.radians(rot + k * 360.0 / n)),
             cy + r * math.sin(math.radians(rot + k * 360.0 / n)))
            for k in range(n)]


def _sheet_poly(pts) -> str:
    s = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{s}" {STROKE}/>'


def poly(n: int, cx: float = 150, cy: float = 150, r: float = 108,
         rot: float = -90.0) -> str:
    """Regular n-gon: triangle 3, square 4, pentagon 5, hexagon 6, octagon 8."""
    return _sheet_poly(_sheet_ring(n, cx, cy, r, rot))


def rect(w: float = 212, h: float = 132, cx: float = 150, cy: float = 150) -> str:
    return (f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" {STROKE}/>')


def sq(side: float = 170, cx: float = 150, cy: float = 150) -> str:
    """Axis-aligned square (a 4-gon on the -45 degree ring)."""
    return poly(4, cx, cy, side / math.sqrt(2), rot=-45.0)


def circle(r: float = 108, cx: float = 150, cy: float = 150) -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" {STROKE}/>'


def tri(p0, p1, p2) -> str:
    return _sheet_poly([p0, p1, p2])


def dots(points, r: float = 11) -> str:
    return "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#333"/>'
                   for x, y in points)


def corner_dots(pts) -> str:
    return dots(pts)


def side_mid_dots(n: int, cx: float = 150, cy: float = 150, r: float = 108,
                  rot: float = -90.0) -> str:
    """A dot on the midpoint of each of a regular n-gon's n sides."""
    ring = _sheet_ring(n, cx, cy, r, rot)
    return dots([((x0 + x1) / 2, (y0 + y1) / 2)
                 for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1])], r=9)


def letter(ch: str, size: int = 190) -> str:
    """A capital letter drawn as text, as in the mirror-image figures."""
    return (f'<text x="150" y="215" font-size="{size}" font-family="serif" '
            f'text-anchor="middle">{ch}</text>')


# ---------- composite shapes ----------------------------------------------
RIGHT_TRI = ((80, 234), (80, 70), (226, 234))       # right angle at the corner
SCALENE_TRI = ((56, 232), (98, 66), (244, 232))     # three unequal sides
ISO_TRI = ((150, 60), (64, 234), (236, 234))        # apex over the base midpoint
TRAP = ((88, 86), (212, 86), (248, 214), (52, 214))  # isosceles trapezoid
PARA = ((112, 86), (250, 86), (188, 214), (50, 214))  # parallelogram
U_PATH = ('<path d="M96 70 V160 A54 54 0 0 0 204 160 V70" fill="none" '
          'stroke="#333" stroke-width="14" stroke-linecap="round"/>')
EIGHT_PATH = ('<path d="M150 150 A55 55 0 0 0 150 40 A55 55 0 0 0 150 150 '
              'A55 55 0 0 0 150 260 A55 55 0 0 0 150 150" '
              f'fill="none" stroke="#333" stroke-width="4"/>')
INSIDE3 = ((150, 118), (124, 168), (176, 168))       # 3 interior dots
INSIDE4 = ((126, 126), (174, 126), (126, 174), (174, 174))  # 4 interior dots


def star(points: int = 5, cx: float = 150, cy: float = 150, r_out: float = 112,
         r_in: float = 45) -> str:
    pts = []
    for k in range(2 * points):
        r = r_out if k % 2 == 0 else r_in
        a = math.radians(-90.0 + k * 180.0 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return _sheet_poly(pts)


def figure_eight() -> str:
    return EIGHT_PATH


# ---------- the 14 inductive sheets, panel per choice letter ---------------
# Shared dimensions so every sheet draws its shapes at the same scale.
TRI_R = 108          # regular triangle / pentagon / hexagon ring radius
SQ_SIDE = 170        # axis-aligned square
SQ_R = SQ_SIDE / math.sqrt(2)   # the square seen as a 4-gon on a ring
SPLIT = 'stroke="#333" stroke-width="4"'


def inductive_sheets() -> dict:
    """item id -> 4-panel SVG body set, one panel per answer choice."""
    rim = [(150 + 100 * math.cos(math.radians(a)),
            150 + 100 * math.sin(math.radians(a)))
           for a in (45, 135, 225, 315)]              # dots ON the circle
    row = [(78, 220), (126, 220), (174, 220), (222, 220)]  # dots along one edge
    square = sq(SQ_SIDE)
    return {
        # --- part1-inductive ------------------------------------------------
        "nmat-p1i-022": {"A": poly(3, r=TRI_R), "B": square, "C": poly(5, r=TRI_R),
                         "D": tri(*RIGHT_TRI)},
        "nmat-p1i-024": {"A": rect(), "B": poly(3, r=TRI_R), "C": circle(),
                         "D": square},
        "nmat-p1i-025": {"A": rect() + f'<line x1="150" y1="84" x2="150" '
                                       f'y2="216" {SPLIT}/>',
                         "B": poly(3, r=TRI_R),
                         "C": square + f'<line x1="65" y1="65" x2="235" '
                                       f'y2="235" {SPLIT}/>',
                         "D": circle() + f'<line x1="42" y1="150" x2="258" '
                                         f'y2="150" {SPLIT}/>'},
        "nmat-p1i-026": {"A": square + corner_dots(_sheet_ring(4, 150, 150, SQ_R,
                                                          rot=-45.0)),
                         "B": circle(100) + dots(rim, r=10),
                         "C": poly(3, r=TRI_R) + corner_dots(_sheet_ring(3, 150, 150,
                                                                   TRI_R)),
                         "D": square + dots(row, r=10)},
        "nmat-p1i-027": {"A": poly(6, r=TRI_R), "B": square, "C": poly(5, r=TRI_R),
                         "D": poly(8, r=112)},
        "nmat-p1i-028": {"A": U_PATH, "B": poly(3, r=TRI_R), "C": circle(),
                         "D": square},
        "nmat-p1i-029": {"A": rect(), "B": tri(*SCALENE_TRI),
                         "C": tri(*ISO_TRI), "D": poly(5, r=TRI_R)},
        "nmat-p1i-030": {"A": poly(3, r=TRI_R) + dots(INSIDE3),
                         "B": square + dots(INSIDE3),
                         "C": poly(5, r=TRI_R) + dots(INSIDE4),
                         "D": circle() + dots(INSIDE3)},
        # --- drill/part1-inductive ------------------------------------------
        "nmat-d-p1i-019": {"A": letter("A"), "B": letter("R"),
                           "C": letter("B"), "D": letter("P")},
        "nmat-d-p1i-020": {"A": _sheet_poly(TRAP), "B": tri(*ISO_TRI),
                           "C": rect(), "D": _sheet_poly(PARA)},
        "nmat-d-p1i-021": {"A": poly(3, r=TRI_R) + corner_dots(_sheet_ring(3, 150, 150,
                                                                    TRI_R)),
                           "B": square + side_mid_dots(4, r=SQ_R, rot=-45.0),
                           "C": poly(5, r=TRI_R) + side_mid_dots(5, r=TRI_R),
                           "D": poly(6, r=TRI_R) + side_mid_dots(6, r=TRI_R)},
        "nmat-d-p1i-022": {"A": poly(3, r=TRI_R), "B": square,
                           "C": poly(5, r=TRI_R), "D": poly(6, r=TRI_R)},
        "nmat-d-p1i-023": {"A": circle(), "B": figure_eight(),
                           "C": square, "D": poly(3, r=TRI_R)},
        "nmat-d-p1i-025": {"A": star(), "B": square, "C": poly(6, r=TRI_R),
                           "D": poly(3, r=TRI_R)},
    }


def write_inductive_sheets() -> list[str]:
    """Emit every 4-panel sheet; returns the figure paths in bank order."""
    return [write(iid, sheet(bodies))
            for iid, bodies in sorted(inductive_sheets().items())]
