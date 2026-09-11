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
        "nmat-p1i-023": {"A": letter("N"), "B": letter("H"),
                         "C": letter("M"), "D": letter("A")},
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
        "nmat-d-p1i-024": {"A": letter("N"), "B": letter("Z"),
                           "C": letter("H"), "D": letter("M")},
    }


def write_inductive_sheets() -> list[str]:
    """Emit every 4-panel sheet; returns the figure paths in bank order."""
    return [write(iid, sheet(bodies))
            for iid, bodies in sorted(inductive_sheets().items())]


# ===========================================================================
# Part-1 perceptual sheets (mirror-image + hidden-figure)
#
# Same sheet grammar as the inductive items: a 2x2 grid whose panels A-D are
# labelled with the choice letters, so the choices act as the legend. Mirror
# panels draw the object, the dashed mirror axis and an image produced by a
# real SVG transform, so a panel can never contradict its own choice text.
# Item nmat-p1p-024 is a counting task over five panels, so it gets a
# numbered 1x5 strip instead of an A-D sheet.
# ===========================================================================
CLUTTER = "#bbb"          # faint strokes that bury a hidden figure
OBJECT = "#888"           # the un-reflected object in a mirror panel
AXIS = "#3b5bdb"          # dashed mirror axes, panel letters, image glyphs
STRIP_CELL = 150          # cell edge for the numbered strip
STRIP_GAP = 12


def _glyph(ch: str, x: float, y: float, size: int, fill=INK) -> str:
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" font-family="serif" '
            f'text-anchor="middle" fill="{fill}">{_esc(ch)}</text>')


def _hflip(inner: str) -> str:
    """Mirror `inner` left-right about the panel's vertical centre (x = 150)."""
    return f'<g transform="translate(300 0) scale(-1 1)">{inner}</g>'


def seg(x1, y1, x2, y2, color=INK, width=4, dash=None) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="{color}" stroke-width="{width}"{d}/>')


def ellipse_fig(rx: float, ry: float, cx: float = 150, cy: float = 150) -> str:
    return f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" {STROKE}/>'


def open_poly(pts, color=INK, width=4) -> str:
    s = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    return (f'<polyline points="{s}" fill="none" stroke="{color}" '
            f'stroke-width="{width}"/>')


def tri_c(pts, color=INK, width=4) -> str:
    """A closed triangle in an arbitrary colour (clutter variants)."""
    return _sheet_poly(pts).replace('stroke="#333"', f'stroke="{color}"')


def box(x, y, w, h, color=INK, width=4, fill="none") -> str:
    return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" '
            f'fill="{fill}" stroke="{color}" stroke-width="{width}"/>')


def shaded_circle(r: float, cx: float, cy: float) -> str:
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="#cfcfcf" '
            f'stroke="{CLUTTER}" stroke-width="3"/>')


def small_circle(r: float, cx: float, cy: float) -> str:
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="none" '
            f'stroke="{CLUTTER}" stroke-width="3"/>')


def small_letter(ch: str, x: float, y: float, size: int = 42) -> str:
    return _glyph(ch, x, y, size, fill="#999")


def v_axis(x: float = 150) -> str:
    return (f'<line x1="{x:.0f}" y1="28" x2="{x:.0f}" y2="272" stroke="{AXIS}" '
            f'stroke-width="2" stroke-dasharray="6 4"/>')


def h_axis(y: float = 150) -> str:
    return (f'<line x1="28" y1="{y:.0f}" x2="272" y2="{y:.0f}" stroke="{AXIS}" '
            f'stroke-width="2" stroke-dasharray="6 4"/>')


def arrow_seg(x1, y1, x2, y2, color=INK, width=5) -> str:
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="{color}" stroke-width="{width}" {ARROW}/>')


# ---------- mirror-image panels -------------------------------------------
def mirror_cell(ch: str, size: int = 120) -> str:
    """`ch`, the vertical mirror, and the image a real transform produces."""
    return (_glyph(ch, 88, 195, size) + v_axis()
            + _hflip(_glyph(ch, 88, 195, size, fill=AXIS)))


