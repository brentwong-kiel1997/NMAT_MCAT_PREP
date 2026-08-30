#!/usr/bin/env python3
"""Generate content/exam-bank/mcat/drill/cars.yml (2 original passages, 10 items).

Both passages are written for this bank (science-policy and humanities
arguments) and are 450-550 words each, asserted at generation time.

Every option list is written [correct, w1, w2, w3]; build() places the correct
option on the requested answer letter and the three wrong options on the
remaining letters in ascending order, so `distractors` keys are exactly the
three letters that are NOT the answer.

Chapters: CARS items are tagged with the CARS subject's own skill chapters
(foundations-of-comprehension / reasoning-within-the-text /
reasoning-beyond-the-text), which are the ids the content library defines.
"""
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/mcat/drill/cars.yml"
LETTERS = "ABCD"
IDPREFIX = "mcat-d-ca"
FOUND = "foundations-of-comprehension"
WITHIN = "reasoning-within-the-text"
BEYOND = "reasoning-beyond-the-text"


def words(text):
    return len(text.split())


def build(n, q, correct, wrongs, key, explain, chapter, passage_id):
    assert key in LETTERS, (n, key)
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
    assert key not in distractors
    return {
        "id": "%s-%03d" % (IDPREFIX, n),
        "q": q,
        "choices": choices,
        "answer": key,
        "explain": explain,
        "distractors": distractors,
        "chapter": chapter,
        "passage_id": passage_id,
    }


P01 = """A decade ago a large consortium set out to repeat one hundred published psychology
experiments and succeeded with fewer than half of them. The public reaction blamed sloppy
statistics, careerism, and in the darker corners of the commentary, fraud. Those explanations
are not useless, but they all locate the problem inside individual researchers. The deeper
difficulty is structural: the profession rewards discovery and does not reward verification, and
pre-registration is the one widely proposed reform aimed squarely at that imbalance rather than
at the character of the people caught in it.

The mechanics are simple. Before collecting data, a researcher writes down the hypothesis, the
sample size, and the analysis plan, and lodges the document with an independent registry. A
journal can then accept the study in principle, so that publication turns on whether the test was
fair rather than on how the result came out. This severs the link between the attractiveness of a
finding and its chances of appearing in print, which is the link that produces the familiar
pathologies: shifting the analysis until a threshold is crossed, presenting a guess dressed up as
a prediction, and leaving inconvenient results in a drawer.

The standing objection is that pre-registration is bureaucracy, and that it would smother the
exploratory work from which discoveries actually come. There is something to this. Serendipity is
not a decoration in the history of science; unanticipated patterns have opened more fields than
most planned programs of research. But the objection misreads what registration forbids. It does
not forbid exploration; it requires that exploration be labeled as such. A finding noticed in the
course of looking for something else may be reported freely, provided it is described as a
suggestion rather than as a confirmation. What is illegitimate is running a trawl through the data
and then narrating it as though a hypothesis had been tested in advance, because the ordinary
logic of statistical evidence depends on that distinction being real.

Medicine has already run the experiment on a larger scale. When registration of clinical trials
became a condition of publication, researchers comparing registered plans with published papers
found that outcomes had quietly changed: primary measures swapped for flattering ones, failures
unreported. In several drug classes the published literature looked considerably more effective
than the registered record once the missing trials were accounted for. That is not an argument
that medical researchers are worse than psychologists; it is evidence that the incentive is
sufficiently general to distort anyone exposed to it, and that closing the loophole changes what
gets reported.

Critics reply that registration cannot fix everything, and they are right. It does nothing about
small samples already collected, nothing about measures that are intrinsically vague, and nothing
about reviewers who dislike a conclusion. But the standard for a reform is not perfection; it is
whether it beats the alternative. The alternative asks readers to take the analysis on faith from
the one party with the strongest interest in the outcome. A field that cannot distinguish its
reliable results from its attractive ones is not accumulating knowledge. It is accumulating
publications."""

