"""Batch 3: append the last 5 practice items."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path("/home/ubuntu/django-wsgi/content/chapters")

BATCH = {
    "6a-sensing-the-environment.yml": [
        {
            "id": "6a-sensing-the-environment-p3",
            "q": ("In a signal detection task, a listener presses “yes, I heard it” on a trial where no "
                  "tone was actually played. This response is scored as a:"),
            "choices": {
                "A": "Hit",
                "B": "Miss",
                "C": "Correct rejection",
                "D": "False alarm",
            },
            "answer": "D",
            "explain": ("The four outcomes cross signal present/absent with yes/no: signal plus “yes” is a "
                        "hit, signal plus “no” a miss, no-signal plus “no” a correct rejection, and "
                        "no-signal plus “yes” a false alarm."),
            "chapter": "6A · Sensing the environment",
        },
    ],
    "fc8-self-others-interactions.yml": [
        {
            "id": "fc8-self-others-interactions-p9",
            "q": ("After an hour of discussion, a like-minded panel's average position on the issue is "
                  "more extreme than the average of its members' private views beforehand. This shift is:"),
            "choices": {
                "A": "Group polarization — deliberation amplifies the group's prevailing lean",
                "B": "Social loafing",
                "C": "Deindividuation",
                "D": "The false consensus effect",
            },
            "answer": "A",
            "explain": ("Group polarization is the post-discussion drift toward a more extreme version of "
                        "the initial tendency. Deindividuation is loss of self-awareness in crowds, and "
                        "false consensus is overestimating how many others share your view."),
            "chapter": "FC8 · Self, others, interactions",
        },
    ],
    "figure-grouping.yml": [
        {
            "id": "figure-grouping-p6",
            "q": ("Four figures are shown: (1) a square with 3 dots inside; (2) an equilateral triangle "
                  "with 3 dots inside; (3) a pentagon with 4 dots inside; (4) a circle with 3 dots inside. "
                  "Which figure does NOT belong with the other three?"),
            "choices": {
                "A": "Figure 1, the square",
                "B": "Figure 2, the triangle",
                "C": "Figure 3, the pentagon",
                "D": "Figure 4, the circle",
            },
            "answer": "C",
            "explain": ("The steady attribute across three figures is “exactly 3 dots inside,” so the "
                        "pentagon with 4 dots is the odd one out. Outer shape (square, triangle, circle) "
                        "is decoration — count structure carries the rule."),
            "chapter": "Figure Grouping",
        },
    ],
    "figure-series.yml": [
        {
            "id": "figure-series-p5",
            "q": ("In a figure series each frame shows a square with an arrow and some dots. The arrow "
                  "starts pointing to 12 o'clock and rotates 90° clockwise in every successive frame, "
                  "while the dot count runs 1, 2, 3, … Frame 5 therefore shows:"),
            "choices": {
                "A": "The arrow pointing right, with 5 dots",
                "B": "The arrow pointing up, with 5 dots",
                "C": "The arrow pointing down, with 5 dots",
                "D": "The arrow pointing up, with 4 dots",
            },
            "answer": "B",
            "explain": ("Two stacked rules tracked separately. Rotation: up → right → down → left → up, "
                        "since 4 × 90° = 360° returns to the start in frame 5. Dots: 1, 2, 3, 4, 5. "
                        "Missing the wrap gives A, reading 180° steps gives C, forgetting the increment "
                        "gives D."),
            "chapter": "Figure Series",
        },
    ],
    "fundamental-operations.yml": [
        {
            "id": "fundamental-operations-p7",
            "q": "A tax rate rises from 4% to 5%. Which statement is correct?",
            "choices": {
                "A": "It rose by 25 percentage points",
                "B": "It rose by 0.25 percentage points",
                "C": "It rose by 4 percentage points",
                "D": "It rose by 1 percentage point, which is a 25% relative increase",
            },
            "answer": "D",
            "explain": ("Percentage points subtract the rates: 5 − 4 = 1 point. Relative percent change "
                        "divides by the baseline: 1 ÷ 4 = 25%. Option A promotes the relative figure to "
                        "points, B swaps the two, C uses the old rate as the change."),
            "chapter": "Fundamental Operations",
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