def word_mirror_cell(word: str) -> str:
    """A word, the mirror, and its reflection (order reversed, glyphs flipped).

    Font size is scaled to the letter count so even a six-letter word in the
    wide DejaVu serif (MOM ~2.8 em, TOMATO ~4.7 em) keeps clear of the axis.
    """
    size = {3: 42, 4: 36, 5: 30, 6: 26}[len(word)]
    return (_glyph(word, 82, 168, size) + v_axis()
            + _hflip(_glyph(word, 82, 168, size, fill=AXIS)))


def word_image_cell(obj: str, image: str, size: int = 54) -> str:
    """The object string on the left, a candidate image on the right."""
    return (_glyph(obj, 85, 168, size) + v_axis()
            + _glyph(image, 215, 168, size, fill=AXIS))


def rot_cell(obj: str, image: str, size: int = 84) -> str:
    """Object string, a half-turn arrow over the pair, candidate result."""
    arc = (f'<path d="M118 58 A56 38 0 0 1 182 58" fill="none" stroke="{AXIS}" '
           f'stroke-width="3" {ARROW}/>')
    return _glyph(obj, 82, 190, size) + _glyph(image, 218, 190, size) + arc


def water_cell(obj: str, image: str, size: int = 92) -> str:
    """Object above a horizontal mirror line, candidate image below it."""
    return (_glyph(obj, 150, 126, size) + h_axis(150)
            + _glyph(image, 150, 264, size, fill=AXIS))


def pair_cell(left: str, right: str, size: int = 120) -> str:
    """The two letters of a candidate pair, mirror line between them."""
    return _glyph(left, 88, 195, size) + v_axis() + _glyph(right, 212, 195, size)


def axes_cell(ch: str, size: int = 170) -> str:
    """A letter with both mirror axes drawn across it."""
    return v_axis() + h_axis() + letter(ch, size)


_ARROW_DIRS = {  # (tail, head) for each diagonal pointing, image half centre
    "up-right": ((183, 222), (247, 158)),
    "up-left": ((247, 222), (183, 158)),
    "down-right": ((183, 158), (247, 222)),
    "down-left": ((247, 158), (183, 222)),
}


def image_arrow_cell(pointing: str) -> str:
    """Object arrow (up-right), the mirror, and an image arrow `pointing`."""
    tail, head = _ARROW_DIRS[pointing]
    return (arrow_seg(53, 222, 117, 158, color=OBJECT) + v_axis()
            + arrow_seg(*tail, *head))


def stroke_L(stem_x: float, foot_x: float, y_top: float, y_bot: float,
             foot_end: str, color=INK, width=11) -> str:
    """An L of two strokes: vertical stem, horizontal foot at either end."""
    if foot_end == "bottom":
        d = f"M{stem_x:.0f} {y_top:.0f} V{y_bot:.0f} H{foot_x:.0f}"
    else:
        d = f"M{stem_x:.0f} {y_bot:.0f} V{y_top:.0f} H{foot_x:.0f}"
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"/>'


def mirror_L_cell(foot: str, end: str) -> str:
    """Object L (foot to the right at the bottom) and its claimed image."""
    obj = stroke_L(85, 135, 70, 230, "bottom", color=OBJECT)
    foot_x = 215 + (50 if foot == "right" else -50)
    return obj + v_axis() + stroke_L(215, foot_x, 70, 230, end)


# ---------- hidden-figure panels ------------------------------------------
def arrow_fig(pointing: str = "up") -> str:
    """Shaft plus two slanted strokes meeting in a point, up or down."""
    if pointing == "up":
        return (seg(150, 240, 150, 70) + seg(110, 105, 150, 60)
                + seg(190, 105, 150, 60))
    return seg(150, 60, 150, 240) + seg(110, 195, 150, 240) + seg(190, 195, 150, 240)