P02 = """Calls for museums to return contested objects are usually described as a collision between
scholarship and justice, with curators defending the care of collections and activists demanding
their surrender. The description is wrong in a revealing way. The dispute is not about whether
objects should be cared for, or even chiefly about where they should sit. It is a disagreement
between two answers to the question of what a museum is, and only one of those answers can
survive an honest account of how many great collections were assembled.

The defense runs as follows. Encyclopedic museums gather the world's productions under one roof
and allow a visitor to compare them side by side, free from local politics and, in recent memory,
free from the wars that have emptied whole regions of their patrimony. Objects of this kind belong
to everyone, so the argument concludes, and are safest in institutions outside every claim upon
them. There is real force in that picture, and no serious participant in the debate proposes
shipping the holdings into the sea. Its weakness is that it never looks at how the objects
arrived. The bronzes taken in a punitive raid on Benin in 1897, the marbles removed from the
Parthenon under a permit whose authority is still argued over, the ancestral remains collected as
specimens: these entered their present homes as the proceeds of force or of maneuvers that no
museum today would defend if described plainly. An institution cannot claim the moral standing of
universality while resting on a founding act of dispossession, however scrupulous its
conservators have been since.

The safety argument deserves better treatment than it usually gets, because it is not made in bad
faith. Works have been destroyed where they stood, and curators who say so are reporting their
professional experience. But safety functions in this debate as an assumption about capability
rather than as a principle, and capability is not fixed. It can be built, by long-term loans, by
shared custody, by training conservators and funding stores in the place a work came from.
Refusing to consider any of these arrangements converts a legitimate concern into a
rationalization of possession, which is why the argument reads so differently depending on who is
permitted to make it.

Something subtler is lost as well. A bronze in Benin was not merely a sculpture to be admired but
part of a court's record and of obligations that ran between people; a museum can preserve the
object and cannot preserve the obligations. That is a genuine cost of return, and it cuts the
other way too: an object deposited in a store without climate control serves neither the claimant
nor the work. Honesty requires admitting both.

The question to put to any museum is therefore not who can care for a thing but who has the right
to decide. Care is a means; authority is the issue. Museums that answer plainly will not find
their galleries emptied. They will discover that a return here and a loan there leaves the rest of
the collection more credible than before, because an object whose arrival can be explained is a
better instrument of understanding than one whose title is contested and quietly passed over."""

# answer-letter plan (10 items): A:3 B:3 C:2 D:2 -> nothing over 3
KEYS = ["B", "C", "A", "D", "B", "A", "C", "B", "D", "A"]
assert len(KEYS) == 10

