#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/drill/part1-perceptual.yml (25-item drill).

Standalone MCQs, no passages, all figures described in words. Deeper than the
main part1-perceptual bank: water-image (up-down) symmetry, seven-segment
mirroring, half-turn versus mirror on N/S/Z, nested transformation chains,
and identity checks that hinge on letter/digit lookalikes (0/O, 1/I/l, B/8)
and adjacent transpositions.

The identical-information items are machine-checked: every option is the same
length as its target, exactly one option matches character for character, and
each distractor's note is BUILT from the real character diff, so it names the
exact position and the exact characters that differ.
"""
import os
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part1-perceptual.yml"

LETTERS = ["A", "C", "B", "D", "B", "A", "D", "C", "A", "B", "D", "C",
           "B", "A", "C", "D", "A", "B", "C", "D", "A", "C", "B", "D",
           "A"]
assert len(LETTERS) == 25
assert Counter(LETTERS) == Counter({"A": 7, "B": 6, "C": 6, "D": 6})
assert max(Counter(LETTERS).values()) <= 7

# --------------------------------------------------------------- mirror image
# (stem, correct, [(wrong, note) x3], explain)
MIRROR = [
    ("Which word still reads exactly the same, letter for letter, after reflection in a vertical "
     "mirror, where each capital is flipped left to right and the letter order reverses?",
     "TOOT",
     [("MAXIM", "Its letters M, A, X and I are all mirror-safe, but the word is not a palindrome: reversed it reads MIXAM."),
      ("MINIMUM", "Its letters M, I, N and U are all mirror-safe, but the word is not a palindrome: reversed it reads MUMINIM."),
      ("MIMIC", "It contains C, which has no left-right symmetry, and reversed it reads CIMIM.")],
     "TOOT is a palindrome, and T and O are each unchanged by a left-right flip, so the mirror returns the same word."),

    ("Which capital letter still looks the same after an up-down flip, the way a letter looks in "
     "the water below it?",
     "H",
     [("N", "N matches itself only under a half turn; flipped up and down its diagonal runs the other way."),
      ("M", "M has a vertical mirror line only; flipped up and down it reads like W."),
      ("T", "T has a vertical mirror line only; flipped up and down its stem points the wrong way.")],
     "H is symmetric about a horizontal line through its crossbar, so an up-down flip leaves it unchanged."),

    ("A seven-segment display shows a single digit. Seen in a vertical mirror, which digit still "
     "reads as a digit?",
     "8",
     [("2", "A mirrored 2 lights the segments of a 5, so it reads as a different digit."),
      ("3", "A mirrored 3 opens the other way and reads as the letter E."),
      ("6", "A mirrored 6 matches no digit; a 6 turns into a 9 only under a half turn.")],
     "8 uses both columns of segments on each side, so swapping left and right changes nothing."),

    ("A card printed with the word MOOD is held facing a vertical mirror. Which describes the "
     "image?",
     "The letters appear in reverse order, D, O, O and M from left to right, and only the D is reversed",
     [("The word appears exactly as printed, because O and M are symmetric",
       "It overlooks both the D, which is not symmetric, and the reversal of the letter order."),
      ("The letters keep their left-to-right order but each one is flipped",
       "A mirror puts the rightmost letter nearest the glass, so the order reverses."),
      ("The word appears upside down, reading MOOD from the top",
       "That describes a water image or a half turn, not a vertical mirror.")],
     "A vertical mirror reverses the running order and flips each letter; only the D is changed in shape."),

    ("Which figure has exactly one line of symmetry?",
     "an isosceles triangle",
     [("a square", "A square has four lines of symmetry, one for each pair of opposite points."),
      ("a circle", "A circle has a line of symmetry through every diameter, so it has endlessly many."),
      ("a rectangle that is not a square", "A non-square rectangle has two, one through each pair of midpoints.")],
     "Only the isosceles triangle folds onto itself in exactly one way, from apex to the midpoint of its base."),

    ("The capital letter L - a vertical stroke with a horizontal foot to the right at its bottom - "
     "is reflected in a vertical mirror, and that image is then given a half turn. What is left?",
     "a vertical stroke with a horizontal foot at its top extending to the right, an upside-down L",
     [("the original L, with its foot at the bottom to the right",
       "The two moves do not cancel: the mirror reverses left and right, the half turn then reverses both."),
      ("a vertical stroke with a foot at its top extending to the left",
       "That applies the half turn before the mirror, which is the other order."),
      ("a vertical stroke with a foot at its bottom extending to the left",
       "That is the mirrored L alone, with the half turn left out.")],
     "The mirror moves the foot to the left at the bottom; the half turn then carries it to the top on the right."),

    ("Which word is made only of capital letters that are each unchanged by an up-down flip?",
     "CHOICE",
     [("BEDTIME", "Its M and T lack a horizontal line of symmetry."),
      ("DECODER", "Its final R has no horizontal line of symmetry."),
      ("CHICKEN", "Its final N has no horizontal line of symmetry, though the other letters do.")],
     "C, H, O, I and E are all symmetric about a horizontal line, so every letter of CHOICE survives an up-down flip."),

    ("Which statement about the capital letters N, S and Z is correct?",
     "each is unchanged by a half turn, and none is unchanged by a mirror reflection",
     [("each has a vertical mirror line",
       "None of the three has any mirror line; a flipped N, S or Z reads the wrong way round."),
      ("only Z is unchanged by a half turn",
       "All three are unchanged by a half turn, not only Z."),
      ("N and Z are mirror images of each other",
       "Mirroring N keeps its two strokes vertical; Z's strokes are horizontal, so no mirror takes one to the other.")],
     "N, S and Z all have half-turn symmetry and none of them has a mirror line, so the first statement covers all three."),

    ("A strip of paper printed with the two lowercase letters 'bd' is held up to a vertical "
     "mirror. What does the mirror show?",
     "bd, unchanged, because b and d are each other's mirror images and the reversal swaps their places",
     [("db", "It reverses the order but forgets that each letter also flips left to right."),
      ("pq", "That is the result of a half turn, not of a mirror reflection."),
      ("qp", "It flips each letter as a half turn would, without reversing their order.")],
     "Mirroring turns b into d and d into b, and the reversal then puts them back in the order b, d."),

]

# ----------------------------------------------------- identical information
# (stem containing {target}, target, [(wrong option, reason) x3], extra explain)
IDENT = [
    ("Target: {t} Which option is an exact character-for-character match for the target?",
     "PHC-2026-0408-RM2",
     [("PHC-2026-O408-RM2", "that is the capital letter O standing in for a zero"),
      ("PHC-2026-040B-RM2", "that is the letter B standing in for the digit 8"),
      ("PHC-2Q26-0408-RM2", "that is the letter Q in place of the zero in the year")],
     "The record number mixes letters and digits, so the zero and the 8 are the two characters most often mistyped."),

    ("Target: {t} Which option is an exact character-for-character match for the target?",
     "Santos, Mariel T. Ocampo",
     [("Santos, Muriel T. Ocampo", "the given name is spelled Mariel, with an a"),
      ("Santos, Mariel T. Ocmapo", "the last two letters of the surname are swapped"),
      ("Santos, Mariel T. Ocamp0", "that is a zero at the end, not the letter o")],
     "In names, a swapped pair of letters and a letter read as a digit are the usual near-misses."),

    ("Target: {t} Which option is an exact character-for-character match for the target?",
     "Lot 14-B, Purok 3, Brgy. San Isidro 1918",
     [("Lot 41-B, Purok 3, Brgy. San Isidro 1918", "the lot digits are transposed"),
      ("Lot 14-B, Purok 3, Brgy. San Isidro 1916", "the postal code ends in 8, not 6"),
      ("Lot 14-8, Purok 3, Brgy. San Isidro 1918", "that is the digit 8 where the target has the letter B")],
     "The lot number and the postal code each hide one trap, and the B after the lot number hides a third."),

    ("Target: {t} Which option is an exact character-for-character match for the target?",
     "LTO Driver 4-22-1988-C",
     [("LTO Driver 4-22-1988-c", "the trailing letter is a capital in the target"),
      ("LTO Driver 4-22-1998-C", "the year is 1988, not 1998"),
      ("L70 Driver 4-22-1988-C", "that is the digit 7 where the target has the letter T")],
     "Case matters here: the same letter in the wrong case is still a different character."),

    ("Target: {t} Which option is an exact character-for-character match for the target?",
     "4821 9037 5566 1204",
     [("4821 9073 5566 1204", "the third and fourth digits of the second group are swapped"),
      ("4827 9037 5566 1204", "the fourth digit of the first group is 1, not 7"),
      ("4821 9037 5566 1240", "the last two digits are swapped")],
     "Grouped digits invite transpositions inside a group, which is exactly what the first and third options carry."),

    ("Target: {t} Which option is an exact character-for-character match for the target?",
     "REF 2027-NC-004518-B",
     [("REF 2O27-NC-004518-B", "that is the letter O in place of the zero in 2027"),
      ("REF 2027-NC-0045I8-B", "that is a capital I in place of the digit 1"),
      ("REF 2027-NC-004518-8", "that is the digit 8 where the target ends in the letter B")],
     "Every wrong entry here turns one character into a lookalike, which is the only way this check fails."),
]

# two-string comparisons: the keyed choice must match the real diff count
COMPARE = [
    ("Two clinic codes are compared: 'TR-55831-QB' and 'TR-5583I-QB'. They are:",
     "TR-55831-QB", "TR-5583I-QB",
     "not identical, because they differ in one character",
     [("identical, character for character",
       "The fifth character of the second group differs, so the strings are not the same."),
      ("not identical, because they differ in two characters",
       "Only one position differs; nothing else in the two strings moves."),
      ("identical once the letters are read as digits",
       "A character check makes no such allowance: I is not 1, so the strings differ.")],
     "Reading character by character, the fifth character of the code is 1 in the first and the letter I in the second."),

    ("Two land-tax ledger lines are compared: 'Lot 17-C: area 240 sq m, tax due P1,880' and "
     "'Lot 17-C: area 240 sq m, tax due P1,88O'. They are:",
     "Lot 17-C: area 240 sq m, tax due P1,880",
     "Lot 17-C: area 240 sq m, tax due P1,88O",
     "not identical, because they differ in one character",
     [("identical, character for character",
       "The final character is a zero in one line and a capital O in the other."),
      ("not identical, because they differ in two characters",
       "Only the last character differs; the area and the rest of the amount agree."),
      ("identical, because the amounts are the same size",
       "Identity is character by character, not numeric; O is a letter, not a zero.")],
     "The last character is 0 (zero) in the first line and O (capital letter) in the second, so the lines differ in one place."),
]


def diff_note(target, wrong, reason):
    """Build the distractor note from the real character diff."""
    assert len(target) == len(wrong), (target, wrong)
    diffs = [k for k in range(len(target)) if target[k] != wrong[k]]
    assert len(diffs) in (1, 2), diffs
    if len(diffs) == 1:
        k = diffs[0]
        return ("Off by one character: position %d reads '%s' where the target has '%s' - %s."
                % (k + 1, wrong[k], target[k], reason))
    a, b = diffs
    return ("Off by two characters: position %d reads '%s' and position %d reads '%s', where the "
            "target has '%s' and '%s' - %s."
            % (a + 1, wrong[a], b + 1, wrong[b], target[a], target[b], reason))


def build():
    pool = []
    for stem, right, wrongs, explain in MIRROR:
        pool.append(dict(q=stem, right=right, wrongs=wrongs, explain=explain,
                         chapter="mirror-image"))

    for stem, target, wrongs, extra in IDENT:
        assert sum(1 for w, _ in wrongs if w == target) == 0
        for w, _ in wrongs:
            assert len(w) == len(target), (w, target)
        assert len({target} | {w for w, _ in wrongs}) == 4
        notes = [(w, diff_note(target, w, reason)) for w, reason in wrongs]
        q = stem.format(t=target)
        explain = "Only this option repeats the target character for character. " + extra
        pool.append(dict(q=q, right=target, wrongs=notes, explain=explain,
                         chapter="identical-information"))

    for stem, a, b, right, wrongs, explain in COMPARE:
        assert len(a) == len(b)
        diffs = sum(1 for k in range(len(a)) if a[k] != b[k])
        assert diffs == 1, diffs
        assert "one character" in right, right
        pool.append(dict(q=stem, right=right, wrongs=wrongs, explain=explain,
                         chapter="identical-information"))

    HIDDEN = _hidden()
    for stem, right, wrongs, explain in HIDDEN:
        pool.append(dict(q=stem, right=right, wrongs=wrongs, explain=explain,
                         chapter="hidden-figure"))

    assert len(pool) == 25, len(pool)
    counts = Counter(p["chapter"] for p in pool)
    assert counts == Counter({"mirror-image": 9, "identical-information": 8,
                              "hidden-figure": 8}), counts
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
            "id": "nmat-d-p1p-%03d" % idx,
            "q": p["q"],
            "choices": {L: choices[L] for L in "ABCD"},
            "answer": letter,
            "explain": p["explain"],
            "distractors": {L: distractors[L] for L in wrong_letters},
            "chapter": p["chapter"],
        })
    return {
        "exam": "nmat",
        "section": "drill-part1-perceptual",
        "label": "Perceptual Acuity drill",
        "subject": "perceptual-acuity",
        "block": "part1",
        "_drill": True,
        "items": items,
    }


def _hidden():
    """(stem, correct panel, [(panel, why it lacks the target) x3], explain)"""
    return [
        ("Target: a triangle with a straight line drawn from its apex to the midpoint of its "
         "base. Which panel contains it?",
         "a triangle with a line from its apex to the midpoint of its base, drawn inside a square frame",
         [("a triangle with a line from its apex to a point close to one end of its base, with a small square beside it",
           "The line stops near the end of the base, not at its midpoint."),
          ("a triangle with a horizontal line drawn parallel to its base",
           "That line runs side to side, so it never reaches the apex."),
          ("a triangle with a line from the midpoint of its base to the midpoint of one side",
           "That line starts on the base rather than at the apex.")],
         "Only the second panel runs a line from the apex to the halfway point of the base; the frame is clutter."),

        ("Target: two concentric circles with a single dot exactly at their common center. Which "
         "panel contains it?",
         "two concentric circles with a dot at their shared center, inside a dashed square",
         [("two circles side by side, each with a dot at its own center",
           "The circles do not share a center, so they are not concentric."),
          ("two concentric circles with a dot resting on the rim of the inner circle",
           "The dot sits on the inner circle, not at the shared center."),
          ("a single circle with two dots side by side inside it",
           "There is only one circle, and there are two dots.")],
         "Concentric means one inside the other about the same center, and the dot must sit on that center."),

        ("Target: a closed outline made of exactly five straight sides. Which panel contains it?",
         "a square with a triangle sitting on its upper edge and sharing that edge",
         [("a rectangle with both diagonals drawn, forming four triangles",
           "Its outlines have four sides and three sides, never five."),
          ("a hexagon with a single line joining two opposite corners",
           "Its outline has six sides, and the line cuts it into two four-sided halves."),
          ("a circle with a square drawn inside it",
           "The circle is not straight-sided and the square has only four sides.")],
         "A square with a triangular roof reads as one five-sided outline, which is the pentagon sought."),

        ("Target: a figure divided into exactly four enclosed regions by two lines that cross at "
         "a point. Which panel contains it?",
         "a square with both diagonals drawn, crossing at its center",
         [("a square with one diagonal only",
           "One line alone divides it into two regions."),
          ("a circle with a single diameter",
           "That is two regions, and the outline is round rather than straight-sided."),
          ("a rectangle with two parallel vertical lines",
           "Three regions result, and parallel lines never cross.")],
         "Two crossing lines make four wedges; the two diagonals of a square do exactly that."),

        ("Target: an L-shaped outline with exactly six straight sides. Which panel contains it?",
         "a square with a smaller square removed from one corner",
         [("a square with a smaller square drawn inside it, touching nothing",
           "The outlines are two separate four-sided figures, not one six-sided outline."),
          ("a rectangle with a notch cut into the middle of one side",
           "Cutting a notch into a side leaves eight sides, not six."),
          ("a triangle with a square drawn on one of its sides",
           "The outline there has five sides, and the parts are three- and four-sided.")],
         "Removing a corner square from a larger square leaves one outline with six sides."),

        ("Target: a circle divided into exactly two equal parts by one straight line through its "
         "center. Which panel contains it?",
         "a circle with one straight line through its center, with a small square drawn on top of the line",
         [("a circle with a straight line that crosses it but misses the center",
           "An off-center chord divides the circle into two unequal parts."),
          ("a circle with two perpendicular lines through its center",
           "Two lines make four parts, not two."),
          ("a square with one straight line through its center",
           "The outline is a square, not a circle.")],
         "Equal halves need a diameter; the small square laid over the line is only clutter."),

        ("Target: a square with a triangle drawn entirely inside it. Which panel contains it?",
         "a square with a triangle drawn inside it, with three small dots nearby",
         [("a square with a triangle drawn outside it, sharing one side",
           "The triangle lies outside the square."),
          ("a triangle with a smaller square drawn inside it",
           "The two figures are the wrong way round."),
          ("a square with a triangle sitting across its upper edge, half in and half out",
           "The triangle is not entirely inside.")],
         "The dots are clutter; the triangle sits wholly within the four sides of the square."),

        ("Target: a triangle with a horizontal line across its middle, dividing it into a smaller "
         "triangle and a trapezoid. Which panel contains it?",
         "a triangle with a horizontal line across its middle, and a circle drawn outside it",
         [("a triangle with a vertical line from its apex to its base",
           "That line runs up and down, so the two parts are both triangles."),
          ("a triangle with a horizontal line drawn just below its base",
           "A line outside the outline divides nothing."),
          ("a trapezoid with a horizontal line across its middle",
           "The outline is already four-sided, so no triangle is divided.")],
         "Only a horizontal line inside the triangle leaves a triangle on top and a trapezoid below."),
    ]


if __name__ == "__main__":
    data = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True,
                       width=100, default_flow_style=False)
    print("wrote", OUT, len(data["items"]), "items")
    print("chapters:", Counter(i["chapter"] for i in data["items"]))
    print("answers:", Counter(i["answer"] for i in data["items"]))