def tombstone() -> str:
    """Rectangle with a semicircle resting flat-side down on its top edge."""
    return box(65, 130, 170, 110) + \
        '<path d="M65 130 A85 85 0 0 1 235 130" fill="none" ' \
        f'stroke="{INK}" stroke-width="4"/>'


# ---------- the numbered strip for the counting item ----------------------
def strip(label_bodies: dict) -> str:
    """1xN row of numbered cells, label bottom-right in the house colour."""
    n = len(label_bodies)
    m = STRIP_GAP
    w = n * STRIP_CELL + (n + 1) * m
    h = STRIP_CELL + 2 * m
    cells = "".join(
        f'<g transform="translate({m + i * (STRIP_CELL + m)} {m})">'
        f'<rect width="{STRIP_CELL}" height="{STRIP_CELL}" fill="#fafafa" '
        f'stroke="#ddd"/>{body}'
        f'<text x="{STRIP_CELL - 10}" y="{STRIP_CELL - 10}" font-size="24" '
        f'font-family="serif" font-weight="bold" text-anchor="end" '
        f'fill="{AXIS}">{label}</text></g>'
        for i, (label, body) in enumerate(label_bodies.items()))
    return _wrap(cells, w, h)


TRI_IN_TRI = (tri((75, 22), (138, 128), (12, 128))
              + f'<circle cx="75" cy="92" r="30" {STROKE}/>')


def strip_panels() -> dict:
    """The five panels of nmat-p1p-024, keyed by their printed number."""
    return {
        "1": TRI_IN_TRI,                                   # circle in triangle
        "2": circle(58, 75, 75) + tri((75, 32), (115, 105), (35, 105)),
        "3": sq(116, 75, 75) + f'<circle cx="75" cy="75" r="38" {STROKE}/>',
        "4": TRI_IN_TRI + box(8, 8, 18, 18),               # + small corner square
        "5": sq(116, 75, 75) + f'<circle cx="52" cy="75" r="22" {STROKE}/>'
             + f'<circle cx="98" cy="75" r="22" {STROKE}/>',
    }


