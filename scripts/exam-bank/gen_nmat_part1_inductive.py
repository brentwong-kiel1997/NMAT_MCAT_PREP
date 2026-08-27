#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/part1-inductive.yml (30 NMAT Inductive Reasoning items).

Every option list is written [correct, w1, w2, w3]; the builder places the
correct option on the requested answer letter and the three wrong options on
the remaining letters in ascending order, so `distractors` keys are exactly
the three letters that are NOT the answer.
"""
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part1-inductive.yml"
LETTERS = "ABCD"

SERIES = "number-and-letter-series"
FIGSER = "figure-series"
FIGGRP = "figure-grouping"


def build(n, q, correct, wrongs, key, explain, chapter):
    assert key in LETTERS, key
    assert len(wrongs) == 3, (n, len(wrongs))
    choices, distractors = {}, {}
    wi = 0
    for L in LETTERS:
        if L == key:
            choices[L] = correct
        else:
            text, why = wrongs[wi]
            wi += 1
            assert text != correct, (n, "duplicate option text")
            choices[L] = text
            distractors[L] = why
    assert wi == 3 and set(distractors) == set(LETTERS) - {key}
    return {
        "id": "nmat-p1i-%03d" % n,
        "q": q,
        "choices": choices,
        "answer": key,
        "explain": explain,
        "distractors": distractors,
        "chapter": chapter,
    }


items = []

# ---------------------------------------------------------------- 1-12 series
# Planned answer letters -> A:3 B:4 C:3 D:2

# 1  arithmetic +6
items.append(build(
    1,
    "What number continues the series? 7, 13, 19, 25, 31, ___",
    "37",
    [("35", "That adds only 4; every gap in the series is 6."),
     ("39", "That adds 8 — twice the constant step."),
     ("43", "That adds 12, i.e. two steps' worth at once.")],
    "B",
    "The terms rise by a constant 6: 7, 13, 19, 25, 31, so 31 + 6 = 37.",
    SERIES))

# 2  geometric x3
items.append(build(
    2,
    "What number continues the series? 2, 6, 18, 54, 162, ___",
    "486",
    [("270", "That adds the last gap (108), treating the series as arithmetic; the gaps themselves grow by x3."),
     ("324", "That multiplies by 2, but the series has no doubling step."),
     ("1458", "That applies x3 twice and jumps two terms ahead.")],
    "C",
    "Each term is 3 times the one before: 2, 6, 18, 54, 162, so 162 x 3 = 486.",
    SERIES))

# 3  alternating +5 / -3
items.append(build(
    3,
    "What number continues the series? 4, 9, 6, 11, 8, 13, ___",
    "10",
    [("16", "That uses +3 instead of -3 — the sign of the second step is flipped."),
     ("18", "That applies the +5 step to 13; +5 belongs to the odd positions only."),
     ("4", "That restarts the block, repeating the first term (4); the series keeps alternating instead of cycling.")],
    "A",
    "The steps alternate +5 and -3: 4 (+5) 9 (-3) 6 (+5) 11 (-3) 8 (+5) 13, so the next step is -3 and 13 - 3 = 10.",
    SERIES))

# 4  interleaved: +3 leg and -2 leg
items.append(build(
    4,
    "What number continues the series? 2, 15, 5, 13, 8, 11, ___",
    "11",
    [("9", "That follows the decreasing leg (-2) — it is the eighth term, not the seventh."),
     ("14", "That adds 3 twice to 8; only one +3 step separates the odd-position terms."),
     ("13", "That adds 2, the reverse of the even leg's -2 step, to the last term.")],
    "D",
    "Two series are interleaved. Odd positions: 2, 5, 8 (adding 3). Even positions: 15, 13, 11 (subtracting 2). The seventh term belongs to the odd leg, so 8 + 3 = 11.",
    SERIES))

# 5  squares of odd numbers
items.append(build(
    5,
    "What number continues the series? 1, 9, 25, 49, 81, ___",
    "121",
    [("100", "That is 10 squared; the series squares odd numbers only, so the next base is 11."),
     ("144", "That is 12 squared, skipping 11."),
     ("169", "That is 13 squared, two bases ahead.")],
    "B",
    "The terms are the squares of the odd numbers 1, 3, 5, 7, 9, so the next term is 11 squared = 121.",
    SERIES))

# 6  cubes
items.append(build(
    6,
    "What number continues the series? 1, 8, 27, 64, 125, ___",
    "216",
    [("196", "That is 14 squared; the series runs on cubes, not squares."),
     ("206", "That uses the wrong gap: 125 + 81 = 206, whereas the gap from 5^3 to 6^3 is 91."),
     ("256", "That is 2^8 (16 squared), not 6 cubed.")],
    "C",
    "The terms are the cubes of 1, 2, 3, 4, 5, so the next term is 6 cubed = 216.",
    SERIES))

# 7  Fibonacci-style
items.append(build(
    7,
    "What number continues the series? 1, 3, 4, 7, 11, 18, ___",
    "29",
    [("25", "That adds the fourth term (7) instead of the fifth (11)."),
     ("36", "That is 18 x 2 — it doubles the last term instead of adding the term before it."),
     ("47", "That is one step too far: 18 + 29.")],
    "A",
    "From the third term on, each term is the sum of the two before it: 1 + 3 = 4, 3 + 4 = 7, 4 + 7 = 11, 7 + 11 = 18, so 11 + 18 = 29.",
    SERIES))

# 8  growing differences
items.append(build(
    8,
    "What number continues the series? 2, 3, 5, 8, 12, 17, ___",
    "23",
    [("20", "That reuses the +3 gap from the middle of the series instead of the next gap of +6."),
     ("22", "That repeats the +5 gap; the gaps grow by 1 each time, so the next is +6."),
     ("25", "That uses +8, doubling the last gap instead of adding 1 to it.")],
    "B",
    "The gaps grow by 1: +1, +2, +3, +4, +5, so the next gap is +6 and 17 + 6 = 23.",
    SERIES))

# 9  letter series, growing gaps
items.append(build(
    9,
    "What letter continues the series? B, D, G, K, P, ___",
    "V",
    [("S", "That adds 3, the smallest gap in the series, instead of the next gap of 6."),
     ("T", "That adds 4, an earlier gap, rather than 6."),
     ("U", "That adds 5, repeating the last gap; the gaps increase by 1 each step.")],
    "D",
    "Alphabet positions: B=2, D=4, G=7, K=11, P=16 — the gaps are +2, +3, +4, +5. The next gap is +6, giving position 22, which is V.",
    SERIES))

# 10  letter pairs, first forward / second backward
items.append(build(
    10,
    "What pair continues the series? AZ, BY, CX, ___",
    "DW",
    [("DV", "The first letter is right, but the second moves back only one place (X to W), not two."),
     ("EW", "That skips ahead two letters in the first position (C to E)."),
     ("DX", "That advances the first letter but leaves the second one fixed at X.")],
    "B",
    "The first letters advance A, B, C, D while the second letters retreat Z, Y, X, W, so the next pair is DW.",
    SERIES))

# 11  doubling subtractions
items.append(build(
    11,
    "What number continues the series? 100, 96, 88, 76, 60, ___",
    "40",
    [("36", "That uses the next-but-one subtraction (-24) instead of -20."),
     ("44", "That repeats the previous subtraction of 16."),
     ("48", "That subtracts 12, an earlier gap in the series.")],
    "A",
    "The subtractions grow by 4 each time: 100 - 4 = 96, 96 - 8 = 88, 88 - 12 = 76, 76 - 16 = 60, so the next subtraction is -20 and 60 - 20 = 40.",
    SERIES))

# 12  letter series, shrinking gaps downward
items.append(build(
    12,
    "What letter continues the series? Z, X, U, Q, L, ___",
    "F",
    [("G", "That steps back only 5, repeating the last gap."),
     ("H", "That steps back 4, an earlier gap in the series."),
     ("E", "That steps back 7, one place too far.")],
    "B",
    "Alphabet positions: Z=26, X=24, U=21, Q=17, L=12 — the gaps are -2, -3, -4, -5. The next gap is -6, giving position 6, which is F.",
    SERIES))

# ------------------------------------------------------- 13-21 figure series
# Planned answer letters -> A:3 B:1 C:2 D:3

# 13  rotation
items.append(build(
    13,
    "Each frame shows a square frame containing a single arrow. Frame 1: the arrow points up. "
    "Frame 2: the arrow points right. Frame 3: the arrow points down. Frame 4: the arrow points left. "
    "What does Frame 5 look like?",
    "An arrow pointing up",
    [("An arrow pointing right", "That is Frame 2's orientation; after left the arrow turns back to up."),
     ("An arrow pointing down", "That is Frame 3's orientation, two turns early."),
     ("An arrow pointing diagonally up and to the right", "The arrow turns a quarter-turn at a time; it never sits on a diagonal.")],
    "D",
    "The arrow rotates 90 degrees clockwise from frame to frame: up, right, down, left, and back to up in Frame 5.",
    FIGSER))

# 14  dots +2
items.append(build(
    14,
    "Frame 1: a square with 1 dot in the middle. Frame 2: a square with 3 dots in a horizontal row. "
    "Frame 3: a square with 5 dots in a horizontal row. Frame 4: a square with 7 dots in a horizontal row. "
    "What does Frame 5 look like?",
    "A square with 9 dots in a horizontal row",
    [("A square with 8 dots in a horizontal row", "That adds only one dot; each frame adds two."),
     ("A square with 10 dots in a horizontal row", "That adds three dots; the increase per frame is two."),
     ("A square with 12 dots in a horizontal row", "That adds five dots, overshooting the pattern.")],
    "A",
    "The dot count goes 1, 3, 5, 7 — odd numbers rising by 2 — so Frame 5 holds 9 dots.",
    FIGSER))

# 15  alternating fill
items.append(build(
    15,
    "Frame 1: a circle filled in solid black. Frame 2: a circle with a black outline and a white interior. "
    "Frame 3: a circle filled in solid black. Frame 4: a circle with a black outline and a white interior. "
    "What does Frame 5 look like?",
    "A circle filled in solid black",
    [("A circle with a black outline and a white interior", "That is Frame 4, the state the series has just left."),
     ("A circle filled in solid grey", "No grey appears anywhere in the series; only black and white are used."),
     ("A circle with a white outline and a black interior", "The outline stays black in every frame; only the fill alternates.")],
    "C",
    "The fill alternates black, white, black, white, so Frame 5 returns to a solid black circle.",
    FIGSER))

# 16  polygon side count
items.append(build(
    16,
    "Frame 1: a triangle (3 sides). Frame 2: a square (4 sides). Frame 3: a pentagon (5 sides). "
    "Frame 4: a hexagon (6 sides). What does Frame 5 look like?",
    "A heptagon (7 sides)",
    [("An octagon (8 sides)", "That skips the 7-sided figure."),
     ("A hexagon (6 sides)", "That repeats Frame 4 without adding a side."),
     ("A triangle (3 sides)", "Nothing in the series suggests restarting the cycle after only four frames.")],
    "B",
    "The number of sides increases by one each frame: 3, 4, 5, 6, so Frame 5 is a 7-sided figure, a heptagon.",
    FIGSER))

# 17  2x2 grid, clockwise shading
items.append(build(
    17,
    "A square is divided into a 2 x 2 grid of four cells. Frame 1: only the top-left cell is shaded. "
    "Frame 2: only the top-right cell is shaded. Frame 3: only the bottom-right cell is shaded. "
    "Frame 4: only the bottom-left cell is shaded. What does Frame 5 look like?",
    "Only the top-left cell is shaded",
    [("Only the top-right cell is shaded", "That is Frame 2; after the bottom-left the shading wraps around to the top-left."),
     ("Only the bottom-left cell is shaded", "That is Frame 4 unchanged; the shaded cell keeps moving."),
     ("The top-left and top-right cells are both shaded", "Exactly one cell is shaded in every frame of this series.")],
    "A",
    "The shaded cell moves clockwise: top-left, top-right, bottom-right, bottom-left, so it returns to the top-left in Frame 5.",
    FIGSER))

# 18  two changing attributes
items.append(build(
    18,
    "Frame 1: a white circle containing 1 star. Frame 2: a shaded circle containing 2 stars. "
    "Frame 3: a white circle containing 3 stars. Frame 4: a shaded circle containing 4 stars. "
    "What does Frame 5 look like?",
    "A white circle containing 5 stars",
    [("A shaded circle containing 5 stars", "The count is right, but the fill alternates, so Frame 5 must be white."),
     ("A white circle containing 6 stars", "The fill is right, but the star count rises by one, not two."),
     ("A shaded circle containing 6 stars", "Both attributes are off: the fill should be white and the count should be 5.")],
    "D",
    "Two rules run together: the star count rises 1, 2, 3, 4, 5, and the fill alternates white, shaded, white, shaded. Frame 5 is therefore a white circle with 5 stars.",
    FIGSER))

# 19  L-shape corner rotation
items.append(build(
    19,
    "Each frame shows an L-shaped figure whose right-angled corner sits in one corner of a square frame. "
    "Frame 1: the corner is at the bottom-left. Frame 2: the corner is at the bottom-right. "
    "Frame 3: the corner is at the top-right. Frame 4: the corner is at the top-left. "
    "What does Frame 5 look like?",
    "The corner is at the bottom-left",
    [("The corner is at the bottom-right", "That is Frame 2's position; the figure completes its circuit back at the bottom-left."),
     ("The corner is at the top-left", "That is Frame 4 unchanged."),
     ("The corner is at the center of the frame", "The corner always sits on the frame's edge, never in the middle.")],
    "C",
    "The figure rotates 90 degrees clockwise each frame, visiting bottom-left, bottom-right, top-right, top-left, and returning to bottom-left.",
    FIGSER))

# 20  arrangement cycle
items.append(build(
    20,
    "Each frame shows four identical small circles. Frame 1: the circles lie in a horizontal row. "
    "Frame 2: the circles form a 2 x 2 square. Frame 3: the circles lie in a vertical column. "
    "Frame 4: the circles form a 2 x 2 square. What does Frame 5 look like?",
    "The circles lie in a horizontal row",
    [("The circles form a 2 x 2 square", "That is Frame 4; the 2 x 2 square appears only between the row and the column."),
     ("The circles lie in a vertical column", "That is Frame 3's arrangement, two frames back."),
     ("Three circles lie in a row with the fourth floating above them", "All four circles keep one symmetric arrangement; none is ever set apart.")],
    "D",
    "The arrangement cycles row, 2 x 2 square, column, 2 x 2 square, so Frame 5 returns to a horizontal row.",
    FIGSER))

# 21  concentric squares
items.append(build(
    21,
    "Frame 1: one square. Frame 2: two concentric squares, one inside the other. Frame 3: three concentric squares. "
    "Frame 4: four concentric squares. What does Frame 5 look like?",
    "Five concentric squares",
    [("Six concentric squares", "That skips the fifth layer."),
     ("Four concentric squares", "That leaves the figure unchanged from Frame 4."),
     ("Five concentric circles", "The figures are squares throughout, not circles.")],
    "A",
    "One nested layer is added per frame: 1, 2, 3, 4, so Frame 5 shows five concentric squares.",
    FIGSER))

# ------------------------------------------------------- 22-30 figure grouping
# Planned answer letters -> A:2 B:2 C:3 D:2

# 22  regular polygons
items.append(build(
    22,
    "Four figures are shown. A. an equilateral triangle; B. a square; C. a regular pentagon; D. a right triangle. "
    "Which figure does not belong with the other three?",
    "D — the right triangle",
    [("A — the equilateral triangle", "It belongs: all three of its sides and angles are equal, like the square and the regular pentagon."),
     ("B — the square", "It belongs; having four sides is not what separates the odd figure — equal sides and angles is."),
     ("C — the regular pentagon", "It belongs; it has the most sides, but side count is not the grouping property here.")],
    "D",
    "A, B and C are regular polygons: every side and every angle is equal. A right triangle has unequal sides and one 90-degree angle, so it is the outsider.",
    FIGGRP))

# 23  vertical mirror symmetry in letters
items.append(build(
    23,
    "Four capital letters are shown. A. N; B. H; C. M; D. A. Which letter does not belong with the other three?",
    "A — N",
    [("B — H", "H belongs: it is symmetric about a vertical mirror line (and a horizontal one too)."),
     ("C — M", "M belongs: its left and right halves mirror each other."),
     ("D — A", "A belongs: a vertical line through its apex divides it into mirror halves.")],
    "A",
    "H, M and A each have a vertical mirror line. N has none — it matches itself only under a 180-degree rotation — so it is the outsider.",
    FIGGRP))

# 24  straight-sided vs curved
items.append(build(
    24,
    "Four figures are shown. A. a rectangle; B. a triangle; C. a circle; D. a square. "
    "Which figure does not belong with the other three?",
    "C — the circle",
    [("A — the rectangle", "It belongs: it is closed by four straight sides and has four corners."),
     ("B — the triangle", "It belongs; having the fewest sides does not set it apart — it is still a straight-sided figure with corners."),
     ("D — the square", "It belongs: four equal straight sides and four corners, like the rectangle and the triangle.")],
    "C",
    "The rectangle, triangle and square are polygons bounded by straight sides meeting at corners. A circle is one continuous curved line with no corners.",
    FIGGRP))

# 25  number of enclosed regions
items.append(build(
    25,
    "Four figures are shown. A. a rectangle with one vertical line drawn down its middle; "
    "B. a triangle with nothing drawn inside it; C. a square with one diagonal drawn; "
    "D. a circle with one diameter drawn. Which figure does not belong with the other three?",
    "B — the plain triangle",
    [("A — the split rectangle", "It belongs: the single line divides it into exactly two enclosed regions."),
     ("C — the square with a diagonal", "It belongs: the diagonal cuts it into two triangular regions."),
     ("D — the circle with a diameter", "It belongs: the diameter splits it into two half-disc regions.")],
    "B",
    "A, C and D are each divided by a single line into two enclosed regions. The plain triangle is one undivided region.",
    FIGGRP))

# 26  dot placement symmetry
items.append(build(
    26,
    "Four figures are shown. A. a square with a dot at each of its four corners; "
    "B. a circle with four dots spaced evenly around its edge; C. an equilateral triangle with a dot at each of its three corners; "
    "D. a square with all four dots placed side by side along its bottom edge. Which figure does not belong with the other three?",
    "D — the square with all four dots along its bottom edge",
    [("A — the square with corner dots", "It belongs: the four dots sit symmetrically at the corners."),
     ("B — the circle with evenly spaced dots", "It belongs: the dots are spread evenly around the figure."),
     ("C — the triangle with dots at its corners", "It belongs; it has three dots rather than four, but every dot still sits at a vertex, so the placement is symmetric — the count is not what separates the odd figure.")],
    "D",
    "In A, B and C the dots are distributed symmetrically about the figure. In D all four dots are crowded along one edge, so the arrangement has no symmetry.",
    FIGGRP))

# 27  even vs odd side count
items.append(build(
    27,
    "Four figures are shown. A. a hexagon (6 sides); B. a square (4 sides); C. a pentagon (5 sides); D. an octagon (8 sides). "
    "Which figure does not belong with the other three?",
    "C — the pentagon",
    [("A — the hexagon", "It belongs: 6 is an even number of sides, like 4 and 8."),
     ("B — the square", "It belongs: 4 is even."),
     ("D — the octagon", "It belongs: 8 is even.")],
    "C",
    "The square, hexagon and octagon all have an even number of sides (4, 6, 8). The pentagon has 5, which is odd.",
    FIGGRP))

# 28  open vs closed figures
items.append(build(
    28,
    "Four figures are shown. A. the capital letter U; B. a triangle; C. a circle; D. a square. "
    "Which figure does not belong with the other three?",
    "A — the letter U",
    [("B — the triangle", "It belongs: its three sides close around an interior region."),
     ("C — the circle", "It belongs: the curve closes on itself and encloses a region."),
     ("D — the square", "It belongs: its four sides form a closed boundary.")],
    "A",
    "The triangle, circle and square are closed figures enclosing an interior. The letter U is an open curve whose two ends never meet.",
    FIGGRP))

# 29  lines of symmetry
items.append(build(
    29,
    "Four figures are shown. A. a rectangle; B. a scalene triangle; C. an isosceles triangle; D. a regular pentagon. "
    "Which figure does not belong with the other three?",
    "B — the scalene triangle",
    [("A — the rectangle", "It belongs: it has two lines of symmetry, one through each pair of midpoints."),
     ("C — the isosceles triangle", "It belongs: a vertical line through its apex and base midpoint mirrors it onto itself."),
     ("D — the regular pentagon", "It belongs: five lines of symmetry, one through each vertex.")],
    "B",
    "The rectangle, isosceles triangle and regular pentagon each have at least one line of symmetry. A scalene triangle has three unequal sides and no line of symmetry at all.",
    FIGGRP))

# 30  shared inner count
items.append(build(
    30,
    "Four figures are shown. A. a triangle containing 3 dots; B. a square containing 3 dots; "
    "C. a pentagon containing 4 dots; D. a circle containing 3 dots. Which figure does not belong with the other three?",
    "C — the pentagon with 4 dots",
    [("A — the triangle with 3 dots", "It belongs; its outline is a triangle while the others are a square and a circle, but the outer shape varies across the whole set — the dot count is the shared property."),
     ("B — the square with 3 dots", "It belongs: three dots inside, like the triangle and the circle."),
     ("D — the circle with 3 dots", "It belongs: three dots inside.")],
    "C",
    "A, B and D each contain exactly three dots, whatever their outline. C contains four, so it is the outsider.",
    FIGGRP))

# ------------------------------------------------------------------ assemble
doc = {
    "exam": "nmat",
    "section": "part1-inductive",
    "label": "Inductive Reasoning",
    "subject": "inductive-reasoning",
    "block": "part1",
    "items_expected": len(items),
    "items": items,
    "passages": [],
}
assert doc["items_expected"] == 30, doc["items_expected"]

with open(OUT, "w") as fh:
    yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True, width=100)

print("wrote", OUT)
print("answers:", dict(sorted(Counter(i["answer"] for i in items).items())))
print("chapters:", dict(Counter(i["chapter"] for i in items)))
