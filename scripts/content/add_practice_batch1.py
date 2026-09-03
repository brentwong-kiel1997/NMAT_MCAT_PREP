"""Batch 1: append practice items to 6 psych/soc chapters (12 items)."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path("/home/ubuntu/django-wsgi/content/chapters")

BATCH = {
    "6c-responding-to-the-world.yml": [
        {
            "id": "6c-responding-to-the-world-p5",
            "q": "According to the James–Lange theory, the conscious feeling of fear comes:",
            "choices": {
                "A": "Before any bodily change, as a pure appraisal of the situation",
                "B": "From the reward value the situation has learned to carry",
                "C": "After physiological arousal — the emotion is the perception of the body's response",
                "D": "From the label other people attach to your behavior",
            },
            "answer": "C",
            "explain": ("James–Lange reverses common sense: the stimulus triggers autonomic arousal "
                        "(heart races, muscles tense) and the emotion IS the perception of that arousal, "
                        "not its cause."),
            "chapter": "6C · Responding to the world",
        },
        {
            "id": "6c-responding-to-the-world-p6",
            "q": "A student has been running on coffee and little sleep for exam week and now catches every cold going around. In Selye's general adaptation syndrome, this depleted state corresponds to:",
            "choices": {
                "A": "The alarm stage, where the sympathetic system first surges",
                "B": "The resistance stage, where cortisol keeps glucose and blood pressure up",
                "C": "Primary appraisal of the stressor",
                "D": "The exhaustion stage, where resources are worn down and immunity drops",
            },
            "answer": "D",
            "explain": ("GAS runs alarm → resistance → exhaustion. Prolonged resistance depletes "
                        "resources, so susceptibility to illness rises — the exhaustion stage. "
                        "Alarm is the initial surge and appraisal happens before any stage."),
            "chapter": "6C · Responding to the world",
        },
    ],
    "7a-individual-influences-on-behavior.yml": [
        {
            "id": "7a-individual-influences-on-behavior-p6",
            "q": "In the five-factor model, a person described as imaginative, curious, and eager to try new experiences scores high on:",
            "choices": {
                "A": "Conscientiousness",
                "B": "Openness to experience",
                "C": "Agreeableness",
                "D": "Neuroticism",
            },
            "answer": "B",
            "explain": ("OCEAN: the O stands for openness to experience — imagination, curiosity, "
                        "preference for novelty. Conscientiousness is organization and self-discipline, "
                        "agreeableness is warmth and cooperation, neuroticism is emotional instability."),
            "chapter": "7A · Individual influences on behavior",
        },
        {
            "id": "7a-individual-influences-on-behavior-p7",
            "q": "Two children carry the same risk allele for a disorder, but only the one raised in a high-stress household develops it. This pattern illustrates:",
            "choices": {
                "A": "Genes determining the outcome regardless of surroundings",
                "B": "The environment rewriting the DNA sequence itself",
                "C": "Parenting being the only cause of psychological outcomes",
                "D": "Gene–environment interaction: the same gene has different effects in different contexts",
            },
            "answer": "D",
            "explain": ("Gene–environment interaction means a genetic predisposition is expressed or "
                        "suppressed depending on context. The DNA sequence is unchanged, and neither the "
                        "gene nor the setting alone is sufficient to predict the outcome."),
            "chapter": "7A · Individual influences on behavior",
        },
    ],
    "7b-social-processes-that-influence-behavior.yml": [
        {
            "id": "7b-social-processes-that-influence-behavior-p7",
            "q": "A committee member does far less on a group report than she would have alone, because no one can tell which sections were hers. This is:",
            "choices": {
                "A": "Social facilitation on a difficult task",
                "B": "Obedience to an authority figure",
                "C": "Social loafing — individual effort drops when contributions are not identifiable",
                "D": "Groupthink",
            },
            "answer": "C",
            "explain": ("Social loafing is reduced individual effort in a group task, driven by diffusion "
                        "of responsibility and anonymity. Social facilitation is the opposite direction "
                        "(presence of others boosts performance on easy/well-learned tasks), and obedience "
                        "requires a direct order."),
            "chapter": "7B · Social processes that influence behavior",
        },
        {
            "id": "7b-social-processes-that-influence-behavior-p8",
            "q": "In Milgram's obedience studies, the highest shock-delivery rates occurred when:",
            "choices": {
                "A": "The legitimate authority stayed present in the room and issued the order in person",
                "B": "The learner was moved into the same room and could be touched",
                "C": "The experimenter left and gave instructions by telephone",
                "D": "The study was run in a plain office building instead of a university",
            },
            "answer": "A",
            "explain": ("Obedience rose with the authority's presence and legitimacy and fell when the "
                        "victim was closer, when the experimenter departed, or when the setting looked "
                        "less institutional — the opposite of the tempting distractors."),
            "chapter": "7B · Social processes that influence behavior",
        },
    ],
    "8b-social-thinking.yml": [
        {
            "id": "8b-social-thinking-p9",
            "q": "After a week of heavy news coverage of two train crashes, a commuter rates rail travel as far riskier than driving. This judgment error is best explained by:",
            "choices": {
                "A": "The self-serving bias",
                "B": "The availability heuristic — vivid, easily recalled cases inflate frequency estimates",
                "C": "Cognitive dissonance",
                "D": "The just-world hypothesis",
            },
            "answer": "B",
            "explain": ("The availability heuristic judges frequency by how easily examples come to mind. "
                        "Well-publicized disasters are highly memorable, so their perceived frequency is "
                        "inflated. Self-serving bias concerns explaining one's own outcomes."),
            "chapter": "8B · Social thinking",
        },
        {
            "id": "8b-social-thinking-p10",
            "q": "An attitude has three components — how you feel about something, how you tend to act toward it, and what you believe about it. These are respectively:",
            "choices": {
                "A": "Cognitive, behavioral, affective",
                "B": "Normative, descriptive, predictive",
                "C": "Id, ego, superego",
                "D": "Affective, behavioral, cognitive",
            },
            "answer": "D",
            "explain": ("The ABC model: Affect (feelings), Behavior (action tendency), Cognition "
                        "(beliefs) — in that order. Swapping affect and cognition is the classic trap."),
            "chapter": "8B · Social thinking",
        },
    ],
    "fc6-perceive-think-react.yml": [
        {
            "id": "fc6-perceive-think-react-p7",
            "q": "You can tell 100 g from 105 g, but not 1,000 g from 1,005 g — you need about 1,050 g. This illustrates:",
            "choices": {
                "A": "Sensory adaptation lowering receptor output over time",
                "B": "An absolute threshold fixed at about 5 g for all weights",
                "C": "Weber's law: the just noticeable difference is a roughly constant fraction of the baseline intensity",
                "D": "Signal detection bias, since hits and false alarms depend on motivation",
            },
            "answer": "C",
            "explain": ("Weber's law states the JND scales proportionally with stimulus magnitude "
                        "(here about 5%), rather than staying at a fixed absolute value. Adaptation "
                        "concerns sustained stimulation, and signal detection concerns willingness "
                        "to report, not discriminable difference."),
            "chapter": "FC6 · Perceive, think, react",
        },
        {
            "id": "fc6-perceive-think-react-p8",
            "q": "A clerk must hold the digits 4, 8, 1, 7, 2, 9, 5, 0 in working memory. The most effective way to raise effective capacity is to:",
            "choices": {
                "A": "Chunk them as 4817 and 2950 — two meaningful units instead of eight items",
                "B": "Repeat each digit separately with a pause between them",
                "C": "Keep staring at the digits until receptor adaptation stops competing for attention",
                "D": "Switch to System 1 and let the fast heuristic route store the digits",
            },
            "answer": "A",
            "explain": ("Working memory holds only a few items, but chunking packs more information "
                        "into each unit — the basis of phone-number grouping. Repeating items one by one "
                        "stays at eight items, adaptation is a receptor phenomenon, and System 1 is the "
                        "fast heuristic route, not a storage expansion."),
            "chapter": "FC6 · Perceive, think, react",
        },
    ],
    "fc9-cultural-and-social-differences.yml": [
        {
            "id": "fc9-cultural-and-social-differences-p10",
            "q": "A manager assumes that applicants from a certain region are lazy, and therefore rejects one of them. The assumption and the rejection are, in order:",
            "choices": {
                "A": "Prejudice, then stereotype",
                "B": "Stereotype, then discrimination",
                "C": "Discrimination, then prejudice",
                "D": "Ethnocentrism, then cultural relativism",
            },
            "answer": "B",
            "explain": ("Stereotype is the belief/cognition about a group; prejudice is the negative "
                        "feeling; discrimination is the unequal behavior. Here the belief drives an "
                        "action, so stereotype → discrimination. Relativism and ethnocentrism concern "
                        "judging cultures, not individuals."),
            "chapter": "FC9 · Cultural and social differences",
        },
        {
            "id": "fc9-cultural-and-social-differences-p11",
            "q": "In the health belief model, whether a patient with a chronic condition seeks care depends mainly on:",
            "choices": {
                "A": "The prestige and bedside manner of the treating physician",
                "B": "The country's gross national income alone",
                "C": "The patient's genotype for drug metabolism",
                "D": "Perceived susceptibility, perceived severity, and the perceived benefits versus barriers of acting",
            },
            "answer": "D",
            "explain": ("The health belief model is a perceived-threat and perceived-efficacy model: "
                        "susceptibility, severity, benefits, and barriers (plus cues to action) predict "
                        "care-seeking. Income and clinician prestige are external context, not the "
                        "model's constructs."),
            "chapter": "FC9 · Cultural and social differences",
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