# ---------- the 19 perceptual sheets, panel per choice letter -------------
def perceptual_sheets() -> dict:
    """item id -> 4-panel SVG bodies, keyed by the choice each panel depicts."""
    return {
        # --- mirror-image ---------------------------------------------------
        "nmat-p1p-001": {"A": mirror_cell("b"), "B": mirror_cell("d"),
                         "C": mirror_cell("m"), "D": mirror_cell("p")},
        "nmat-p1p-002": {"A": word_image_cell("pod", "boq"),
                         "B": word_image_cell("pod", "qob"),
                         "C": word_image_cell("pod", "bod"),
                         "D": word_image_cell("pod", "qod")},
        "nmat-p1p-003": {"A": rot_cell("bd", "qp"), "B": rot_cell("bd", "pq"),
                         "C": rot_cell("bd", "db"), "D": rot_cell("bd", "qb")},
        "nmat-p1p-004": {"A": water_cell("d", "b"), "B": water_cell("d", "p"),
                         "C": water_cell("d", "q"), "D": water_cell("d", "d")},
        "nmat-p1p-005": {"A": word_mirror_cell("MOM"),
                         "B": word_mirror_cell("DAD"),
                         "C": word_mirror_cell("NOON"),
                         "D": word_mirror_cell("EYE")},
        "nmat-p1p-006": {"A": axes_cell("N"), "B": axes_cell("C"),
                         "C": axes_cell("M"), "D": axes_cell("H")},
        "nmat-p1p-007": {"A": image_arrow_cell("down-right"),
                         "B": image_arrow_cell("up-left"),
                         "C": image_arrow_cell("down-left"),
                         "D": image_arrow_cell("up-right")},
        "nmat-p1p-008": {"A": pair_cell("p", "d"), "B": pair_cell("q", "b"),
                         "C": pair_cell("n", "u"), "D": pair_cell("b", "d")},
        "nmat-p1p-009": {"A": mirror_L_cell("left", "bottom"),
                         "B": mirror_L_cell("right", "top"),
                         "C": mirror_L_cell("right", "bottom"),
                         "D": mirror_L_cell("left", "top")},
        "nmat-p1p-010": {"A": word_mirror_cell("DAMAGE"),
                         "B": word_mirror_cell("PIXEL"),
                         "C": word_mirror_cell("TOMATO"),
                         "D": word_mirror_cell("CHOICE")},
        # --- hidden figure ---------------------------------------------------
        "nmat-p1p-021": {
            # A: circle + horizontal midline, two small triangles beside it
            "A": (circle(80, 100, 150) + seg(20, 150, 180, 150)
                  + tri((200, 80), (280, 80), (240, 135))
                  + tri((200, 215), (280, 215), (240, 160))),
            # B: the target (circle + vertical diameter) partly crossed by
            #    two overlapping squares
            "B": (circle(80, 100, 150) + seg(100, 70, 100, 230)
                  + box(140, 100, 75, 75) + box(180, 145, 75, 75)),
            "C": ellipse_fig(95, 55) + seg(150, 95, 150, 205),
            "D": sq(160) + seg(150, 70, 150, 230),
        },
        "nmat-p1p-022": {
            # A: an X, four circles around it
            "A": (seg(75, 75, 225, 225) + seg(225, 75, 75, 225)
                  + small_circle(22, 60, 60) + small_circle(22, 240, 60)
                  + small_circle(22, 60, 240) + small_circle(22, 240, 240)),
            # B: an L (strokes meeting end to end), two triangles beside
            "B": (seg(110, 70, 110, 230) + seg(110, 230, 200, 230)
                  + tri((215, 70), (285, 70), (250, 125))
                  + tri((215, 190), (285, 190), (250, 245))),
            # C: the target plus, drawn over a zigzag
            "C": (open_poly(((20, 60), (65, 110), (105, 50), (150, 105),
                             (190, 45), (235, 100), (280, 40)), color=CLUTTER)
                  + seg(150, 60, 150, 240) + seg(60, 150, 240, 150)),
            # D: vertical stroke touching two parallels without crossing
            "D": seg(90, 70, 210, 70) + seg(90, 230, 210, 230)
                 + seg(150, 70, 150, 230),
        },
        "nmat-p1p-023": {
            # A: the target star over three overlapping rectangles
            "A": (box(40, 60, 140, 90, color=CLUTTER, width=3)
                  + box(90, 110, 150, 95, color=CLUTTER, width=3)
                  + box(55, 160, 130, 85, color=CLUTTER, width=3)
                  + star(5, r_out=105, r_in=42)),
            "B": poly(3, r=105, rot=-90) + poly(3, r=105, rot=90),
            "C": circle(105) + star(4, r_out=105, r_in=38),
            "D": poly(5, r=TRI_R),
        },
        "nmat-p1p-025": {
            "A": (rect() + seg(150, 84, 150, 216)
                  + f'<circle cx="62" cy="202" r="13" {STROKE}/>'),
            "B": rect() + seg(44, 150, 256, 150),
            "C": rect() + seg(150, 84, 150, 216) + seg(44, 84, 256, 216),
            "D": rect() + seg(150, 84, 150, 216),
        },
        "nmat-p1p-026": {
            "A": seg(150, 60, 150, 240) + seg(60, 150, 240, 150),
            "B": seg(150, 235, 150, 105) + seg(150, 105, 214, 41),
            # C: the target L, partly hidden by a shaded circle laid over it
            "C": (seg(120, 60, 120, 235) + seg(120, 235, 235, 235)
                  + shaded_circle(60, 170, 100)),
            "D": seg(110, 70, 110, 230) + seg(190, 70, 190, 230),
        },
        "nmat-p1p-027": {
            # A: the target up arrow, across a field of small circles
            "A": ("".join(small_circle(9, x, y) for x, y in
                          ((45, 60), (105, 45), (215, 55), (265, 95), (40, 150),
                           (255, 170), (70, 240), (140, 265), (220, 250),
                           (262, 262), (36, 210), (250, 120)))
                  + arrow_fig("up")),
            "B": arrow_fig("down"),
            "C": seg(150, 80, 150, 240) + seg(85, 80, 215, 80),
            "D": seg(150, 120, 150, 240) + seg(105, 60, 150, 125)
                 + seg(195, 60, 150, 125),
        },
        "nmat-p1p-028": {
            # A: an H among other letters
            "A": (seg(105, 70, 105, 230) + seg(195, 70, 195, 230)
                  + seg(105, 150, 195, 150)
                  + small_letter("s", 55, 112) + small_letter("e", 250, 122)
                  + small_letter("t", 58, 236) + small_letter("r", 246, 240)),
            # B: slanted strokes meeting at the top, no crossbar
            "B": (seg(85, 230, 150, 70) + seg(150, 70, 215, 230)
                  + small_letter("s", 52, 120) + small_letter("e", 252, 130)
                  + small_letter("r", 120, 272, size=36)),
            # C: slanted strokes meeting at the bottom, no crossbar
            "C": (seg(85, 70, 150, 230) + seg(150, 230, 215, 70)
                  + small_letter("s", 52, 130) + small_letter("e", 252, 120)
                  + small_letter("t", 180, 272, size=36)),
            # D: the target capital A, printed inside a bordered box
            "D": (box(55, 55, 190, 190, width=3)
                  + seg(85, 230, 150, 70) + seg(150, 70, 215, 230)
                  + seg(108, 175, 192, 175)),
        },
        "nmat-p1p-029": {
            # A: a square on its corner, line joining two side midpoints
            "A": poly(4, r=110, rot=-90) + seg(205, 95, 95, 205),
            # B: square with both diagonals, overlapped by a triangle
            "B": (sq(170) + seg(65, 65, 235, 235) + seg(235, 65, 65, 235)
                  + tri_c(((150, 30), (270, 170), (60, 200)), color=CLUTTER)),
            "C": rect(230, 120) + seg(35, 90, 265, 210),
            "D": tri((150, 50), (250, 235), (50, 235)) + seg(150, 50, 150, 235),
        },
        "nmat-p1p-030": {
            "A": box(65, 130, 170, 110) + tri((65, 130), (235, 130), (150, 55)),
            "B": (box(65, 70, 170, 110)
                  + '<path d="M65 180 A85 85 0 0 0 235 180" fill="none" '
                    f'stroke="{INK}" stroke-width="4"/>'),
            "C": box(65, 130, 170, 110) + f'<circle cx="150" cy="80" r="50" {STROKE}/>',
            "D": tombstone(),
        },
    }


