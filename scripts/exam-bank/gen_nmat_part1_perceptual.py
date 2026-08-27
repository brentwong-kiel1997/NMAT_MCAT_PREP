#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/part1-perceptual.yml (30-item NMAT Perceptual bank).

10 mirror-image + 10 identical-information + 10 hidden-figure items. Every string
comparison and every mirror transformation is asserted programmatically below
before the YAML is dumped, so the keys cannot drift from the content.
"""
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part1-perceptual.yml"

# --------------------------------------------------------------------------
# helpers for character-by-character verification
# --------------------------------------------------------------------------

def first_diff(a, b):
    """(index, char_in_a, char_in_b) of the first mismatch, scanning left to right."""
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return (i, x, y)
    n = min(len(a), len(b))
    return (n, None, None)


# --- mirror alphabet facts (vertical mirror = left-right; horizontal = up-down) ---
LR = {"b": "d", "d": "b", "p": "q", "q": "p"}   # vertical mirror
UD = {"b": "p", "p": "b", "d": "q", "q": "d"}   # water image
ROT = {"b": "q", "q": "b", "d": "p", "p": "d"}  # 180-degree rotation
for k in LR:
    assert UD[ROT[k]] == LR[k], "transform tables inconsistent"


def flip_word_lr(word):
    """True mirror of a lowercase word: each letter flipped AND order reversed."""
    return "".join(LR.get(c, c) for c in reversed(word))


# --------------------------------------------------------------------------
# items
# --------------------------------------------------------------------------
ITEMS = []
let = {"A": 0, "B": 0, "C": 0, "D": 0}


def add(n, q, correct, wrong, ans, explain, chapter):
    """wrong: {letter: (option_text, distractor_note)} for the 3 non-answer letters."""
    assert chapter in ("mirror-image", "hidden-figure", "identical-information")
    assert ans in ("A", "B", "C", "D")
    assert set(wrong) == set("ABCD") - {ans}, f"item {n}: distractor keys {sorted(wrong)}"
    choices = {ans: correct}
    distractors = {}
    for k, (text, note) in wrong.items():
        choices[k] = text
        distractors[k] = note
    ITEMS.append({
        "id": f"nmat-p1p-{n:03d}",
        "q": q,
        "choices": choices,
        "answer": ans,
        "explain": explain,
        "distractors": distractors,
        "chapter": chapter,
    })
    let[ans] += 1


# ============================ MIRROR IMAGE (1-10) ==========================

# 1 ------------------------------------------------------------------
add(1,
    "Which lowercase letter looks exactly the same after a left-right flip in a vertical mirror?",
    "m",
    {"A": ("b", "b reflected left-right becomes d."),
     "B": ("d", "d reflected left-right becomes b."),
     "D": ("p", "p reflected left-right becomes q.")},
    "C",
    "m is symmetric about its own vertical axis, so a left-right reflection leaves it unchanged; "
    "b, d and p all carry their asymmetry on one side.",
    "mirror-image")

# 2 ------------------------------------------------------------------
assert flip_word_lr("pod") == "boq"
add(2,
    "Convention: a vertical mirror flips each lowercase letter left-to-right and also reverses the "
    "letter order, exactly as a real mirror does. Reflected this way, the word 'pod' appears as:",
    "boq",
    {"B": ("qob", "qob flips each letter correctly but forgets that a mirror also reverses the "
                 "letter order."),
     "C": ("bod", "bod flips the p as if by an up-down (water-image) flip and leaves the d "
                  "unflipped."),
     "D": ("qod", "qod flips the p correctly but leaves the d unflipped; a vertical mirror turns "
                  "d into b.")},
    "A",
    "Reading the image from the left you meet the original right-hand letters first: d becomes b, "
    "o stays o, p becomes q - 'boq'.",
    "mirror-image")

# 3 ------------------------------------------------------------------
assert ROT["b"] == "q" and ROT["d"] == "p"
add(3,
    "A strip of paper printed with the lowercase letters 'bd' is rotated 180 degrees in the plane. "
    "What does the strip read afterwards?",
    "pq",
    {"A": ("qp", "qp rotates both letter shapes correctly but does not reverse their left-to-right "
                 "order."),
     "C": ("db", "db leaves both letter shapes unrotated."),
     "D": ("qb", "qb merely swaps the two letters' positions without rotating either shape.")},
    "B",
    "A 180-degree turn sends b to q and d to p, and it reverses the order of the letters as well, "
    "so the strip reads p then q.",
    "mirror-image")

# 4 ------------------------------------------------------------------
assert UD["d"] == "q"
add(4,
    "Turned upside down as in a water image (an up-down flip), the lowercase letter 'd' becomes:",
    "q",
    {"A": ("b", "b is d's left-right mirror image, not its up-down flip."),
     "B": ("p", "p is what you get by rotating d through 180 degrees."),
     "D": ("d", "d has no horizontal axis of symmetry, so it cannot survive this flip unchanged.")},
    "C",
    "An up-down reflection maps d to q (and b to p): the ascending stem now descends below the "
    "baseline while the bowl stays on the same side.",
    "mirror-image")

# 5 ------------------------------------------------------------------
add(5,
    "Which word still reads the same, letter for letter, after reflection in a vertical mirror "
    "(each letter flipped left-to-right and the order reversed)?",
    "MOM",
    {"B": ("DAD", "D is not left-right symmetric - it flips into a backwards D."),
     "C": ("NOON", "N has no vertical mirror symmetry; it turns into a backwards N."),
     "D": ("EYE", "E is not left-right symmetric: its spine sits on the left and would move to "
                  "the right.")},
    "A",
    "M and O are both symmetric about a vertical axis, and MOM is a palindrome, so the reversal of "
    "letter order changes nothing.",
    "mirror-image")

# 6 ------------------------------------------------------------------
add(6,
    "Which capital letter is symmetric about BOTH a vertical mirror and a horizontal mirror?",
    "H",
    {"A": ("N", "N has 180-degree rotational symmetry but no mirror symmetry about either axis."),
     "B": ("C", "C survives only an up-down flip; a left-right flip turns it into a backwards C."),
     "C": ("M", "M survives only a left-right flip; an up-down flip turns it into a W-like shape.")},
    "D",
    "H is unchanged by a left-right flip and by an up-down flip, the only option carrying both "
    "mirror symmetries.",
    "mirror-image")

# 7 ------------------------------------------------------------------
add(7,
    "An arrow points up and to the right. Held in front of a vertical mirror, the image arrow points:",
    "up and to the left",
    {"A": ("down and to the right", "That keeps the rightward direction unchanged, but the "
                                    "horizontal component is exactly what a vertical mirror flips."),
     "C": ("down and to the left", "That is a 180-degree rotation of the arrow, not a left-right "
                                   "reflection."),
     "D": ("up and to the right", "That is the object itself; the image must at least swap left "
                                  "and right.")},
    "B",
    "A vertical mirror swaps left and right and leaves up and down alone, so up-right becomes "
    "up-left.",
    "mirror-image")

# 8 ------------------------------------------------------------------
assert LR["b"] == "d"
add(8,
    "Which pair of lowercase letters are left-right mirror images of each other - each becoming the "
    "other in a vertical mirror?",
    "b and d",
    {"A": ("p and d", "p and d are 180-degree rotations of each other."),
     "B": ("q and b", "q and b are 180-degree rotations of each other."),
     "C": ("n and u", "n and u swap under an up-down (water-image) flip, not a left-right one.")},
    "D",
    "A vertical mirror moves the bowl to the other side of the stem: b to d, d to b, and likewise "
    "p to q.",
    "mirror-image")

# 9 ------------------------------------------------------------------
add(9,
    "A capital L - a vertical stroke with a horizontal foot extending to the right at its bottom - "
    "is reflected in a vertical mirror. The image is:",
    "a vertical stroke with its foot extending to the left at the bottom",
    {"B": ("a vertical stroke with its foot extending to the right at the top",
           "That is an up-down (water-image) flip: the foot moved to the top instead of switching "
           "sides."),
     "C": ("the same L, unchanged",
           "L is not symmetric left-to-right; its foot must switch sides in the image."),
     "D": ("a vertical stroke with its foot extending to the left at the top",
           "That is a 180-degree rotation: the foot changed both its side and its end.")},
    "A",
    "Left and right swap, so the foot now points left; up and down are untouched, so the foot stays "
    "at the bottom.",
    "mirror-image")

# 10 -----------------------------------------------------------------
add(10,
    "Which word is made only of capital letters that are unchanged by a left-right (vertical-mirror) "
    "flip?",
    "TOMATO",
    {"A": ("DAMAGE", "The D and the E have no vertical symmetry - D flips into a backwards D."),
     "B": ("PIXEL", "The P and the E both flip into backwards versions of themselves."),
     "D": ("CHOICE", "The C and the E are not left-right symmetric.")},
    "C",
    "T, O, M and A all have vertical mirror symmetry, so TOMATO shows the same letters after the "
    "flip.",
    "mirror-image")

# ====================== IDENTICAL INFORMATION (11-20) ======================

# 11 -----------------------------------------------------------------
s1, s2 = "TR-55831-QB", "TR-5583I-QB"
assert len(s1) == len(s2) == 11 and first_diff(s1, s2) == (7, "1", "I")
add(11,
    "Two inventory codes are read aloud for checking: 'TR-55831-QB' and 'TR-5583I-QB'. They are:",
    "different - the eighth character is the digit 1 in one code and the capital letter I in the "
    "other",
    {"A": ("identical",
           "The two codes are not identical: character 8 is the digit 1 in the first and the "
           "capital letter I in the second."),
     "C": ("different - a zero has been typed for the letter O",
           "Neither code contains a zero or a letter O; the trap in these strings is 1 versus I."),
     "D": ("different - a character has been left out of one code",
           "Both codes are 11 characters long; nothing is missing.")},
    "B",
    "Character 8 is the digit 1 in the first code and the capital letter I in the second; every "
    "other position matches.",
    "identical-information")

# 12 -----------------------------------------------------------------
t = "MARBELLA-0417-CP"
o = {"A": "MARBELLA-0417-CP", "B": "MARBELLA-O417-CP", "C": "MARBELA-0417-CP",
     "D": "MARBELLA-0417-GP"}
assert o["A"] == t and first_diff(t, o["B"]) == (9, "0", "O")
assert first_diff(t, o["C"]) == (6, "L", "A") and len(o["C"]) == len(t) - 1
assert first_diff(t, o["D"]) == (14, "C", "G")
add(12,
    "Target: MARBELLA-0417-CP. Which option is an exact character-for-character match for the "
    "target?",
    "MARBELLA-0417-CP",
    {"B": ("MARBELLA-O417-CP", "Its second block opens with the letter O instead of the digit 0 "
                               "(O417, not 0417)."),
     "C": ("MARBELA-0417-CP", "It drops one L, spelling MARBELA."),
     "D": ("MARBELLA-0417-GP", "Its final letter is G, not C (GP, not CP).")},
    "A",
    "Option A repeats the target exactly: MARBELLA, hyphen, 0417, hyphen, CP.",
    "identical-information")

# 13 -----------------------------------------------------------------
P = "Delos Santos, Maria Corazon A."
Q = "Delos Santos, Maria Corrazon A."
R = "Delos Santos, Maria Corazon A."
S = "De Los Santos, Maria Corazon A."
assert P == R and first_diff(P, Q) == (23, "a", "r") and first_diff(P, S) == (2, "l", " ")
add(13,
    "Four name entries are listed. P: 'Delos Santos, Maria Corazon A.'  Q: 'Delos Santos, Maria "
    "Corrazon A.'  R: 'Delos Santos, Maria Corazon A.'  S: 'De Los Santos, Maria Corazon A.'  "
    "Which pair is identical?",
    "P and R",
    {"A": ("P and Q", "Q spells the middle name 'Corrazon' with a doubled r."),
     "B": ("P and S", "S writes 'De Los Santos' instead of 'Delos Santos'."),
     "D": ("Q and R", "Q carries the doubled r in the middle name, so it differs from R too.")},
    "C",
    "P and R are character-for-character the same; Q doubles the r in Corazon and S splits Delos "
    "into two words.",
    "identical-information")

# 14 -----------------------------------------------------------------
a1, a2 = "4O71-BRN-09", "4071-BRN-09"
assert len(a1) == len(a2) == 11 and first_diff(a1, a2) == (1, "O", "0")
add(14,
    "Compare these two serial numbers: '4O71-BRN-09' and '4071-BRN-09'. They are:",
    "different - the second character is the letter O in one and the digit 0 in the other",
    {"A": ("identical", "They differ at character 2: a capital O against a zero."),
     "B": ("different - one serial is one character longer than the other",
           "Both serials are 11 characters long; nothing was added or dropped."),
     "C": ("different - the final block differs", "Both end in '-09'; the mismatch is up front.")},
    "D",
    "Character 2 is a capital O in the first serial and a zero in the second; the remaining ten "
    "characters match.",
    "identical-information")

# 15 -----------------------------------------------------------------
r1 = "Account 88-4012-B: Variable Rate 6.125%"
r2 = "Account 88-4012-B: Variable Rate 6.152%"
i, x, y = first_diff(r1, r2)
assert len(r1) == len(r2) and r1[:i] == "Account 88-4012-B: Variable Rate 6.1" and (x, y) == ("2", "5")
add(15,
    "Two ledger lines are compared: 'Account 88-4012-B: Variable Rate 6.125%' and 'Account "
    "88-4012-B: Variable Rate 6.152%'. They are:",
    "different - the last three digits of the rate are transposed (125 against 152)",
    {"A": ("identical", "The lines differ inside the rate: 6.125% against 6.152%."),
     "C": ("different - the account number differs",
           "Both lines read 'Account 88-4012-B' identically."),
     "D": ("different - the two lines differ in capitalization",
           "Every letter matches case for case; only digits differ.")},
    "B",
    "Account number, label and capitalization all match; only the rate differs, 6.125% against "
    "6.152% - the last two digits have been swapped.",
    "identical-information")

# 16 -----------------------------------------------------------------
t = "1I7-lI7-771"
o = {"A": "lI7-lI7-771", "B": "1I7-l17-771", "C": "1I7-lI7-771", "D": "1I7-lI7-77l"}
assert o["C"] == t and first_diff(t, o["A"]) == (0, "1", "l")
assert first_diff(t, o["B"]) == (5, "I", "1") and first_diff(t, o["D"]) == (10, "1", "l")
add(16,
    "Target: 1I7-lI7-771. Which option is an exact character-for-character match for the target?",
    "1I7-lI7-771",
    {"A": ("lI7-lI7-771", "Its first character is a lowercase l instead of the digit 1."),
     "B": ("1I7-l17-771", "Its second block reads l17 - the capital I has become the digit 1."),
     "D": ("1I7-lI7-77l", "Its last character is a lowercase l instead of the digit 1.")},
    "C",
    "Option C reproduces the target exactly: digit 1, capital I, 7, hyphen, lowercase l, capital I, "
    "7, hyphen, 7, 7, digit 1.",
    "identical-information")

# 17 -----------------------------------------------------------------
P = "12-B Mabini St., Brgy. San Roque, QC 1109"
Q = "12-B Mabini St., Brgy. San Roque, QC 1109"
R = "12-B Mabini St., Brgy. San Rogue, QC 1109"
S = "12-B Mabini St, Brgy. San Roque, QC 1109"
assert P == Q and first_diff(P, R) == (29, "q", "g") and first_diff(P, S) == (14, ".", ",")
add(17,
    "Four address lines are listed. P: '12-B Mabini St., Brgy. San Roque, QC 1109'  Q: '12-B "
    "Mabini St., Brgy. San Roque, QC 1109'  R: '12-B Mabini St., Brgy. San Rogue, QC 1109'  S: "
    "'12-B Mabini St, Brgy. San Roque, QC 1109'  Which pair is identical?",
    "P and Q",
    {"B": ("P and R", "R reads 'San Rogue' rather than 'San Roque'."),
     "C": ("R and S", "R carries the Rogue misspelling and S drops the period after 'St'."),
     "D": ("Q and S", "S is missing the period after 'St'.")},
    "A",
    "P and Q are character-for-character the same; R misspells Roque as Rogue and S drops the "
    "period after 'St'.",
    "identical-information")

# 18 -----------------------------------------------------------------
t = "REF 2027-NC-004518-B / DUE 30 SEP"
o = {"A": "REF 2027-NC-004518-8 / DUE 30 SEP",
     "B": "REF 2027-NC-00451 8-B / DUE 30 SEP",
     "C": "REF 2027-NC-004518-B / DUE 39 SEP",
     "D": "REF 2027-NC-004518-B / DUE 30 SEP"}
assert o["D"] == t and first_diff(t, o["A"]) == (19, "B", "8")
assert first_diff(t, o["B"]) == (17, "8", " ") and first_diff(t, o["C"]) == (28, "0", "9")
add(18,
    "Target: REF 2027-NC-004518-B / DUE 30 SEP. Which option is an exact character-for-character "
    "match for the target?",
    "REF 2027-NC-004518-B / DUE 30 SEP",
    {"A": ("REF 2027-NC-004518-8 / DUE 30 SEP",
           "The reference ends in the digit 8 instead of the letter B."),
     "B": ("REF 2027-NC-00451 8-B / DUE 30 SEP",
           "An extra space has crept into the reference: '00451 8-B'."),
     "C": ("REF 2027-NC-004518-B / DUE 39 SEP", "The due day reads 39 instead of 30.")},
    "D",
    "Option D reproduces the reference, the slash and the due date exactly, with single spaces "
    "throughout.",
    "identical-information")

# 19 -----------------------------------------------------------------
t = "4821 9037 5566 1204"
o = {"A": "4821 9037 5566 1204", "B": "4821 9073 5566 1204", "C": "4821 9037 5666 1204",
     "D": "4821 9037 5566 12O4"}
assert o["A"] == t and first_diff(t, o["B"]) == (7, "3", "7")
assert first_diff(t, o["C"]) == (11, "5", "6") and first_diff(t, o["D"]) == (17, "0", "O")
add(19,
    "Target: 4821 9037 5566 1204. Which option is an exact character-for-character match for the "
    "target?",
    "4821 9037 5566 1204",
    {"B": ("4821 9073 5566 1204", "Its second block reads 9073 - the 3 and the 7 have been swapped."),
     "C": ("4821 9037 5666 1204", "Its third block reads 5666 instead of 5566."),
     "D": ("4821 9037 5566 12O4", "Its final block uses the letter O in place of the zero (12O4).")},
    "A",
    "Option A reproduces all four four-digit blocks and the three separating spaces exactly.",
    "identical-information")

# 20 -----------------------------------------------------------------
P = "0917 553 8821"
Q = "0917 553 8821"
R = "0917 5538 821"
S = "0917 553 8827"
assert P == Q and first_diff(P, R) == (8, " ", "8") and first_diff(P, S) == (12, "1", "7")
add(20,
    "Four contact numbers are listed. P: '0917 553 8821'  Q: '0917 553 8821'  R: '0917 5538 821'  "
    "S: '0917 553 8827'  Which pair is identical?",
    "P and Q",
    {"A": ("P and R", "R inserts a space after 553, so it is not identical to P even though the "
                      "digits run in the same order."),
     "B": ("Q and S", "S ends in 8827, not 8821."),
     "D": ("R and S", "R is regrouped and S ends in 8827, so the two differ from each other as "
                      "well.")},
    "C",
    "P and Q are character-for-character the same; R regroups the digits with an extra space and S "
    "ends in 8827.",
    "identical-information")

# ========================= HIDDEN FIGURE (21-30) ===========================

add(21,
    "Target outline: a circle with a single straight line drawn through its center from top to "
    "bottom (a vertical diameter). Each panel is described in words. Which panel contains the "
    "target?",
    "A circle with a single vertical line through its center, partly crossed by two overlapping "
    "squares",
    {"A": ("A circle with a single horizontal line through its center, beside two small triangles",
           "The line inside its circle runs horizontally, not top to bottom."),
     "C": ("An ellipse (a flattened oval) with a single vertical line through its center",
           "Its outline is an ellipse, not a circle."),
     "D": ("A square with a single vertical line through its center",
           "Its outline is a square, not a circle.")},
    "B",
    "Only this panel pairs a circular outline with a top-to-bottom line through the middle; the two "
    "squares are extra clutter that does not erase the target.",
    "hidden-figure")

add(22,
    "Target outline: a plus sign - one horizontal and one vertical stroke crossing exactly at their "
    "midpoints. Which panel contains it?",
    "One horizontal and one vertical stroke crossing at their midpoints, drawn over a zigzag line",
    {"A": ("Two diagonal strokes crossing at their midpoints, surrounded by four circles",
           "Its two strokes are diagonal, forming an X rather than an upright plus."),
     "B": ("A vertical stroke meeting the end of a horizontal stroke, beside two triangles",
           "Its strokes meet end to end in an L shape; neither crosses the other."),
     "D": ("One vertical stroke touching two parallel horizontal strokes without crossing either",
           "Its strokes touch but do not cross, so no midpoint intersection is formed.")},
    "C",
    "Only this panel has a horizontal and a vertical stroke that cross at their midpoints, with the "
    "zigzag merely clutter around them.",
    "hidden-figure")

add(23,
    "Target outline: a five-pointed star. Which panel contains it?",
    "A five-pointed star drawn over three overlapping rectangles",
    {"B": ("A six-pointed star formed by two overlapping triangles",
           "That star has six points, not five."),
     "C": ("A four-pointed star inside a circle", "That star has only four points."),
     "D": ("A plain five-sided pentagon with no inner lines",
           "A pentagon is a five-sided outline, not a five-pointed star.")},
    "A",
    "The rectangles are clutter; the five-pointed star is present underneath them, while the other "
    "panels hold stars with the wrong number of points or none at all.",
    "hidden-figure")

add(24,
    "Five panels are described left to right. (1) a circle drawn inside a triangle. (2) a triangle "
    "drawn inside a circle. (3) a circle drawn inside a square. (4) a circle drawn inside a "
    "triangle, with a small square in one corner. (5) two circles drawn inside a square. How many "
    "panels contain a circle drawn inside a triangle?",
    "2",
    {"A": ("1", "That counts only panel 1; panel 4 still holds a circle inside a triangle even with "
                "the extra square."),
     "B": ("3", "That adds a panel whose circle is not inside a triangle - panel 2 is a triangle "
                "inside a circle and panel 3 puts the circle inside a square."),
     "C": ("4", "That counts nearly every panel showing a circle, ignoring what surrounds it.")},
    "D",
    "Panels 1 and 4 each show a circle inside a triangle; panel 2 reverses the arrangement, panel 3 "
    "uses a square, and panel 5 has no triangle.",
    "hidden-figure")

add(25,
    "Target outline: a rectangle divided into two equal parts by a vertical line through its "
    "midpoint. Which panel does NOT contain the target?",
    "A rectangle with a horizontal line through its midpoint",
    {"A": ("A rectangle with a vertical line through its midpoint and a small circle in the "
           "lower-left corner",
           "The circle is extra clutter; the rectangle is still split by a vertical midline."),
     "C": ("A rectangle with a vertical line through its midpoint and one diagonal added",
           "The diagonal is clutter; the vertical midline of the target is still there."),
     "D": ("A plain rectangle with a vertical line through its midpoint",
           "That is the target drawn on its own, with no extra lines at all.")},
    "B",
    "Its dividing line runs horizontally, so it splits the rectangle top and bottom rather than "
    "left and right.",
    "hidden-figure")

add(26,
    "Target outline: two straight strokes joined end to end at a right angle (an L shape). Which "
    "panel contains it?",
    "Two strokes joined end to end at a right angle, partly hidden by a shaded circle",
    {"A": ("Two strokes crossing at their midpoints to form four right angles",
           "Its strokes cross at their midpoints instead of being joined end to end."),
     "B": ("Two strokes joined end to end at a 45-degree angle",
           "The angle between its strokes is 45 degrees, not 90."),
     "D": ("Two parallel strokes lying side by side without touching",
           "Its strokes never meet, so no corner is formed at all.")},
    "C",
    "The shaded circle is clutter laid over the target; the two strokes beneath it are still joined "
    "end to end at 90 degrees.",
    "hidden-figure")

add(27,
    "Target outline: an upward arrow - a vertical shaft with two slanted strokes rising to a single "
    "point at the top of the shaft. Which panel contains it?",
    "A vertical shaft with two slanted strokes meeting in a point at its top, drawn across a field "
    "of small circles",
    {"B": ("A vertical shaft with two slanted strokes meeting in a point at its bottom",
           "Its arrowhead sits at the bottom of the shaft, so the arrow points down."),
     "C": ("A vertical shaft with a horizontal bar across its top",
           "Its top is capped by a flat bar; the two slanted strokes of the arrowhead are missing."),
     "D": ("A vertical shaft with two slanted strokes forming a V that opens upward at its top",
           "Its top strokes form a cup that opens upward, with no point at the top.")},
    "A",
    "The field of small circles is clutter; the shaft below it still carries two slanted strokes "
    "meeting in a point at the top.",
    "hidden-figure")

add(28,
    "Target outline: a capital letter A - two slanted strokes meeting at a top point with a "
    "horizontal crossbar between them. Which panel contains it?",
    "Two slanted strokes meeting at a point at the top with a horizontal crossbar between them, "
    "printed inside a bordered box",
    {"A": ("Two vertical strokes joined by a crossbar in the middle, among other letters",
           "That is a capital H - both side strokes are vertical and meet no point at the top."),
     "B": ("Two slanted strokes meeting at a point at the top with no crossbar, among other letters",
           "That is a capital V; the crossbar is missing."),
     "C": ("Two slanted strokes meeting at a point at the bottom with no crossbar, among other "
           "letters",
           "Its strokes meet at the bottom rather than the top, and it has no crossbar.")},
    "D",
    "The bordered box is clutter around the letter; the strokes and crossbar inside it are exactly "
    "the target.",
    "hidden-figure")

add(29,
    "Target outline: a square with one diagonal, a single line joining two opposite corners. Which "
    "panel contains it?",
    "A square with both diagonals drawn, overlapped by a triangle",
    {"A": ("A square rotated 45 degrees with a line joining the midpoints of two opposite sides",
           "Its line joins the midpoints of sides, not two corners, so it is not a diagonal."),
     "C": ("A rectangle, longer than it is wide, with one line joining two opposite corners",
           "Its outline is a non-square rectangle, so the square of the target is missing."),
     "D": ("A triangle with one line drawn from a corner to the opposite side",
           "Its outline is a three-sided figure, not a four-sided square.")},
    "B",
    "The target is embedded in heavier clutter: of the two diagonals shown, either one together "
    "with the square outline forms the target.",
    "hidden-figure")

add(30,
    "Target outline: a rectangle with a semicircle sitting on its top edge, flat side down (a "
    "tombstone shape). Which panel contains it?",
    "A rectangle with a semicircle on its top edge, flat side down",
    {"A": ("A rectangle with a triangle on its top edge",
           "A triangle caps its rectangle - the house shape, not a semicircle."),
     "B": ("A rectangle with a semicircle hanging from its bottom edge",
           "Its semicircle is underneath, so the figure is the target turned upside down."),
     "C": ("A rectangle with a full circle sitting on its top edge",
           "The shape on top is a complete circle, not a semicircle with a flat side.")},
    "D",
    "This panel has the rectangle with a half-circle resting flat-side down on its top edge, "
    "exactly the target outline.",
    "hidden-figure")

# --------------------------------------------------------------------------
# pre-dump validation
# --------------------------------------------------------------------------
assert len(ITEMS) == 30, len(ITEMS)
assert [i["id"] for i in ITEMS] == [f"nmat-p1p-{n:03d}" for n in range(1, 31)]
assert Counter(i["chapter"] for i in ITEMS) == {
    "mirror-image": 10, "identical-information": 10, "hidden-figure": 10}
counts = Counter(i["answer"] for i in ITEMS)
assert max(counts.values()) <= 8, counts
for it in ITEMS:
    assert set(it["choices"]) == {"A", "B", "C", "D"}
    assert it["answer"] in it["choices"]
    assert it["answer"] not in it["distractors"]
    assert set(it["distractors"]) == set("ABCD") - {it["answer"]}
    assert all(it["choices"].values()) and all(it["distractors"].values())
    assert len(set(it["choices"].values())) == 4, f"{it['id']}: duplicate option text"

doc = {
    "exam": "nmat",
    "section": "part1-perceptual",
    "label": "Perceptual Acuity",
    "subject": "perceptual-acuity",
    "block": "part1",
    "items_expected": 30,
    "items": ITEMS,
    "passages": [],
}

with open(OUT, "w", encoding="utf-8") as fh:
    yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True, width=100,
                   default_flow_style=False)

print("wrote", OUT)
print("answers:", dict(sorted(counts.items())))
print("chapters:", dict(Counter(i["chapter"] for i in ITEMS)))