p1_items = [
    build(1,
          "The central argument of the passage is that",
          "pre-registration matters because it changes the incentives that reward discovery over "
          "verification, rather than because researchers are personally at fault",
          [("exploratory research should be curtailed, since it is the principal source of "
            "unreliable findings",
            "The author defends exploration and asks only that it be labeled as exploratory."),
           ("the replication failures of recent decades were caused mainly by outright fraud",
            "The opening paragraph treats fraud as a darker and less adequate explanation than the "
            "structural one."),
           ("statistical technique cannot reveal a false hypothesis, so reform must begin with "
            "better training",
            "Statistical logic is presented as sound but dependent on a distinction the current "
            "system erodes.")],
          KEYS[0],
          "Paragraph one states the thesis directly: the difficulty is structural, and "
          "pre-registration is the reform aimed at the imbalance between discovering and "
          "verifying. The rest of the passage defends that claim.",
          FOUND, "mcat-d-cars-p01"),

    build(2,
          "The author discusses the effect of trial registration on the published drug literature "
          "primarily in order to",
          "show that the incentive problem has measurable consequences rather than being a "
          "speculation about character",
          [("suggest that medical researchers are less honest than their counterparts in psychology",
            "The author explicitly denies that this is the point of the example."),
           ("concede that registration cannot address every weakness of the research system",
            "That concession comes later, in a separate move about samples, measures and "
            "reviewers."),
           ("argue that clinical medicine should be exempt from the reforms applied elsewhere",
            "The example is offered as evidence that the reform works there, not that it should "
            "be withdrawn.")],
          KEYS[1],
          "The paragraph ends by saying the example shows the incentive is general and that closing "
          "the loophole changes what gets reported, which is an empirical point about consequences.",
          WITHIN, "mcat-d-cars-p01"),

    build(3,
          "The author would most likely agree with which of the following statements?",
          "An unexpected finding published as a suggestion is less dangerous than the same finding "
          "presented as though it had been a planned confirmation",
          [("Journals should give priority to studies whose results are striking rather than "
            "representative",
            "The passage attacks the link between how striking a result is and whether it is "
            "published."),
           ("Sample sizes in psychology are generally adequate for the questions asked",
            "The author lists small samples among the things registration does not fix, implying "
            "they are a live problem."),
           ("Research practice should be left to the professional judgment of individual "
            "investigators",
            "The whole argument favors an external commitment made before data are collected.")],
          KEYS[2],
          "Paragraph three distinguishes a freely reported suggestion from a data trawl narrated as "
          "a confirmation, and locates the harm in the second.",
          WITHIN, "mcat-d-cars-p01"),

    build(4,
          "Which finding, if true, would most weaken the author's argument for pre-registration?",
          "Studies that were registered and faithfully reported fail to replicate at about the same "
          "rate as unregistered studies",
          [("Some researchers describe the registration process as burdensome and slow",
            "The author already concedes friction, so this would not touch the central claim."),
           ("Unregistered studies are more likely to appear in highly selective journals",
            "That supports the claim that the reward system favors appearance over verification."),
           ("Registration is currently required in only a few fields of research",
            "The passage notes medicine has already adopted it, so this would not undercut the "
            "evidence.")],
          KEYS[3],
          "The argument's payoff is that registration improves the reliability of what is "
          "reported. Equal replication rates for registered and unregistered work would remove that "
          "payoff.",
          BEYOND, "mcat-d-cars-p01"),

    build(5,
          "The author concedes to opponents of pre-registration that",
          "some important discoveries have come from patterns investigators did not anticipate in "
          "advance",
          [("the file-drawer problem is largely a myth confined to a few laboratories",
            "The passage presents unreported results as one of the standard pathologies."),
           ("statistical evidence cannot distinguish generating a hypothesis from testing one",
            "The author insists that this distinction is real and that the logic of evidence "
            "depends on it."),
           ("replication failures have been concentrated in a single subfield",
            "No such restriction is offered; the clinical example is meant to generalize the "
            "problem.")],
          KEYS[4],
          "Paragraph three grants that serendipity is not a decoration and that unanticipated "
          "patterns have opened fields, before rejoining that exploration must be labeled as such.",
          FOUND, "mcat-d-cars-p01"),
]