def write_perceptual_figures() -> list[str]:
    """Emit the 19 perceptual sheets plus the one counting strip."""
    paths = [write(iid, sheet(bodies))
             for iid, bodies in sorted(perceptual_sheets().items())]
    paths.append(write("nmat-p1p-024", strip(strip_panels())))
    return paths


# ===========================================================================
# Figure-series frame strips
#
# The figure-series items used to narrate their frames in words inside the
# stem ("Frame 1: ... Frame 2: ..."). Each now gets one strip that draws the
# series: 300 x 300 frames in order, numbered 1..N in the house colour, so
# the picture carries the narration and the stem shrinks to the question.
# ===========================================================================
def frame_strip(frames) -> str:
    """1xN row of numbered series frames, 300 x 300 each (see ir-rot-arrow-1)."""
    n = len(frames)
    dividers = "".join(
        f'<line x1="{300 * i}" y1="0" x2="{300 * i}" y2="300"/>'
        for i in range(1, n))
    cells = "".join(
        f'<g transform="translate({300 * i} 0)">{body}'
        f'<text x="285" y="285" font-size="22" font-family="sans-serif" '
        f'text-anchor="end" fill="{AXIS}">{i + 1}</text></g>'
        for i, body in enumerate(frames))
    return _wrap(f'<g stroke="#ddd" stroke-width="2">{dividers}</g>{cells}', 300 * n, 300)


