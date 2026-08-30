#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/drill/part1-verbal.yml (25-item practice-only drill).

Standalone MCQs, no passages. Topics go deeper than the main part1-verbal bank:
analogy relations the main bank barely touches (collective nouns, numeric
prefixes, field-of-study pairs) and harder percent/comparison reading items.

Each item is authored as (correct text, [(wrong text, why-wrong note) x 3]).
Letters come from a fixed balanced sequence; the correct text is placed on the
target letter and the three notes are mapped to the three NON-answer letters in
ascending order, so the distractor dict can never hold the answer's letter.
"""
import os
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part1-verbal.yml"

# Balanced answer letters: A:7 B:6 C:6 D:6 (max 7).
LETTERS = ["A", "C", "B", "D", "B", "A", "D", "C", "A", "B", "D", "C",
           "B", "A", "C", "D", "A", "B", "C", "D", "A", "C", "B", "D",
           "A"]
assert len(LETTERS) == 25
assert Counter(LETTERS) == Counter({"A": 7, "B": 6, "C": 6, "D": 6})
assert max(Counter(LETTERS).values()) <= 7

# ---------------------------------------------------------------- analogies
# (stem, correct, [(wrong, note) x3], explain, relation)
ANALOGIES = [
    ("SERRATED : SMOOTH :: VACILLATING : ?",
     "resolute",
     [("unsteady", "Unsteady restates vacillating; the pair demands a contrast, as smooth contrasts with serrated."),
      ("hesitant", "Hesitant is a synonym of vacillating, not its opposite."),
      ("yielding", "Yielding describes giving way to others, which is not the firmness that opposes wavering.")],
     "Serrated and smooth are opposites, so the second pair must be opposites too: vacillating (wavering) is the opposite of resolute (firm).",
     "antonyms"),

    ("EPHEMERAL : TRANSIENT :: QUOTIDIAN : ?",
     "everyday",
     [("rare", "Rare is close to the opposite of quotidian, which names the ordinary daily round."),
      ("eternal", "Eternal describes endless duration; quotidian describes what recurs each day."),
      ("monthly", "Monthly names a different interval; quotidian specifically means daily.")],
     "Quotidian means belonging to every day, so it matches the synonym pair ephemeral/transient as everyday.",
     "synonyms"),

    ("GAGGLE : GEESE :: PRIDE : ?",
     "lions",
     [("peacocks", "The collective term for peacocks is a muster or an ostentation, not a pride."),
      ("wolves", "A group of wolves is a pack."),
      ("bees", "A group of bees is a swarm or a colony.")],
     "A gaggle is the collective term for geese, as a pride is the collective term for lions.",
     "collective noun : animal"),

    ("BAROMETER : PRESSURE :: ODOMETER : ?",
     "distance traveled",
     [("speed", "Speed is read on a speedometer, a separate instrument."),
      ("engine temperature", "Engine heat is read on a temperature gauge, not on an odometer."),
      ("fuel remaining", "A fuel gauge, not an odometer, reports how much fuel is left.")],
     "A barometer measures atmospheric pressure, as an odometer measures distance traveled.",
     "instrument : what it measures"),

    ("WARM : SCALDING :: COOL : ?",
     "frigid",
     [("tepid", "Tepid is only mildly warm, a lesser degree rather than a greater one."),
      ("damp", "Damp describes moisture, not temperature."),
      ("lukewarm", "Lukewarm sits near the mild end of the scale, the opposite direction from the pair.")],
     "Warm is to scalding as cool is to frigid: each second term is the extreme of the same scale as its partner.",
     "moderate degree : extreme degree"),

    ("PREFACE : BOOK :: OVERTURE : ?",
     "opera",
     [("curtain call", "A curtain call comes at the end of a performance, not at the start."),
      ("aria", "An aria is a solo number inside an opera, itself only a part."),
      ("libretto", "A libretto is the sung text of an opera, not its instrumental introduction.")],
     "A preface introduces a book, as an overture introduces an opera.",
     "introduction : work it opens"),

    ("POLYGLOT : LANGUAGES :: GOURMET : ?",
     "food",
     [("gardens", "A gardener or horticulturist, not a gourmet, is the expert on gardens."),
      ("music", "A trained musician or listener, not a gourmet, is the expert on music."),
      ("coins", "A numismatist, not a gourmet, is the expert on coins.")],
     "A polyglot is a person expert in languages, as a gourmet is a person expert in food.",
     "expert : field of expertise"),

    ("CASCADE : WATER :: AVALANCHE : ?",
     "snow",
     [("dune", "A dune is a stationary heap of sand, not a moving mass of it."),
      ("cloud", "A cloud is the source a storm draws on, not the rushing mass itself."),
      ("breeze", "A breeze is a light movement of air, a matter of strength rather than of substance.")],
     "A cascade is a rushing fall of water, as an avalanche is a rushing slide of snow.",
     "moving mass : what it is made of"),

    ("JOEY : KANGAROO :: CYGNET : ?",
     "swan",
     [("goose", "A young goose is a gosling."),
      ("duck", "A young duck is a duckling."),
      ("eagle", "A young eagle is an eaglet.")],
     "A joey is a young kangaroo, as a cygnet is a young swan.",
     "young animal : its adult"),

    ("ORNITHOLOGY : BIRDS :: ENTOMOLOGY : ?",
     "insects",
     [("words", "Etymology, the sound-alike trap, traces word origins."),
      ("reptiles", "Herpetology, not entomology, covers reptiles and amphibians."),
      ("humankind", "Anthropology studies humankind; the 'ant' at its start is only a false cue.")],
     "Ornithology is the study of birds, as entomology is the study of insects.",
     "field of study : its subject"),

    ("AFFABLE : SURLY :: GREGARIOUS : ?",
     "solitary",
     [("sociable", "Sociable is a synonym of gregarious, so the pair would not be opposites."),
      ("talkative", "Talkativeness concerns speech, while gregariousness concerns company."),
      ("timid", "Timidity is fear of risk, not a preference for being alone.")],
     "Affable and surly are opposites, so gregarious (fond of company) must pair with its opposite, solitary.",
     "antonyms"),

    ("BICENTENNIAL : 200 YEARS :: SESQUICENTENNIAL : ?",
     "150 years",
     [("1,000 years", "A millennium, not a sesquicentennial, is 1,000 years."),
      ("100 years", "A centennial is 100 years; the 'sesqui-' adds half as much again."),
      ("10 years", "A decennial event recurs every 10 years.")],
     "Bi- marks two centuries, so sesqui- (one and a half) marks 150 years, half as much again as a centennial.",
     "numeric prefix : quantity named"),

    ("POISON : ANTIDOTE :: INFECTION : ?",
     "antibiotic",
     [("analgesic", "An analgesic dulls pain; it does not act on the infection causing it."),
      ("vaccine", "A vaccine builds protection beforehand; it is not a remedy once infection is established."),
      ("antiseptic", "An antiseptic works on the surface of a wound and does not reach an established internal infection.")],
     "An antidote counteracts a poison, as an antibiotic counteracts an infection.",
     "problem : what counteracts it"),
]

# --------------------------------------------------- reading comprehension
# (stem with a short self-contained passage, correct, [(wrong, note) x3], explain)
RC = [
    ("Towns on the coast that kept a belt of mangroves between their shore and their fish pens "
     "recorded far less damage when a typhoon made landfall than neighboring towns that had "
     "cleared the same trees to build salt beds. Engineers credit the mangroves' tangled roots, "
     "which slow the incoming surge and hold the mud in place. The passage mainly explains:",
     "why towns that kept their mangroves suffered less storm damage",
     [("how salt beds are built on cleared coastal land",
       "Salt beds are mentioned only to say what the comparison towns did with the cleared ground."),
      ("why fish pens yield more when mangroves stand nearby",
       "The pens mark a location; the passage makes no claim about their yield."),
      ("how engineers plant mangrove seedlings along a shore",
       "Nothing about planting or engineering methods appears in the passage.")],
     "The passage sets up a comparison of storm damage and then assigns the cause: roots that slow the surge and hold the mud."),

    ("In a trial, half the volunteers were given a sugar tablet and told it was a new migraine "
     "medicine; the other half received the actual medicine. Both groups reported the same "
     "average drop in pain over four hours, so the investigators recorded no measurable "
     "advantage for the medicine. The findings best support which statement?",
     "Some of the relief patients report can come from expecting relief.",
     [("Sugar tablets act directly on migraine pain.",
       "The tablet has no medicinal action; the drop in that group is explained by belief, not chemistry."),
      ("Migraine medicines are useless in general.",
       "One trial of one medicine cannot carry so broad a claim."),
      ("The volunteers exaggerated their pain to please the investigators.",
       "Nothing shows exaggeration, and both groups fell by the same amount, so no group had reason to differ.")],
     "A sugar tablet matched the medicine, so the improvement shared by both groups must come from expectation rather than from the drug."),

    ("Reviewing a hospital chart, the resident wrote: 'Post-operative course uneventful; drains "
     "out on day two; tolerated diet; discharged ambulatory on day five.' A student reading the "
     "note for the first time asks what 'uneventful' means here. In the note, 'uneventful' "
     "most nearly means:",
     "free of complications",
     [("dull for the patient",
       "The word records the absence of problems, not the patient's boredom."),
      ("unusually rapid",
       "The note times the discharge but claims no unusual speed of recovery."),
      ("undertreated",
       "The note reports routine steps taken, not a shortfall in care.")],
     "In clinical shorthand 'uneventful' marks a recovery in which nothing went wrong."),

    ("A barangay's anti-dengue drive had four parts: weekly draining of water jars, larvicide "
     "dropped into unused tires, free testing at the health center every Wednesday, and a fine "
     "for households that ignored written warnings. By August the center reported cases down "
     "two thirds from the same month the year before, although the fine had been issued only "
     "once. According to the passage, all of the following were part of the drive EXCEPT:",
     "spraying insecticide inside homes",
     [("weekly draining of water jars",
       "Draining the jars is the first part named."),
      ("free testing at the health center every Wednesday",
       "The Wednesday testing is the third part named."),
      ("a fine for households that ignored written warnings",
       "The fine is the fourth part named, though it was issued only once.")],
     "The four named parts are the jars, the tires, the Wednesday testing, and the fine; spraying is never mentioned."),

    ("The auditor's report notes, without comment, that the agency bought 400 laptops for a "
     "staff of 120, that the purchase was split into three smaller orders just under the level "
     "that would require competitive bidding, and that delivery was accepted while the "
     "supplier's owner was abroad. The author's primary purpose is to:",
     "present facts whose pattern invites the reader to question the purchase",
     [("prove in court that the purchases were illegal",
       "The report records facts without comment and names no statute that was broken."),
      ("praise the agency for modernizing its equipment",
       "Nothing in the selection is approving; the numbers are set out as anomalies."),
      ("explain how competitive bidding is required by law",
       "Bidding appears only as a threshold the three orders stayed just under.")],
     "The author offers no judgment but stacks three odd details, leaving the reader to draw the inference."),

    ("A principal reported that after the school banned phones, average scores rose, and "
     "concluded that the phones were the cause. Records show, however, that during the same "
     "term the school cut class sizes by a third and raised the grade needed to pass. The "
     "principal's conclusion is weakened because:",
     "other changes that term could account for the rise in scores",
     [("average scores are never a fair measure of learning",
       "The flaw is the ignored rival explanation, not the choice of measure."),
      ("banning phones cannot possibly affect attention",
       "No such claim is made, and it would not touch the reasoning as stated."),
      ("the passing grade was raised after the scores were computed",
       "The passage places the change in the same term, not after the results.")],
     "Two other changes landed in the same term, so the rise cannot be credited to the ban alone."),

    ("A clinic's rule reads: any patient with a fever above 38.5 degrees and a rash of fewer "
     "than three days' duration must be seen the same day. Miko arrived on a Tuesday with a "
     "fever of 39.1 degrees and a rash that first appeared on the Sunday before. Which "
     "conclusion follows?",
     "Miko must be seen the same day.",
     [("Miko must be referred to a dermatologist.",
       "The rule says nothing about referral to a specialist."),
      ("Miko's fever is too low to qualify.",
       "39.1 degrees is above the 38.5-degree threshold the rule sets."),
      ("The rule does not apply because the rash is too recent.",
       "A rash first seen on Sunday is two days old on Tuesday, which the rule allows.")],
     "Both conditions hold: 39.1 exceeds 38.5, and a rash appearing on Sunday is two days old on Tuesday, fewer than three."),

    ("A city found that painting roofs white lowered indoor temperatures by about two degrees, "
     "because the coating reflected sunlight that dark roofs had absorbed. A barangay captain "
     "wants the same benefit for a row of warehouses whose walls, not roofs, take the "
     "afternoon sun. Applying the passage's principle, the most promising step is to:",
     "coat the sun-facing walls in a light reflective finish",
     [("paint the roofs white as well, since that is what worked downtown",
       "The roofs are not the surfaces taking the afternoon sun in this row of buildings."),
      ("install thicker curtains inside the offices",
       "The passage's mechanism is reflection from a surface, not added insulation."),
      ("plant trees between the warehouses and the street",
       "Tree shade works by blocking light rather than by reflecting it off a building surface.")],
     "The principle is that a light surface reflects the sun instead of absorbing it, so it belongs on whichever surface receives the sun."),

    ("The cooperative lent P480,000 to its members in the first quarter: P200,000 in April, "
     "P160,000 in May, and the rest in June. Repayments received in the same quarter totaled "
     "P300,000, of which P90,000 was interest. In June the cooperative lent:",
     "P120,000",
     [("P180,000",
       "That subtracts the quarter's repayments from the quarter's lending, though repayments are a separate flow."),
      ("P90,000",
       "That figure is the interest received during the quarter, not June's lending."),
      ("P280,000",
       "That removes only April's P200,000 from the quarter's total.")],
     "April and May account for P360,000 of the P480,000, leaving P120,000 for June; the repayment figures belong to a different flow."),

    ("The essay opens by describing a rice terrace as it looks at planting time, then explains "
     "how the terraces were cut and kept clear over four centuries, and closes by noting that "
     "young people are leaving the villages and that some walls already stand abandoned. The "
     "passage is organized chiefly by:",
     "moving from a present scene to its history and then to its likely future",
     [("listing problems and then proposing solutions",
       "No solution is proposed; the essay ends on the abandoned walls."),
      ("comparing two villages side by side",
       "Only one place is described throughout."),
      ("stating a thesis and answering objections to it",
       "No opposing argument is raised, so none is answered.")],
     "The three paragraphs run present, past, then prospect, which is the movement the answer names."),

    ("Although the mayor announced that the new pier would be finished by March, the engineer "
     "in charge kept two barges and a full crew on retainer through June and told the crew "
     "chief to keep the dredge fueled. The engineer's arrangements suggest that she:",
     "expected the March date to slip",
     [("planned to take on other projects once the pier was done",
       "The barges and the dredge are tied to the pier itself, not to other work."),
      ("doubted that the pier would ever be built at all",
       "Holding a crew ready is planning for the job, not doubt that the job exists."),
      ("had already finished the work ahead of schedule",
       "A finished pier would leave no reason to keep a dredge fueled on retainer.")],
     "Retainers and a fueled dredge running into June only make sense if she did not believe the March completion date."),

    ("Because antibiotics kill bacteria rather than viruses, doctors who prescribe them for "
     "colds do nothing for the patient while helping the bacteria in that patient's body "
     "survive the drug. Health agencies therefore urge physicians to reserve the medicines for "
     "infections they can confirm are bacterial. The passage is chiefly concerned with:",
     "why prescribing antibiotics for colds is both useless and harmful",
     [("how bacteria become resistant to antibiotics",
       "Resistance is named as the result, not explained as a process."),
      ("the cost of antibiotics to public health budgets",
       "Cost is never raised in the passage."),
      ("the difference between colds and influenza",
       "Influenza is never mentioned.")],
     "Both halves of the answer appear: the prescription does nothing for a viral cold and it trains bacteria to survive the drug."),
]


def build():
    pool = []
    for stem, right, wrongs, explain, rel in ANALOGIES:
        assert "::" in stem and stem.strip().endswith("?"), stem
        pool.append(dict(q=stem, right=right, wrongs=wrongs, explain=explain,
                         chapter="analogies", rel=rel))
    for stem, right, wrongs, explain in RC:
        assert len(stem.split()) >= 40, len(stem.split())
        pool.append(dict(q=stem, right=right, wrongs=wrongs, explain=explain,
                         chapter="reading-comprehension", rel="rc"))
    assert len(pool) == 25, len(pool)
    assert len([p for p in pool if p["chapter"] == "analogies"]) == 13
    assert len([p for p in pool if p["chapter"] == "reading-comprehension"]) == 12
    assert len({p["q"] for p in pool}) == 25, "duplicate stems"
    # every analogy must hold reading the pairs in both directions
    for stem, right, wrongs, explain, rel in ANALOGIES:
        assert "::" in stem and right and len(wrongs) == 3

    items = []
    for idx, (p, letter) in enumerate(zip(pool, LETTERS), start=1):
        wrong_letters = [L for L in "ABCD" if L != letter]
        assert len(p["wrongs"]) == 3
        choices, distractors = {}, {}
        choices[letter] = p["right"]
        for L, (text, note) in zip(wrong_letters, p["wrongs"]):
            choices[L] = text
            distractors[L] = note
        assert len(set(choices.values())) == 4, (idx, choices)
        assert letter not in distractors
        items.append({
            "id": "nmat-d-p1v-%03d" % idx,
            "q": " ".join(p["q"].split()),
            "choices": {L: choices[L] for L in "ABCD"},
            "answer": letter,
            "explain": p["explain"],
            "distractors": {L: distractors[L] for L in wrong_letters},
            "chapter": p["chapter"],
        })
    return {
        "exam": "nmat",
        "section": "drill-part1-verbal",
        "label": "Verbal drill",
        "subject": "verbal",
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
