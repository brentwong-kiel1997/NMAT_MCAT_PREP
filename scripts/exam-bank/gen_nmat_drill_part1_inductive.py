#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/drill/part1-inductive.yml (25-item practice-only drill).

Standalone MCQs, no passages. Deeper than the main part1-inductive bank:
second-difference squares, three-way interleaving, wrap-around letter steps,
letter-plus-number pairs, double-prime series, and figure rules that combine
two moving parts (rotation plus fill, two dots crossing, opposite rotations).

Every numeric/letter series is RE-DERIVED in this file by the rule function
next to it, and the authored terms are asserted against that recomputation.
"""
import os
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part1-inductive.yml"

LETTERS = ["A", "C", "B", "D", "B", "A", "D", "C", "A", "B", "D", "C",
           "B", "A", "C", "D", "A", "B", "C", "D", "A", "C", "B", "D",
           "A"]
assert len(LETTERS) == 25
assert Counter(LETTERS) == Counter({"A": 7, "B": 6, "C": 6, "D": 6})
assert max(Counter(LETTERS).values()) <= 7

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def pos(ch):
    return ALPHA.index(ch) + 1


def lett(n):
    return ALPHA[(n - 1) % 26]


# ------------------------------------------------------- number/letter series
# (stem, terms, correct, [(wrong, note) x3], explain, rule tag)
SERIES = [
    ("What number continues the series? 2, 4, 7, 14, 17, 34, ___",
     [2, 4, 7, 14, 17, 34],
     "37",
     [("51", "Adds the two previous terms (34 + 17), a Fibonacci habit the series does not use."),
      ("68", "Doubles the last term again and skips the '+ 3' step."),
      ("71", "Applies both operations to one term: 34 x 2 + 3.")],
     "The operations alternate: x 2, then + 3. So 2, 4 (x 2), 7 (+ 3), 14 (x 2), 17 (+ 3), 34 (x 2), and 34 + 3 = 37.",
     "alternating x2 / +3"),

    ("What number continues the series? 2, 3, 7, 16, 32, ___",
     [2, 3, 7, 16, 32],
     "57",
     [("48", "Repeats the previous difference of 16 instead of taking the next square."),
      ("55", "Assumes the differences rise by a steady 7 (16 + 7 = 23)."),
      ("64", "Jumps to the next perfect square rather than adding 25 to the last term.")],
     "The gaps are the squares 1, 4, 9, 16, so the next gap is 25 and 32 + 25 = 57.",
     "second differences are squares"),

    ("What number continues the series? 6, 120, 8, 110, 10, 100, 12, ___",
     [6, 120, 8, 110, 10, 100, 12],
     "90",
     [("80", "Steps the second sub-series down by 20 instead of by 10."),
      ("95", "Halves the drop, taking 5 from 100 rather than 10."),
      ("14", "Continues the odd-position sub-series (+ 2) instead of the even one.")],
     "Two series are interleaved: the odd positions rise by 2 (6, 8, 10, 12) and the even positions fall by 10 (120, 110, 100, 90).",
     "two interleaved series"),

    ("What number continues the series? 100, 92, 85, 79, 74, ___",
     [100, 92, 85, 79, 74],
     "70",
     [("65", "Assumes the drop keeps growing and takes 9 from 74."),
      ("69", "Repeats the previous drop of 5."),
      ("71", "Uses a drop of 3, one step back in the pattern.")],
     "The drops shrink by one each time: -8, -7, -6, -5, so the next drop is 4 and 74 - 4 = 70.",
     "differences decrease by 1"),

    ("What letter continues the series? B, F, K, Q, X, ___",
     ["B", "F", "K", "Q", "X"],
     "F",
     [("E", "Counts the alphabet from zero, so the wrap lands one place early."),
      ("G", "Steps 9 past X instead of 8."),
      ("Z", "Stops at the wrap without continuing past it.")],
     "The steps grow by one: +4, +5, +6, +7. X is the 24th letter, so 24 + 8 = 32, and 32 - 26 = 6, the letter F.",
     "growing gaps with wrap-around"),

    ("What pair continues the series? A3, C6, E9, G12, ___",
     ["A3", "C6", "E9", "G12"],
     "I15",
     [("H15", "Steps the letter by one place instead of two."),
      ("I12", "Holds the number still; the number rises by 3 each frame."),
      ("J15", "Steps the letter by three places instead of two.")],
     "The letters advance two places (A, C, E, G, I) and the numbers rise by 3 (3, 6, 9, 12, 15), giving I15.",
     "letter +2 and number +3"),

    ("What number continues the series? 3, 10, 31, 94, ___",
     [3, 10, 31, 94],
     "283",
     [("282", "Multiplies by 3 but drops the '+ 1'."),
      ("279", "Subtracts 3 instead of adding 1."),
      ("376", "Multiplies by 4 instead of by 3.")],
     "Each term is three times the one before, plus 1: 3 x 3 + 1 = 10, 10 x 3 + 1 = 31, 31 x 3 + 1 = 94, 94 x 3 + 1 = 283.",
     "multiply by 3 then add 1"),

    ("What number continues the series? 4, 6, 10, 14, 22, ___",
     [4, 6, 10, 14, 22],
     "26",
     [("24", "Reads the series as ordinary consecutive even numbers."),
      ("28", "Adds the previous gap of 8 once more."),
      ("34", "Skips a prime and doubles 17 instead of 13.")],
     "Every term is twice a prime: 2 x 2, 2 x 3, 2 x 5, 2 x 7, 2 x 11, so the next is 2 x 13 = 26.",
     "twice the primes"),

    ("What number continues the series? 40, 38, 34, 28, 20, ___",
     [40, 38, 34, 28, 20],
     "10",
     [("12", "Repeats the previous drop of 8."),
      ("11", "Uses a drop of 9, halfway between the last two steps."),
      ("8", "Restarts the doubling and drops 12 from 20.")],
     "The gaps grow by two each time: -2, -4, -6, -8, so the next gap is -10 and 20 - 10 = 10.",
     "differences grow by 2"),

    ("What letter continues the series? Z, W, V, S, R, ___",
     ["Z", "W", "V", "S", "R"],
     "O",
     [("Q", "Applies the - 1 step once more instead of the - 3 step."),
      ("N", "Combines the two alternating steps into a single - 4."),
      ("L", "Applies - 3 twice, giving 18 - 3 - 3 = 12.")],
     "The steps alternate -3 and -1: Z -3 W, W -1 V, V -3 S, S -1 R, so R -3 = the 15th letter, O.",
     "alternating -3 / -1"),
]


def _alt(seed):
    """Recompute the alternating x2 / +3 series from its seed (sanity check)."""
    out = []
    a = seed
    for i in range(6):
        out.append(a)
        a = a * 2 if i % 2 == 0 else a + 3
    return out


# ------------------------------------------------------------ figure series
# (stem, correct, [(wrong, note) x3], explain)
FIG_SERIES = [
    ("Each frame is a square with a single dot placed in one of its four corners. Frame 1: the "
     "dot sits in the top-left corner. Frame 2: the top-right corner. Frame 3: the bottom-right "
     "corner. Which corner holds the dot in Frame 4?",
     "the bottom-left corner",
     [("the top-left corner", "That is where the dot began; it does not return there until Frame 5."),
      ("the top-right corner", "That follows a counter-clockwise walk, but the dot moves clockwise."),
      ("the bottom-right corner", "That is Frame 3's position, which the dot has already left.")],
     "The dot visits the corners clockwise: top-left, top-right, bottom-right, and then bottom-left."),

    ("Frame 1 shows 2 dots arranged as 1 row of 2. Frame 2 shows 6 dots arranged as 2 rows of "
     "3. Frame 3 shows 12 dots arranged as 3 rows of 4. What does Frame 4 show?",
     "20 dots arranged as 4 rows of 5",
     [("16 dots arranged as 4 rows of 4", "Squares the row count; the grid is always one column wider than it is tall."),
      ("25 dots arranged as 5 rows of 5", "Skips ahead to the next square number instead of the next rectangular grid."),
      ("12 dots arranged as 3 rows of 4", "Repeats Frame 3 instead of extending the pattern.")],
     "Frame n holds n rows of n + 1 dots, so Frame 4 holds 4 x 5 = 20 dots."),

    ("Each frame shows a single arrow. Frame 1: a solid arrow pointing right. Frame 2: a hollow "
     "arrow pointing down. Frame 3: a solid arrow pointing left. What does Frame 4 show?",
     "a hollow arrow pointing up",
     [("a solid arrow pointing up", "Gets the quarter turn but keeps Frame 3's solid fill; the fill alternates."),
      ("a hollow arrow pointing down", "Repeats Frame 2 instead of turning another quarter."),
      ("a solid arrow pointing left", "Repeats Frame 3, ignoring both the turn and the change of fill.")],
     "The direction turns 90 degrees clockwise each frame (right, down, left, up) while the fill alternates solid, hollow, solid, hollow."),

    ("Frame 1: a circle. Frame 2: a circle with a square drawn inside it. Frame 3: a circle with "
     "a square inside it and a triangle inside the square. What does Frame 4 show?",
     "a circle, a square, a triangle, and a smaller circle nested inside the triangle",
     [("a circle, a square, a triangle, and a smaller square inside the triangle",
       "Restarts the cycle with a square; the shapes repeat in the order circle, square, triangle."),
      ("a circle, a square, and a larger triangle drawn outside the square",
       "The nesting grows inward, not outward."),
      ("a circle and a square only, with the triangle removed",
       "No shape is ever removed; each frame keeps every earlier shape.")],
     "One new shape is nested inside the innermost shape each frame, cycling circle, square, triangle, circle."),

    ("A strip of six cells is numbered 1 to 6 from left to right. Frame 1: a black dot in cell 1 "
     "and a white dot in cell 6. Each frame the black dot moves one cell right and the white dot "
     "one cell left. What does Frame 4 show?",
     "the black dot in cell 4 and the white dot in cell 3",
     [("the black dot in cell 3 and the white dot in cell 4",
       "Stops the dots where they first meet in Frame 3; both keep moving."),
      ("the black dot in cell 5 and the white dot in cell 2",
       "Moves each dot two cells per frame instead of one."),
      ("the black dot in cell 4 and the white dot in cell 4",
       "Assumes the dots merge when they cross; they pass through each other.")],
     "From Frame 1 three moves take the black dot to cell 4 and the white dot to cell 3, so the two have swapped sides."),

    ("Frame 1: one small square. Frame 2: two identical squares side by side. Frame 3: four "
     "identical squares arranged 2 by 2. What does Frame 4 show?",
     "eight identical squares arranged in two rows of four",
     [("six identical squares arranged in two rows of three", "Adds two squares per frame instead of doubling."),
      ("sixteen squares arranged 4 by 4", "Squares the count instead of doubling it."),
      ("twelve squares arranged in three rows of four", "Multiplies the count by 3 instead of by 2.")],
     "The number of squares doubles each frame: 1, 2, 4, 8, and eight squares sit as two rows of four."),

    ("A circle is divided into four quadrants: north, east, south and west. Frame 1: the north "
     "quadrant is shaded and a dot sits in the east quadrant. Each frame the shaded quadrant "
     "turns one step clockwise while the dot turns one step counter-clockwise. What does Frame "
     "4 show?",
     "the west quadrant shaded and the dot in the south quadrant",
     [("the east quadrant shaded and the dot in the north quadrant",
       "That is Frame 2; both figures have moved two further steps by Frame 4."),
      ("the west quadrant shaded and the dot in the north quadrant",
       "Turns both figures the same way; they move in opposite directions."),
      ("the south quadrant shaded and the dot in the west quadrant",
       "Reads the shading as turning counter-clockwise instead of clockwise.")],
     "The shading runs N, E, S, W clockwise while the dot runs E, N, W, S counter-clockwise, so Frame 4 shades west and holds the dot in the south."),

    ("Frame 1: a small upward-pointing triangle on the left half of the frame. Each frame the "
     "triangle doubles in size and moves to the other half of the frame, and on every second "
     "frame it points downward. What does Frame 4 show?",
     "an extra-large downward-pointing triangle on the right half of the frame",
     [("an extra-large upward-pointing triangle on the right half of the frame",
       "The doubling and the move are right, but the triangle points down on every second frame."),
      ("an extra-large downward-pointing triangle on the left half of the frame",
       "Fails to swap halves; the triangle changes sides each frame."),
      ("a large upward-pointing triangle on the left half of the frame",
       "Repeats Frame 3, ignoring both the doubling and the flip.")],
     "Size doubles (small, medium, large, extra large), the half swaps each frame (left, right, left, right), and the point flips on even frames."),
]

# ---------------------------------------------------------- figure grouping
# (stem, correct figure, [(matching figure, why it belongs) x3], explain)
FIG_GROUP = [
    ("Four figures are shown: the capital letters A, B, R and P. Which letter does not belong "
     "with the other three?",
     "the capital letter B",
     [("the capital letter A", "Its counter under the crossbar encloses exactly one region, as R and P do."),
      ("the capital letter R", "Its bowl encloses exactly one region, as A and P do."),
      ("the capital letter P", "Its bowl encloses exactly one region, as A and R do.")],
     "A, R and P each enclose a single region; B encloses two, one in each of its two bowls."),

    ("Four figures are shown: an isosceles trapezoid, a parallelogram, an isosceles triangle, "
     "and a rectangle that is not a square. Which figure does not belong with the other three?",
     "the parallelogram",
     [("the isosceles trapezoid", "It has a line of symmetry between its two slanted sides."),
      ("the isosceles triangle", "It has a line of symmetry from its apex to the midpoint of its base."),
      ("the rectangle that is not a square", "It has two lines of symmetry, one through each pair of midpoints.")],
     "The trapezoid, the triangle and the rectangle all have at least one line of symmetry; a parallelogram has none and matches itself only under a half turn."),

    ("Four figures are shown: a square with a dot at the midpoint of each of its four sides, a "
     "triangle with a dot at each of its three corners, a pentagon with a dot at the midpoint of "
     "each of its five sides, and a hexagon with a dot at the midpoint of each of its six sides. "
     "Which figure does not belong with the other three?",
     "the triangle with a dot at each of its three corners",
     [("the square with dots at the midpoints of its four sides", "Its dots sit at side midpoints, as in the pentagon and the hexagon."),
      ("the pentagon with dots at the midpoints of its five sides", "Its dots also sit at side midpoints."),
      ("the hexagon with dots at the midpoints of its six sides", "Its dots also sit at side midpoints.")],
     "In the square, the pentagon and the hexagon every dot marks the midpoint of a side; the triangle puts its dots on corners."),

    ("Four figures are shown: an equilateral triangle, a square, a regular hexagon and a regular "
     "pentagon. Which figure cannot, by itself, tile a flat surface without gaps or overlaps?",
     "the regular pentagon",
     [("the equilateral triangle", "Six of them fit around a point because 6 x 60 = 360 degrees, so triangles tile."),
      ("the square", "Four of them fit around a point because 4 x 90 = 360 degrees."),
      ("the regular hexagon", "Three of them fit around a point because 3 x 120 = 360 degrees.")],
     "Tiling around a point needs an interior angle that divides 360 degrees; the pentagon's 108 degrees does not, so gaps are left over."),

    ("Four figures are shown: a circle, a figure eight (a curve crossing itself once at a single "
     "point), a square, and a triangle. Which figure does not belong with the other three?",
     "the figure eight",
     [("the circle", "A circle is a simple closed curve that never crosses itself."),
      ("the square", "A square's sides meet only at its four corners and never cross."),
      ("the triangle", "A triangle's sides meet only at its three corners and never cross.")],
     "Circle, square and triangle are simple closed curves whose outlines never cross themselves; the figure eight crosses once."),

    ("Four capital letters are shown: N, M, Z and H. Which letter does not belong with the "
     "other three?",
     "M",
     [("N", "N is drawn with three straight strokes: two verticals and one diagonal."),
      ("Z", "Z is drawn with three straight strokes: two horizontals and one diagonal."),
      ("H", "H is drawn with three straight strokes: two verticals and one crossbar.")],
     "N, Z and H each use three straight strokes; M uses four."),

    ("Four figures are shown: a square, a regular hexagon, a five-pointed star and an "
     "equilateral triangle. Which figure does not belong with the other three?",
     "the five-pointed star",
     [("the square", "Every interior angle of a square is 90 degrees, so it bulges outward everywhere."),
      ("the regular hexagon", "Its interior angles are all 120 degrees, again all under 180."),
      ("the equilateral triangle", "Its three interior angles are 60 degrees each.")],
     "Square, hexagon and triangle are convex, with no interior angle over 180 degrees; a star's inner notches are reflex angles."),
]


def build():
    pool = []
    for stem, terms, right, wrongs, explain, rel in SERIES:
        # the terms printed in the stem must be exactly the terms authored here
        import re as _re
        m = _re.search(r"\? (.*)$", stem)
        stated = [t.strip() for t in m.group(1).split(",") if t.strip() and t.strip() != "___"]
        if all(t.lstrip("-").isdigit() for t in stated):
            assert [int(t) for t in stated] == terms, (stem, stated, terms)
        else:
            assert stated == terms, (stem, stated, terms)
        if rel == "alternating x2 / +3":
            assert _alt(terms[0]) == terms, _alt(terms[0])
            assert int(right) == terms[-1] + 3, right
        elif rel == "second differences are squares":
            gaps = [terms[i + 1] - terms[i] for i in range(len(terms) - 1)]
            assert gaps == [k * k for k in range(1, len(terms))], gaps
            assert int(right) == terms[-1] + len(terms) ** 2, right
        elif rel == "two interleaved series":
            up, down = terms[0::2], terms[1::2]
            assert up == [6, 8, 10, 12] and down == [120, 110, 100], (up, down)
            assert int(right) == down[-1] - 10, right
        elif rel == "differences decrease by 1":
            gaps = [terms[i] - terms[i + 1] for i in range(len(terms) - 1)]
            assert gaps == [8, 7, 6, 5], gaps
            assert int(right) == terms[-1] - 4, right
        elif rel == "growing gaps with wrap-around":
            ps = [pos(t) for t in terms]
            for i in range(len(ps) - 1):
                assert ps[i + 1] - ps[i] == 4 + i, ps
            assert lett(pos(terms[-1]) + 8) == right, right
        elif rel == "letter +2 and number +3":
            for i, t in enumerate(terms):
                assert t[0] == ALPHA[2 * i] and int(t[1:]) == 3 * (i + 1), t
            assert right == ALPHA[2 * len(terms)] + str(3 * (len(terms) + 1)), right
        elif rel == "multiply by 3 then add 1":
            for i in range(len(terms) - 1):
                assert terms[i + 1] == 3 * terms[i] + 1, terms
            assert int(right) == 3 * terms[-1] + 1, right
        elif rel == "twice the primes":
            primes = [2, 3, 5, 7, 11, 13]
            assert terms == [2 * p for p in primes[:5]], terms
            assert int(right) == 2 * primes[5], right
        elif rel == "differences grow by 2":
            gaps = [terms[i] - terms[i + 1] for i in range(len(terms) - 1)]
            assert gaps == [2, 4, 6, 8], gaps
            assert int(right) == terms[-1] - 10, right
        elif rel == "alternating -3 / -1":
            ps = [pos(t) for t in terms]
            for i in range(len(ps) - 1):
                assert ps[i] - ps[i + 1] == (3 if i % 2 == 0 else 1), ps
            assert lett(pos(terms[-1]) - 3) == right, right
        else:
            raise AssertionError(rel)
        assert right not in [w for w, _ in wrongs]
        pool.append(dict(q=stem, right=right, wrongs=wrongs, explain=explain,
                         chapter="number-and-letter-series"))

    for stem, right, wrongs, explain in FIG_SERIES:
        pool.append(dict(q=stem, right=right, wrongs=wrongs, explain=explain,
                         chapter="figure-series"))
    for stem, right, wrongs, explain in FIG_GROUP:
        pool.append(dict(q=stem, right=right, wrongs=wrongs, explain=explain,
                         chapter="figure-grouping"))

    assert len(pool) == 25, len(pool)
    counts = Counter(p["chapter"] for p in pool)
    assert counts == Counter({"number-and-letter-series": 10,
                              "figure-series": 8, "figure-grouping": 7}), counts
    assert len({p["q"] for p in pool}) == 25, "duplicate stems"
    for p in pool:
        assert p["right"] not in [w for w, _ in p["wrongs"]]
        assert len({p["right"]} | {w for w, _ in p["wrongs"]}) == 4

    items = []
    for idx, (p, letter) in enumerate(zip(pool, LETTERS), start=1):
        wrong_letters = [L for L in "ABCD" if L != letter]
        choices, distractors = {}, {}
        choices[letter] = p["right"]
        for L, (text, note) in zip(wrong_letters, p["wrongs"]):
            choices[L] = text
            distractors[L] = note
        assert letter not in distractors
        assert len(set(choices.values())) == 4, (idx, choices)
        items.append({
            "id": "nmat-d-p1i-%03d" % idx,
            "q": " ".join(p["q"].split()),
            "choices": {L: choices[L] for L in "ABCD"},
            "answer": letter,
            "explain": p["explain"],
            "distractors": {L: distractors[L] for L in wrong_letters},
            "chapter": p["chapter"],
        })
    return {
        "exam": "nmat",
        "section": "drill-part1-inductive",
        "label": "Inductive Reasoning drill",
        "subject": "inductive-reasoning",
        "block": "part1",
        "_drill": True,
        "items": items,
    }


if __name__ == "__main__":
    data = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True,
                       width=100, default_flow_style=False)
    print("wrote", OUT, len(data["items"]), "items")
    print("chapters:", Counter(i["chapter"] for i in data["items"]))
    print("answers:", Counter(i["answer"] for i in data["items"]))