# ---------- frame primitives (300 x 300 frame-local coordinates) ----------
def frame_square() -> str:
    """The square frame most series items draw inside."""
    return (f'<rect x="40" y="40" width="220" height="220" fill="none" '
            f'stroke="{INK}" stroke-width="3"/>')


def frame_box() -> str:
    """A faint outer frame a moving figure stays inside."""
    return (f'<rect x="38" y="38" width="224" height="224" fill="none" '
            f'stroke="#ddd" stroke-width="4"/>')


def dot_row(n: int, cy: float = 150.0, r: float = 11.0, x0: float = 55.0,
            x1: float = 245.0) -> str:
    xs = [150.0] if n == 1 else [x0 + k * (x1 - x0) / (n - 1) for k in range(n)]
    return "".join(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{r}" fill="{INK}"/>'
                   for x in xs)


def dot_grid(rows: int, cols: int, r: float = 9.0, step: float = 48.0) -> str:
    w, h = (cols - 1) * step, (rows - 1) * step
    return "".join(
        f'<circle cx="{150 - w / 2 + j * step:.1f}" cy="{150 - h / 2 + i * step:.1f}" '
        f'r="{r}" fill="{INK}"/>'
        for i in range(rows) for j in range(cols))


GRID_CELLS = {"TL": (60, 60), "TR": (150, 60), "BR": (150, 150), "BL": (60, 150)}


def grid2x2(shaded=()) -> str:
    """A square split into four cells; the cells named in `shaded` are filled."""
    out = [f'<rect x="{x}" y="{y}" width="90" height="90" fill="{INK}"/>'
           for x, y in (GRID_CELLS[k] for k in shaded)]
    out.append(f'<rect x="60" y="60" width="180" height="180" fill="none" '
               f'stroke="{INK}" stroke-width="3"/>')
    out.append(f'<line x1="150" y1="60" x2="150" y2="240" stroke="{INK}" '
               f'stroke-width="3"/>')
    out.append(f'<line x1="60" y1="150" x2="240" y2="150" stroke="{INK}" '
               f'stroke-width="3"/>')
    return "".join(out)


def star_glyph(cx: float, cy: float, r_out: float = 21.0, r_in: float = 8.5) -> str:
    pts = []
    for k in range(10):
        r = r_out if k % 2 == 0 else r_in
        a = math.radians(-90 + k * 36)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{INK}"/>'


STAR_SPOTS = {
    1: [(150, 150)],
    2: [(115, 150), (185, 150)],
    3: [(95, 150), (150, 150), (205, 150)],
    4: [(112, 112), (188, 112), (112, 188), (188, 188)],
}


def circle_with_stars(count: int, shaded: bool) -> str:
    fill = "#cfcfcf" if shaded else "none"
    body = (f'<circle cx="150" cy="150" r="105" fill="{fill}" stroke="{INK}" '
            f'stroke-width="4"/>')
    return body + "".join(star_glyph(x, y) for x, y in STAR_SPOTS[count])


def corner_L(corner: str) -> str:
    """An L hugging one corner of the frame (or a small one at the centre)."""
    path = {"BL": "M60 60 V240 H240", "BR": "M240 60 V240 H60",
            "TR": "M240 240 V60 H60", "TL": "M60 240 V60 H240",
            "CENTRE": "M115 195 V115 H195"}[corner]
    return f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="10"/>'


def four_circles(arrangement: str, r: float = 26.0) -> str:
    """Four identical circles laid out in one of the series arrangements."""
    spots = {
        "row": [(55.5, 150), (118.5, 150), (181.5, 150), (244.5, 150)],
        "column": [(150, 55.5), (150, 118.5), (150, 181.5), (150, 244.5)],
        "grid2x2": [(108, 108), (192, 108), (108, 192), (192, 192)],
    }[arrangement]
    return "".join(
        f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="none" '
        f'stroke="{INK}" stroke-width="4"/>' for x, y in spots)


