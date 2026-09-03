"""Batch 2: append practice items to 4 skill + 2 sociocultural chapters (11 items)."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path("/home/ubuntu/django-wsgi/content/chapters")

BATCH = {
    "hidden-figure.yml": [
        {
            "id": "hidden-figure-p3",
            "q": ("A hidden-figure target is an L-shape made of two arms of equal length meeting at a "
                  "right angle. Somewhere in the clutter it appears turned upside down and back to front. "
                  "Which candidate is that target?"),
            "choices": {
                "A": "An L-shape whose vertical arm is twice as long as its horizontal arm",
                "B": "A T-shape whose two arms are equal",
                "C": "An L-shape with equal arms, rotated 180° so the corner points the other way",
                "D": "A plus sign with four equal arms",
            },
            "answer": "C",
            "explain": ("Rotation and mirroring preserve the shape, so the target is still an equal-armed "
                        "L. Changing an arm's length produces a different figure, and T and cross shapes "
                        "have different line junctions entirely."),
            "chapter": "Hidden Figure",
        },
        {
            "id": "hidden-figure-p4",
            "q": ("On a hidden-figure item you must find a triangle buried in overlapping polygons. "
                  "Checking short runs of contour — one vertex plus the two lines leaving it — beats "
                  "trying to see the whole triangle at once because:"),
            "choices": {
                "A": "A local junction is a small, verifiable unit, and confirmed segments add up to the outline",
                "B": "The eye takes in an entire complex figure in a single fixation",
                "C": "Background lines never cross the target's outline",
                "D": "Filled-in regions are easier to match than outlines",
            },
            "answer": "A",
            "explain": ("Segment matching turns one hard search into several easy ones. Whole-figure "
                        "search fails because background lines do cross the outline, and the target's "
                        "outline — not any fill — is what must be tracked."),
            "chapter": "Hidden Figure",
        },
    ],
    "identical-information.yml": [
        {
            "id": "identical-information-p4",
            "q": ("Compare these two record strings: AB-47/II·09 and AB-47/ll·09. Which verdict is right?"),
            "choices": {
                "A": "Identical — the slash makes the following characters irrelevant",
                "B": "Different: after the slash, the first has two capital I's and the second has two lowercase L's",
                "C": "Different: the digit 4 has been replaced by a letter in the second string",
                "D": "Different: the hyphen has been dropped from the second string",
            },
            "answer": "B",
            "explain": ("Capital I and lowercase l are near-identical glyphs — the classic confusable-pair "
                        "trap. Every other position matches, so the divergence sits exactly at that one "
                        "place and only a character-by-character scan finds it."),
            "chapter": "Identical Information",
        },
        {
            "id": "identical-information-p5",
            "q": ("Which pair is NOT identical? (1) 839-2041 vs 839-2041 ; (2) Kayla.Rae@med.ph vs "
                  "Kayla.Rae@med.ph ; (3) 0.5 mL, q6h vs 0.5 mL, q6h ; (4) PN-9912-Q vs PN-9912-O"),
            "choices": {
                "A": "Pair 1",
                "B": "Pair 2",
                "C": "Pair 3",
                "D": "Pair 4",
            },
            "answer": "D",
            "explain": ("Pairs 1–3 match at every position. Pair 4 differs only in the final character "
                        "(Q vs O), a confusable pair hiding at the end of the string — exactly where "
                        "hurried scanning relaxes."),
            "chapter": "Identical Information",
        },
    ],
    "number-and-letter-series.yml": [
        {
            "id": "number-and-letter-series-p4",
            "q": "What letter comes next in the series C, F, I, L, … ?",
            "choices": {
                "A": "N",
                "B": "M",
                "C": "O",
                "D": "P",
            },
            "answer": "C",
            "explain": ("Map to alphabet indices: C=3, F=6, I=9, L=12 — a constant step of +3. "
                        "12 + 3 = 15, and the 15th letter is O. N=14 and M=13 are off-by-one slips, "
                        "P=16 assumes a +4 step."),
            "chapter": "Number and Letter Series",
        },
        {
            "id": "number-and-letter-series-p5",
            "q": "What number continues the series 2, 3, 6, 11, 18, … ?",
            "choices": {
                "A": "27",
                "B": "26",
                "C": "25",
                "D": "29",
            },
            "answer": "A",
            "explain": ("Second-order rule: the differences 1, 3, 5, 7 are consecutive odd numbers, so the "
                        "next difference is 9 and 18 + 9 = 27. 26 takes the last difference as 8, 25 forces "
                        "the terms onto the squares 1, 4, 9, 16, 25, and 29 skips ahead to a difference of 11."),
            "chapter": "Number and Letter Series",
        },
    ],
    "problem-solving.yml": [
        {
            "id": "problem-solving-p4",
            "q": ("Towns P and Q are 240 km apart. A car leaves P toward Q at 60 km/h and, at the same "
                  "moment, another leaves Q toward P at 40 km/h. After how long do they meet?"),
            "choices": {
                "A": "4.0 h — dividing 240 by the faster car's speed alone",
                "B": "2.4 h — the gap closes at the sum of the speeds, 100 km/h",
                "C": "6.0 h — dividing 240 by the slower car's speed alone",
                "D": "12 h — subtracting the speeds first, 240 ÷ 20",
            },
            "answer": "B",
            "explain": ("In a meet setup the closing speed is the sum: 60 + 40 = 100 km/h. "
                        "Time = 240 ÷ 100 = 2.4 h. Dividing by one car's speed ignores that both are moving."),
            "chapter": "Problem Solving",
        },
        {
            "id": "problem-solving-p5",
            "q": ("How many liters of a 20% salt solution must be mixed with 10 L of a 50% solution to "
                  "produce a 30% mixture?"),
            "choices": {
                "A": "5 L",
                "B": "10 L",
                "C": "15 L",
                "D": "20 L",
            },
            "answer": "D",
            "explain": ("Conserve solute: 0.20x + 0.50(10) = 0.30(x + 10) → 0.20x + 5 = 0.30x + 3 → "
                        "0.1x = 2 → x = 20 L. Check: 4 L + 5 L = 9 L of salt in 30 L = 30%."),
            "chapter": "Problem Solving",
        },
    ],
    "sociology-and-anthropology.yml": [
        {
            "id": "sociology-and-anthropology-p6",
            "q": ("An anthropologist spends a year in a highland village, planting rice alongside farmers "
                  "and joining rituals while keeping daily field notes. This method is:"),
            "choices": {
                "A": "A structured survey with a fixed questionnaire",
                "B": "A laboratory experiment with random assignment",
                "C": "Participant observation — the core ethnographic method",
                "D": "Secondary analysis of census records",
            },
            "answer": "C",
            "explain": ("Living inside the setting and taking part in daily life while recording "
                        "observations is participant observation, the ethnographic route to grasping a "
                        "culture's meaning from the inside."),
            "chapter": "Sociology and Anthropology",
        },
        {
            "id": "sociology-and-anthropology-p7",
            "q": "Which of the following is an ascribed status rather than an achieved one?",
            "choices": {
                "A": "The ethnic group a person is born into",
                "B": "A licensed registered nurse",
                "C": "An elected council member",
                "D": "A doctoral degree holder",
            },
            "answer": "A",
            "explain": ("Ascribed status is assigned at birth or involuntarily (ethnicity, sex, age in "
                        "most legal systems); achieved status is earned through action, as with licenses, "
                        "offices, and degrees."),
            "chapter": "Sociology and Anthropology",
        },
    ],
    "10a-social-inequality.yml": [
        {
            "id": "10a-social-inequality-p12",
            "q": "The “Matthew effect” in social inequality describes the tendency for:",
            "choices": {
                "A": "Progressive taxation to level wealth across generations",
                "B": "Early advantage to compound, so those who start ahead pull further ahead",
                "C": "Groups with different starting points to converge on equal outcomes",
                "D": "Schooling by itself to erase class differences in health",
            },
            "answer": "B",
            "explain": ("Advantage accumulates and amplifies: children who read early read more and gain "
                        "vocabulary faster, and capital earns returns on returns. The result is widening "
                        "gaps, not convergence."),
            "chapter": "10A · Social inequality",
        },
    ],
}


def main() -> None:
    for fname, items in BATCH.items():
        path = ROOT / fname
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        existing = doc.get("practice") or []
        have = {it["id"] for it in existing}
        for it in items:
            if it["id"] in have:
                raise SystemExit(f"{fname}: id already present {it['id']}")
            if it["answer"] not in it["choices"]:
                raise SystemExit(f"{it['id']}: answer not in choices")
            existing.append(it)
        doc["practice"] = existing
        path.write_text(
            yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
            encoding="utf-8",
        )
        print(f"{fname}: now {len(existing)} practice items")


if __name__ == "__main__":
    main()
