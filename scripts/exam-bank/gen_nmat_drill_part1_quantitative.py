#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/drill/part1-quantitative.yml (25-item drill).

Standalone MCQs, no passages. Deeper than the main part1-quantitative bank:
order-of-operations traps, percent questions that hinge on which base you use,
a fill/leak work rate, markup-then-discount reversal, and DI items whose
percentages change base between rows.

Every numeric answer is RECOMPUTED here by the checker lambda in the last
field of each tuple and asserted against the authored answer text.
"""
import os
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part1-quantitative.yml"

LETTERS = ["A", "C", "B", "D", "B", "A", "D", "C", "A", "B", "D", "C",
           "B", "A", "C", "D", "A", "B", "C", "D", "A", "C", "B", "D",
           "A"]
assert len(LETTERS) == 25
assert Counter(LETTERS) == Counter({"A": 7, "B": 6, "C": 6, "D": 6})
assert max(Counter(LETTERS).values()) <= 7

# ----------------------------------------------- data-interpretation tables
HC = {"Jan": (240, 36000), "Feb": (300, 45000), "Mar": (210, 37800)}
PH = {"Quiapo": (1200000, 8), "Divisoria": (900000, 9)}
TARGET = 2500000

HC_TABLE = ("A barangay health center logged three months of consultations and the "
            "medicine cost charged against them:\n\n"
            "Month | Consultations | Medicine cost\n"
            "January | 240 | P36,000\n"
            "February | 300 | P45,000\n"
            "March | 210 | P37,800\n\n")
PH_TABLE = ("Two branches of a pharmacy chain reported a month of sales and the staff "
            "on duty:\n\n"
            "Branch | Sales | Staff\n"
            "Quiapo | P1,200,000 | 8\n"
            "Divisoria | P900,000 | 9\n\n")


def peso(n):
    return "P{:,.0f}".format(n)


# (chapter, stem, correct, [(wrong, note) x3], explain, checker)
ITEMS = [
    # ------------------------------------------------ fundamental operations
    ("fundamental-operations",
     "Evaluate: 18 - 2 x (3 + 4)^2 / 7",
     "4",
     [("16", "Drops the square and uses 7 instead of 49: 18 - 2 x 7 / 7 = 16."),
      ("-80", "Squares and multiplies but skips the division by 7: 18 - 98 = -80."),
      ("140", "Adds 18 and 2 first, then multiplies: 20 x 49 / 7 = 140.")],
     "Parentheses first: (3 + 4)^2 = 49. Then 2 x 49 = 98, 98 / 7 = 14, and 18 - 14 = 4.",
     lambda: 18 - 2 * (3 + 4) ** 2 / 7),

    ("fundamental-operations",
     "A price rises from P360 to P450. The increase is what percent of the original price?",
     "25%",
     [("20%", "Uses the NEW price as the base: 90 / 450 = 20%. The base is the original P360."),
      ("125%", "Compares the new price with the old (450 / 360) instead of comparing the increase."),
      ("90%", "Reports the peso increase as though it were already a percentage.")],
     "The increase is P90 on a base of P360, and 90 / 360 = 0.25, so the increase is 25% of the original price.",
     lambda: (450 - 360) / 360 * 100),

    ("fundamental-operations",
     "Evaluate: 7/8 - 2/3 + 5/12",
     "5/8",
     [("9/8", "Adds 2/3 instead of subtracting it: 21/24 + 16/24 - 10/24 = 27/24 = 9/8."),
      ("5/12", "Writes 5/12 as 5/24 when building the common denominator, doubling the denominator without doubling the numerator."),
      ("7/12", "Writes 7/8 as 20/24 instead of 21/24, giving 20 - 16 + 10 = 14/24.")],
     "In twenty-fourths: 21/24 - 16/24 + 10/24 = 15/24, which reduces to 5/8.",
     lambda: "5/8" if 7 / 8 - 2 / 3 + 5 / 12 == 15 / 24 else None),

    ("fundamental-operations",
     "Simplify: (3^4 x 3^-2) / 3^1",
     "3",
     [("27", "Adds the exponent 1 in the division instead of subtracting it: 3^(4-2+1) = 3^3."),
      ("-243", "Reads 3^-2 as the negative of 3^2, so 81 x (-9) / 3 = -243."),
      ("729", "Drops the division and adds the first two exponents: 3^(4+2) = 3^6.")],
     "Subtract exponents when dividing: 3^(4 - 2 - 1) = 3^1 = 3.",
     lambda: 3 ** 4 * 3 ** -2 / 3 ** 1),

    ("fundamental-operations",
     "4.2 / 0.07 = ?",
     "60",
     [("0.6", "Shifts the decimal the wrong way, treating the divisor as 7 rather than 0.07."),
      ("6", "Shifts only one place instead of two when clearing the decimal from the divisor."),
      ("600", "Shifts three places, as though dividing 4.2 by 0.007.")],
     "Multiply top and bottom by 100: 420 / 7 = 60.",
     lambda: 4.2 / 0.07),

    ("fundamental-operations",
     "Evaluate: 3 1/2 x 2 2/5",
     "8 2/5",
     [("6 1/5", "Multiplies the whole numbers and the fractions separately: 3 x 2 and 1/2 x 2/5."),
      ("5 9/10", "Adds the two mixed numbers instead of multiplying them."),
      ("7 1/5", "Converts 2 2/5 to 12/5 but multiplies it by 3 only, dropping the half.")],
     "As improper fractions: 7/2 x 12/5 = 84/10 = 42/5 = 8 2/5.",
     lambda: "8 2/5" if (7 / 2) * (12 / 5) == 42 / 5 else None),

    ("fundamental-operations",
     "Two partners share profits in the ratio 4:7. The larger share is P4,200 more than the "
     "smaller share. What is the smaller share?",
     peso(5600),
     [(peso(4200), "Takes the difference itself as the smaller share, ignoring that the difference is 3 parts."),
      (peso(9800), "That is the larger share, 7 parts of P1,400."),
      (peso(2400), "Divides 4,200 by 7 and multiplies by 4, using the wrong number of parts in the difference.")],
     "The difference is 7 - 4 = 3 parts, so one part is P1,400 and the smaller share is 4 x P1,400 = P5,600.",
     lambda: 4 * (4200 / (7 - 4))),

    ("fundamental-operations",
     "A loan of P12,000 earns 6% simple interest a year. What is the total owed after 8 months?",
     peso(12480),
     [(peso(480), "Reports the interest alone as though it were the total owed."),
      (peso(12720), "Charges a full year of interest instead of eight months' worth."),
      (peso(11520), "Subtracts the interest instead of adding it to the principal.")],
     "Interest is 12,000 x 0.06 x 8/12 = P480, so the total owed is 12,000 + 480 = P12,480.",
     lambda: 12000 + 12000 * 0.06 * (8 / 12)),

    ("fundamental-operations",
     "Which value is closest to the square root of 245?",
     "15.7",
     [("15.5", "Averages 15 and 16 instead of moving toward 16 because 245 sits nearer 256 than 225."),
      ("16.5", "Puts the root past 16, though 16.5^2 = 272 is already well above 245."),
      ("14.5", "Rounds 245 down toward 225; 14.5^2 = 210 is far short.")],
     "15^2 = 225 and 16^2 = 256, so the root lies between them; 15.7^2 = 246.5 is closest to 245.",
     lambda: 15.7 if 245 ** 0.5 > 15.6 else None),

    # ------------------------------------------------------ problem solving
    ("problem-solving",
     "Ben is three times as old as his son. In 12 years he will be exactly twice as old as his "
     "son. How old is the son now?",
     "12 years old",
     [("24 years old", "Reports the son's age 12 years from now rather than now."),
      ("36 years old", "Reports Ben's present age, not the son's."),
      ("6 years old", "Halves the 12-year span instead of solving the two conditions together.")],
     "If the son is s, Ben is 3s, and 3s + 12 = 2(s + 12), so 3s + 12 = 2s + 24 and s = 12. Check: Ben is 36, later 48 and 24.",
     lambda: 12 if (3 * 12 + 12 == 2 * (12 + 12)) else None),

    ("problem-solving",
     "Pipe A fills a tank in 4 hours. A leak at the bottom drains the full tank in 12 hours. "
     "With the pipe open and the leak running, how long does the empty tank take to fill?",
     "6 hours",
     [("3 hours", "Adds the two rates (1/4 + 1/12 = 1/3) instead of subtracting the leak."),
      ("8 hours", "Averages the two given times instead of combining the rates."),
      ("16 hours", "Adds the two given times as though the leak merely slowed the fill by its own duration.")],
     "Net rate is 1/4 - 1/12 = 3/12 - 1/12 = 2/12 = 1/6 of a tank an hour, so the tank fills in 6 hours.",
     lambda: 1 / (1 / 4 - 1 / 12)),

    ("problem-solving",
     "How many kilograms of rice costing P48 a kilogram must be mixed with 12 kg of rice "
     "costing P60 a kilogram to make a blend worth P52 a kilogram?",
     "24 kg",
     [("6 kg", "Inverts the alligation ratio 2:1 and allots the smaller amount to the cheaper rice."),
      ("36 kg", "Adds the price differences (8 + 4) instead of taking their ratio."),
      ("12 kg", "Assumes the two rice lots must be equal in weight.")],
     "The gaps are 60 - 52 = 8 and 52 - 48 = 4, so cheap : dear = 8 : 4 = 2 : 1. Twice 12 kg is 24 kg.",
     lambda: 12 * (60 - 52) / (52 - 48)),

    ("problem-solving",
     "A motorist covers 120 km at 60 km/h and the next 120 km at 40 km/h. What is the average "
     "speed for the whole trip?",
     "48 km/h",
     [("50 km/h", "Takes the simple average of the two speeds, which is wrong when the times differ."),
      ("53 km/h", "Uses 1.5 hours for the first leg instead of 2, giving 240 / 4.5."),
      ("40 km/h", "Reports the slower leg's speed rather than the whole-trip average.")],
     "The legs take 2 h and 3 h, so 240 km over 5 h gives 48 km/h.",
     lambda: 240 / (120 / 60 + 120 / 40)),

    ("problem-solving",
     "The sum of three consecutive odd integers is 141. What is the product of the smallest "
     "and the largest?",
     "2205",
     [("2025", "Squares the middle term instead of multiplying the smallest by the largest."),
      ("2160", "Multiplies the smallest by the middle term."),
      ("2401", "Squares the largest term.")],
     "The middle integer is 141 / 3 = 47, so the three are 45, 47 and 49, and 45 x 49 = 2205.",
     lambda: 45 * 49 if 45 + 47 + 49 == 141 else None),

    ("problem-solving",
     "A shop marks up an item 40% on cost, then sells it at a 10% discount on the marked "
     "price. The selling price is P2,520. What did the item cost?",
     peso(2000),
     [(peso(1800), "Divides by the 1.40 markup and stops, ignoring the 10% discount."),
      (peso(2268), "Applies the 10% discount again instead of undoing it."),
      (peso(2800), "Divides by 0.9 only, ignoring the 40% markup.")],
     "Selling price = cost x 1.40 x 0.90 = 1.26 x cost, so the cost is 2,520 / 1.26 = P2,000.",
     lambda: 2520 / (1.4 * 0.9)),

    ("problem-solving",
     "A rectangular garden measuring 18 m by 12 m is surrounded by a uniform walkway 2 m wide. "
     "What is the area of the walkway?",
     "136 square meters",
     [("64 square meters", "Adds the walkway width to only one dimension of each side, giving 20 x 14."),
      ("120 square meters", "Multiplies the walkway's width by the garden's perimeter, ignoring the corners."),
      ("432 square meters", "Doubles the garden's area instead of subtracting it from the larger rectangle.")],
     "The outer rectangle is 22 m by 16 m = 352 sq m; the garden is 216 sq m, so the walkway is 352 - 216 = 136 sq m.",
     lambda: (18 + 2 * 2) * (12 + 2 * 2) - 18 * 12),

    ("problem-solving",
     "In a class of 45 students, 28 joined the math club, 24 joined the science club, and 9 "
     "joined neither club. How many joined both clubs?",
     "16",
     [("7", "Subtracts the class size from the sum of the two memberships, ignoring the 9 who joined neither."),
      ("43", "Subtracts the 9 from the sum 52 instead of from the class size."),
      ("12", "Subtracts the science club from the union instead of from the sum of memberships.")],
     "36 students joined at least one club (45 - 9), so both = 28 + 24 - 36 = 16.",
     lambda: 28 + 24 - (45 - 9)),

    ("problem-solving",
     "A number leaves a remainder of 3 when divided by 5 and a remainder of 4 when divided by "
     "7. What is the smallest number greater than 10 with both properties?",
     "18",
     [("11", "Satisfies the divisor-7 condition only, since 11 / 5 leaves 1."),
      ("23", "Satisfies the divisor-5 condition only, since 23 / 7 leaves 2."),
      ("39", "Satisfies the two remainders with the divisors interchanged: 39 leaves 4 by 5 and 4 by 7.")],
     "Numbers leaving 4 by 7 are 11, 18, 25, 32, 39; the first of these leaving 3 by 5 is 18.",
     lambda: next(n for n in range(11, 200) if n % 5 == 3 and n % 7 == 4)),

    # -------------------------------------------------- data interpretation
    ("data-interpretation",
     HC_TABLE + "What was the medicine cost per consultation in February?",
     peso(150),
     [(peso(120), "Divides January's cost by February's consultations."),
      (peso(214), "Divides February's cost by March's consultations."),
      (peso(135), "Averages January's and February's per-consultation costs instead of computing February's.")],
     "February: P45,000 over 300 consultations is P150 each.",
     lambda: 45000 / HC["Feb"][0]),

    ("data-interpretation",
     HC_TABLE + "The medicine cost per consultation in March is what percent higher than in "
     "January?",
     "20%",
     [("5%", "Compares the two total medicine costs, ignoring that consultations fell as well."),
      ("16.7%", "Divides the P30 rise by the March figure of P180 instead of by the January base."),
      ("30%", "Reports the peso rise of P30 as though it were 30%.")],
     "January is 36,000 / 240 = P150 and March is 37,800 / 210 = P180 per consultation, so the rise is 30 / 150 = 20%.",
     lambda: (37800 / 210 - 36000 / 240) / (36000 / 240) * 100),

    ("data-interpretation",
     HC_TABLE + "How many consultations did the center record over the three months?",
     "750",
     [("720", "Loses 30 of February's consultations when adding."),
      ("780", "Counts 30 of February's consultations twice."),
      ("300", "Reports the highest single month instead of the three-month total.")],
     "240 + 300 + 210 = 750 consultations.",
     lambda: HC["Jan"][0] + HC["Feb"][0] + HC["Mar"][0]),

    ("data-interpretation",
     PH_TABLE + "Which branch recorded the higher sales per member of staff, and by how much?",
     "Quiapo, by %s" % peso(50000),
     [("Divisoria, by %s" % peso(50000), "Swaps the two branches; Divisoria's sales per member of staff is the lower one."),
      ("Quiapo, by %s" % peso(300000), "Compares the difference in total sales instead of sales per member of staff."),
      ("Quiapo, by %s" % peso(12500), "Divides the total sales difference by the combined staff of 24.")],
     "Quiapo: 1,200,000 / 8 = P150,000. Divisoria: 900,000 / 9 = P100,000. The gap is P50,000 in Quiapo's favor.",
     lambda: "P50,000" if PH["Quiapo"][0] / PH["Quiapo"][1] - PH["Divisoria"][0] / PH["Divisoria"][1] == 50000 else None),

    ("data-interpretation",
     PH_TABLE + "The two branches together aimed at %s. What percent of the target did they "
     "reach?" % peso(TARGET),
     "84%",
     [("119%", "Inverts the ratio and divides the target by the sales."),
      ("16%", "Reports the shortfall of P400,000 as the attainment."),
      ("87.5%", "Uses a target of P2,400,000, dropping P100,000 from the stated figure.")],
     "Combined sales are 1,200,000 + 900,000 = P2,100,000, and 2,100,000 / 2,500,000 = 84%.",
     lambda: (PH["Quiapo"][0] + PH["Divisoria"][0]) / TARGET * 100),

    ("data-interpretation",
     PH_TABLE + "Next month Quiapo's sales rise 10% and Divisoria's fall 10%. What would the "
     "two branches take together?",
     peso(2130000),
     [(peso(2100000), "Assumes a 10% rise and a 10% fall cancel, though the two bases differ."),
      (peso(1320000), "Counts Quiapo's higher total only."),
      (peso(2310000), "Raises both branches by 10% instead of lowering Divisoria's.")],
     "Quiapo becomes 1,200,000 x 1.10 = P1,320,000 and Divisoria 900,000 x 0.90 = P810,000, a total of P2,130,000.",
     lambda: PH["Quiapo"][0] * 1.1 + PH["Divisoria"][0] * 0.9),

    ("data-interpretation",
     PH_TABLE + "What percent of the two branches' combined sales came from Divisoria?",
     "42.9%",
     [("30%", "Divides Divisoria's staff share or its sales against P3,000,000 instead of the combined total."),
      ("57.1%", "Reports Quiapo's share of the combined sales."),
      ("75%", "Compares Divisoria's sales with Quiapo's instead of with the combined total.")],
     "900,000 / 2,100,000 = 0.4286, about 42.9% of the combined sales.",
     lambda: round(PH["Divisoria"][0] / (PH["Quiapo"][0] + PH["Divisoria"][0]) * 100, 1)),
]

ALLOWED = {"fundamental-operations", "problem-solving", "data-interpretation"}


def build():
    pool = []
    for chap, stem, right, wrongs, explain, checker in ITEMS:
        assert chap in ALLOWED, chap
        val = checker()
        if isinstance(val, float):
            assert abs(val - round(val, 6)) < 1e-9, val
        if right.endswith("%"):
            assert abs(val - float(right.rstrip("%"))) < 0.05, (right, val)
        elif right.startswith("P"):
            assert abs(val - float(right[1:].replace(",", ""))) < 0.01, (right, val)
        elif right[0].isdigit() and " " not in right and "/" not in right:
            assert abs(val - float(right)) < 1e-6, (right, val)
        assert right not in [w for w, _ in wrongs], right
        pool.append(dict(q=stem, right=right, wrongs=wrongs, explain=explain, chapter=chap))

    assert len(pool) == 25, len(pool)
    counts = Counter(p["chapter"] for p in pool)
    assert counts == Counter({"fundamental-operations": 9, "problem-solving": 9,
                              "data-interpretation": 7}), counts
    assert len({p["q"] for p in pool}) == 25, "duplicate stems"

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
            "id": "nmat-d-p1q-%03d" % idx,
            "q": p["q"],
            "choices": {L: choices[L] for L in "ABCD"},
            "answer": letter,
            "explain": p["explain"],
            "distractors": {L: distractors[L] for L in wrong_letters},
            "chapter": p["chapter"],
        })
    return {
        "exam": "nmat",
        "section": "drill-part1-quantitative",
        "label": "Quantitative drill",
        "subject": "quantitative",
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