def concentric_squares(n: int) -> str:
    return "".join(sq(s) for s in (250, 204, 158, 112, 66, 20)[:n])


def corner_dot(corner: str) -> str:
    x, y = {"TL": (105, 105), "TR": (195, 105), "BR": (195, 195),
            "BL": (105, 195)}[corner]
    return frame_square() + f'<circle cx="{x}" cy="{y}" r="13" fill="{INK}"/>'


BLOCK_ARROW = ((150, 52), (198, 112), (172, 112), (172, 240),
               (128, 240), (128, 112), (102, 112))


def block_arrow(direction: str, solid: bool) -> str:
    """A block arrow pointing `direction`, filled solid or outline only."""
    ang = {"up": 0, "right": 90, "down": 180, "left": 270}[direction]
    pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in BLOCK_ARROW)
    style = f'fill="{INK}"' if solid else STROKE
    return (f'<g transform="rotate({ang} 150 150)">'
            f'<polygon points="{pts}" {style}/></g>')


def cell_strip(black_cell: int, white_cell: int) -> str:
    """Six numbered cells; a black dot and a white dot sit in two of them."""
    out = []
    for i in range(6):
        x = 30 + i * 40
        out.append(f'<rect x="{x}" y="110" width="40" height="80" fill="none" '
                   f'stroke="{INK}" stroke-width="3"/>')
        out.append(_txt(x + 20, 215, str(i + 1), size=13, fill="#666"))
    for cell, white in ((black_cell, False), (white_cell, True)):
        cx = 30 + (cell - 1) * 40 + 20
        out.append(
            f'<circle cx="{cx}" cy="150" r="13" fill="#fff" stroke="{INK}" '
            f'stroke-width="4"/>' if white else
            f'<circle cx="{cx}" cy="150" r="13" fill="{INK}"/>')
    return "".join(out)


def square_grid(rows: int, cols: int, side: float = 90.0, gap: float = 20.0) -> str:
    """Identical squares laid out rows x cols, centred in the frame."""
    w = cols * side + (cols - 1) * gap
    h = rows * side + (rows - 1) * gap
    return "".join(
        f'<rect x="{150 - w / 2 + j * (side + gap):.0f}" '
        f'y="{150 - h / 2 + i * (side + gap):.0f}" width="{side:.0f}" '
        f'height="{side:.0f}" {STROKE}/>'
        for i in range(rows) for j in range(cols))


def half_triangle(half: str, pointing: str, height: float, width: float) -> str:
    """A triangle centred in one half of the frame, pointing up or down."""
    cx = 90 if half == "left" else 210
    y0, y1 = 150 - height / 2, 150 + height / 2
    if pointing == "up":
        pts = ((cx, y0), (cx - width / 2, y1), (cx + width / 2, y1))
    else:
        pts = ((cx, y1), (cx - width / 2, y0), (cx + width / 2, y0))
    return (f'<line x1="150" y1="20" x2="150" y2="280" stroke="#ddd" '
            f'stroke-width="3" stroke-dasharray="8 6"/>' + _sheet_poly(pts))