p2_items = [
    build(6,
          "The primary purpose of the passage is to",
          "argue that repatriation disputes turn less on conservation than on who holds the right "
          "to decide the fate of an object",
          [("show that encyclopedic museums should be dismantled and their holdings dispersed",
            "The author says plainly that museums answering honestly will not see their galleries "
            "emptied."),
           ("defend the ideal of the universal museum against narrowly nationalist claims",
            "The passage criticizes that ideal for resting on acquisitions it will not describe "
            "plainly."),
           ("document recent improvements in conservation capacity outside Europe",
            "Capacity is mentioned as something that can be built, not as the passage's subject.")],
          KEYS[5],
          "The closing paragraph states the governing question, who has the right to decide, and "
          "sets it against the question of who can care for an object.",
          FOUND, "mcat-d-cars-p02"),

    build(7,
          "The author mentions the Benin bronzes and the Parthenon marbles primarily in order to",
          "show that the universal-museum claim rests on acquisitions whose own legitimacy is in "
          "dispute",
          [("indicate that these works have deteriorated badly in their present locations",
            "The passage's complaint concerns how they were acquired, not their condition."),
           ("recommend that museums from now on collect only from living artists",
            "Nothing in the passage addresses future collecting policy."),
           ("establish that such works would be safer in the regions they came from",
            "The author treats regional safety as uncertain and as something that can be built.")],
          KEYS[6],
          "The examples follow the statement that the defense never examines how the objects "
          "arrived, and they are described as proceeds of force or of contested permission.",
          WITHIN, "mcat-d-cars-p02"),

    build(8,
          "The author's response to the safety argument depends on the assumption that",
          "a legitimate concern about physical security can be addressed without also settling the "
          "question of possession permanently in the holder's favor",
          [("objects in European museums are currently in serious physical danger",
            "The author grants that curators report real experience of loss and calls the argument "
            "good faith."),
           ("long-term loans are the only arrangement a source nation could reasonably accept",
            "Loans are listed alongside shared custody and capacity-building as possible "
            "arrangements."),
           ("source nations have declined every offer of collaboration made so far",
            "The passage makes no claim about what has been offered or refused.")],
          KEYS[7],
          "Paragraph three allows that safety is a genuine concern but insists it is not a "
          "principle; capability can be built, so it cannot operate as a permanent veto.",
          WITHIN, "mcat-d-cars-p02"),

    build(9,
          "Based on the passage, which policy would the author most likely support?",
          "Transferring legal title to a claimant nation while the works remain on loan to the "
          "museum until local conservation facilities are ready",
          [("Immediate return of every object with a contested title, regardless of the "
            "conservation consequences",
            "The author warns that depositing a work without proper care serves neither the "
            "claimant nor the object."),
           ("Retention of all contested works, with digital reproductions offered in place of "
            "returns",
            "This leaves the decision of authority untouched, which the passage identifies as the "
            "real question."),
           ("Sale of contested works to whichever institution bids highest for them",
            "The passage treats these objects as carrying obligations that a market transaction "
            "does not address.")],
          KEYS[8],
          "The author wants authority settled in favor of the claimant while acknowledging that "
          "care has to be built; staged transfer with continued loans combines both commitments.",
          BEYOND, "mcat-d-cars-p02"),

    build(10,
          "The author's prediction that museums which answer the question plainly \"will not find "
          "their galleries emptied\" functions chiefly to",
          "rebut the assumption that acknowledging a contested title must end a museum's public "
          "purpose",
          [("concede that most objects in such museums have unimpeachable titles",
            "The passage has just argued that several foundational acquisitions are indefensible."),
           ("predict that attendance will rise once repatriations begin",
            "Attendance is never mentioned; the point is about credibility, not visitor numbers."),
           ("imply that arranging a loan is administratively simpler than arranging a return",
            "No comparative claim about administrative difficulty is made anywhere in the "
            "passage.")],
          KEYS[9],
          "The sentence pairs the fear of an emptied gallery with the claim that returns and loans "
          "make the remaining collection more credible, which answers a practical objection rather "
          "than conceding it.",
          WITHIN, "mcat-d-cars-p02"),
]

def paragraphs(raw):
    """Collapse intra-paragraph wrapping, keep blank-line paragraph breaks.

    The exam template renders passage text with `splitlines` into <p> tags, so
    paragraph breaks must survive as real newlines.
    """
    return "\n\n".join(" ".join(p.split()) for p in raw.strip().split("\n\n") if p.strip())


passages = [
    {"id": "mcat-d-cars-p01", "text": paragraphs(P01), "chapter": FOUND, "items": p1_items},
    {"id": "mcat-d-cars-p02", "text": paragraphs(P02), "chapter": FOUND, "items": p2_items},
]

doc = {
    "exam": "mcat",
    "section": "drill-cars",
    "label": "CARS drill",
    "subject": "cars",
    "block": "cars",
    "_drill": True,
    "items_expected": 10,
    "items": [],
    "passages": passages,
}
for p in passages:
    n = words(p["text"])
    assert 450 <= n <= 550, (p["id"], n)
    assert len(p["items"]) == 5, (p["id"], len(p["items"]))
    for i in p["items"]:
        assert i["passage_id"] == p["id"]
all_items = [i for p in passages for i in p["items"]]
assert len(all_items) == 10 == doc["items_expected"]
assert len({i["id"] for i in all_items}) == 10
letters = Counter(i["answer"] for i in all_items)
assert max(letters.values()) <= 3, letters
assert {i["chapter"] for i in all_items} <= {FOUND, WITHIN, BEYOND}
print("passage word counts:", {p["id"]: words(p["text"]) for p in passages})

with open(OUT, "w") as fh:
    yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True, width=100)

print("wrote", OUT)
print("answers:", dict(sorted(letters.items())))
print("chapters:", dict(Counter(i["chapter"] for i in all_items)))