# ---------- the series, frame by frame -------------------------------------
def series_frames() -> dict:
    """item id -> the frames of its series, in order."""
    solid = f'<circle cx="150" cy="150" r="100" fill="{INK}"/>'
    hollow = (f'<circle cx="150" cy="150" r="100" fill="#fff" '
              f'stroke="{INK}" stroke-width="4"/>')
    return {
        # --- part1-inductive -------------------------------------------------
        "nmat-p1i-014": [frame_square() + dot_row(n) for n in (1, 3, 5, 7)],
        "nmat-p1i-015": [solid, hollow, solid, hollow],
        "nmat-p1i-016": [poly(3, r=TRI_R), sq(SQ_SIDE), poly(5, r=TRI_R),
                         poly(6, r=TRI_R)],
        "nmat-p1i-017": [grid2x2([c]) for c in ("TL", "TR", "BR", "BL")],
        "nmat-p1i-018": [circle_with_stars(1, False), circle_with_stars(2, True),
                         circle_with_stars(3, False), circle_with_stars(4, True)],
        "nmat-p1i-019": [frame_box() + corner_L(c) for c in ("BL", "BR", "TR", "TL")],
        "nmat-p1i-020": [four_circles(a)
                         for a in ("row", "grid2x2", "column", "grid2x2")],
        "nmat-p1i-021": [concentric_squares(n) for n in (1, 2, 3, 4)],
        # --- drill/part1-inductive -------------------------------------------
        "nmat-d-p1i-011": [corner_dot(c) for c in ("TL", "TR", "BR")],
        "nmat-d-p1i-012": [dot_grid(r, c) for r, c in ((1, 2), (2, 3), (3, 4))],
        "nmat-d-p1i-013": [block_arrow("right", True), block_arrow("down", False),
                           block_arrow("left", True)],
        "nmat-d-p1i-014": [circle(125),
                           circle(125) + sq(160),
                           circle(125) + sq(160)
                           + tri((150, 95), (200, 192), (100, 192))],
        "nmat-d-p1i-015": [cell_strip(b, 7 - b) for b in (1, 2, 3)],
        "nmat-d-p1i-016": [square_grid(1, 1), square_grid(1, 2), square_grid(2, 2)],
        "nmat-d-p1i-018": [half_triangle("left", "up", 50, 46),
                           half_triangle("right", "down", 100, 88),
                           half_triangle("left", "up", 150, 116)],
    }


def write_series_strips() -> list[str]:
    """Emit every series strip; returns the figure paths in bank order."""
    return [write(iid, frame_strip(frames))
            for iid, frames in sorted(series_frames().items())]


def write_nmat_part1_figures() -> list[str]:
    """All the Part-1 inductive art: choice sheets, series strips, glyphs."""
    return (write_inductive_sheets() + write_series_strips()
            + write_series_glyph_sheets() + write_perceptual_figures())


# ===========================================================================
# Number/letter series sheets
#
# The remaining inductive items are number and letter series whose choices are
# bare numerals or letter strings. Their sheet draws each choice as a glyph,
# read straight out of the bank file, so panel and choice text can never
# disagree and the options gain a visual anchor without restating the stem.
# ===========================================================================
BANK = ROOT / "content" / "exam-bank" / "nmat"
GLYPH_ITEMS = {
    "part1-inductive.yml": [f"nmat-p1i-{n:03d}" for n in range(1, 13)],
    "drill/part1-inductive.yml": [f"nmat-d-p1i-{n:03d}" for n in range(1, 11)],
}


def numeral(text: str) -> str:
    """A choice value drawn large and centred, scaled to its length."""
    size = {1: 150, 2: 120, 3: 96, 4: 80}.get(len(text), 64)
    return (f'<text x="150" y="{150 + 0.34 * size:.0f}" font-size="{size}" '
            f'font-family="serif" text-anchor="middle">{_esc(text)}</text>')


def series_glyph_sheets() -> dict:
    """item id -> a panel per choice, each drawing that choice's own text."""
    import yaml  # only this bank-driven generator needs the bank parser

    out = {}
    for rel, ids in GLYPH_ITEMS.items():
        doc = yaml.safe_load((BANK / rel).read_text(encoding="utf-8"))
        by_id = {it["id"]: it for it in doc.get("items") or []}
        for iid in ids:
            item = by_id.get(iid)
            if item and set(item.get("choices") or {}) == set(PANEL_LABELS):
                out[iid] = {L: numeral(str(item["choices"][L]))
                            for L in PANEL_LABELS}
    return out


def write_series_glyph_sheets() -> list[str]:
    """Emit the choice-glyph sheets for the number/letter series items."""
    return [write(iid, sheet(bodies))
            for iid, bodies in sorted(series_glyph_sheets().items())]
