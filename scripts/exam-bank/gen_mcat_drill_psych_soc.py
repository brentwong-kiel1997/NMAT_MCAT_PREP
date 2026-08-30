#!/usr/bin/env python3
"""Generate content/exam-bank/mcat/drill/psych-soc.yml (30 practice-only items).

Drill bank weighted toward what the scored Psych/Soc bank underrepresents:
research-methods scenarios (design, validity, bias, inference) rather than
term-matching, plus applied perception, social and sociological scenarios.

Every option list is written [correct, w1, w2, w3]; build() places the correct
option on the requested answer letter and the three wrong options on the
remaining letters in ascending order, so `distractors` keys are exactly the
three letters that are NOT the answer. Quantitative stems recompute their
numbers a second way before the option text is built.
"""
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/mcat/drill/psych-soc.yml"
LETTERS = "ABCD"
IDPREFIX = "mcat-d-ps"


def calc(n, got, want, rel=2e-3):
    assert abs(got - want) <= rel * max(1.0, abs(want)), (n, got, want)
    return got


def build(n, q, correct, wrongs, key, explain, chapter):
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
        "passage_id": "",
    }


# answer-letter plan (30 items): A:7 B:8 C:8 D:7
KEYS = (["B", "A", "C", "D"] +
        ["D", "B", "A", "C"] +
        ["C", "D", "B", "A"] +
        ["A", "C", "D", "B"] +
        ["B", "D", "A", "C"] +
        ["C", "A", "B", "D"] +
        ["D", "B", "C", "A"] +
        ["B", "C"])
assert len(KEYS) == 30

PSY = "psychology"
SOC = "sociology-and-anthropology"

items = []

# ------------------------------------------------------- 1-12 research methods
items.append(build(
    1,
    "A researcher randomly assigns one group of volunteers to sleep 4 hours and another to sleep "
    "8 hours, then measures how quickly each group presses a button in response to a tone. In this "
    "study, what are the independent and dependent variables?",
    "Sleep duration is the independent variable and reaction time is the dependent variable",
    [("Reaction time is the independent variable and sleep duration is the dependent variable",
      "Reverses the two; reaction time is measured, not manipulated."),
     ("Sleep duration is the independent variable and the volunteers are the dependent variable",
      "Volunteers are the units of study, not the measured outcome."),
     ("Reaction time is the independent variable and sleep is a confound",
      "Sleep is manipulated by random assignment, so it cannot be a confound in this design.")],
    KEYS[0],
    "The independent variable is what the experimenter manipulates (hours of sleep allowed); the "
    "dependent variable is what is measured as the outcome (button-press latency).",
    PSY))

items.append(build(
    2,
    "In a sleep-deprivation study, the 4-hour group is tested at 11 p.m. and the 8-hour group at "
    "9 a.m. What is the most serious threat to the validity of the conclusion that sleep loss "
    "slowed reaction time?",
    "Time of day is confounded with the independent variable, so it could account for the "
    "difference in performance",
    [("Reaction time is not a valid measure of alertness",
      "The measure itself is well established; the problem is the unbalanced testing schedule."),
     ("Random assignment makes any difference uninterpretable",
      "Random assignment strengthens causal inference; the flaw here is the systematic scheduling "
      "difference."),
     ("The sample size is too small to compute a mean",
      "Nothing in the stem indicates a sample-size problem.")],
    KEYS[1],
    "Two variables change together across groups, so the design cannot tell whether sleep loss or "
    "circadian position produced the slower responses. That uncontrolled co-variation is a "
    "confound and it damages internal validity.",
    PSY))

items.append(build(
    3,
    "A public-health database finds that districts selling more ice cream have more drownings. "
    "Which inference is best supported?",
    "The association is probably explained by a third variable, such as hot weather driving both "
    "swimming and ice-cream sales",
    [("Ice cream consumption causes risky swimming",
      "No mechanism is offered and the design is observational, so a causal claim is unwarranted."),
     ("Ice cream sales and drownings are unrelated because the correlation is coincidental",
      "A consistent population-level association is real; the question is what produces it."),
     ("Drownings cause people to buy more ice cream",
      "Reverse causation is not plausible here and is not the best-supported reading of the data.")],
    KEYS[2],
    "Observational correlations admit a third-variable explanation. Summer heat raises both "
    "swimming (and drowning risk) and ice-cream purchases, which is the standard spuriousness "
    "pattern.",
    PSY))

items.append(build(
    4,
    "A study reports that it measured stress as the concentration of cortisol in a saliva sample "
    "collected on waking. This is an example of which methodological feature?",
    "An operational definition of the dependent variable",
    [("A double-blind procedure", "Blinding concerns who knows the condition, not how stress is "
                                  "quantified."),
     ("A manipulation check", "A manipulation check verifies that the independent variable changed "
                              "the intended state."),
     ("Random assignment", "Random assignment concerns how participants are placed in conditions.")],
    KEYS[3],
    "Turning 'stress' into a measurable quantity (waking salivary cortisol) is an operational "
    "definition.",
    PSY))

items.append(build(
    5,
    "A memory study recruits all of its participants from one university's introductory psychology "
    "course and reports a large effect. What is the main limitation on the conclusion?",
    "External validity is limited because the convenience sample may not represent the wider "
    "population",
    [("Internal validity is limited because participants were not randomly assigned",
      "The concern described is about who was sampled, not about how conditions were assigned."),
     ("The effect cannot be replicated in principle",
      "Convenience sampling affects generalization, not the possibility of replication."),
     ("The study violates the requirement of informed consent",
      "Standard recruitment from a subject pool with consent raises no such violation.")],
    KEYS[4],
    "A sample drawn from a narrow, unrepresentative pool constrains how far the finding "
    "generalizes, which is external validity.",
    PSY))

items.append(build(
  6,
  "In a trial of a new anxiolytic, neither the participants nor the researchers who rate symptoms "
  "know who received the drug and who received an identical-looking placebo. What is the chief "
  "purpose of this double-blind design?",
    "To prevent participant and experimenter expectancy from influencing the reported outcome",
    [("To make the sample representative of the target population",
      "Representativeness is a sampling matter, not a blinding matter."),
     ("To guarantee that the drug and placebo have identical chemical effects",
      "Blinding does not change pharmacology; it controls expectations about it."),
     ("To allow the researchers to infer causation without a control group",
      "A placebo control group is still required, and blinding never substitutes for one.")],
    KEYS[5],
    "Blinding both parties controls demand and expectation effects on the part of participants and "
    "observer bias on the part of raters.",
    PSY))

items.append(build(
    7,
    "A bathroom scale reads exactly 2 kg high on every measurement but is perfectly consistent from "
    "day to day. What does this instrument demonstrate?",
    "High reliability but low validity",
    [("High validity but low reliability", "Reverses the two properties; a consistent bias is not "
                                           "accuracy."),
     ("Both low reliability and low validity", "A perfectly consistent reading is by definition "
                                               "reliable."),
     ("High reliability and high validity", "Consistency does not establish that the scale "
                                            "measures the true value.")],
    KEYS[6],
    "Reliability is consistency across repeated measurements; validity is agreement with the true "
    "value. A systematic offset preserves the first and destroys the second.",
    PSY))

items.append(build(
    8,
    "A researcher concludes that a new therapy works, when in fact the observed difference arose "
    "by chance. What kind of error is this?",
    "A Type I error, a false positive",
    [("A Type II error, a false negative", "A Type II error is failing to detect an effect that "
                                           "exists, the opposite outcome."),
     ("A confounding error", "Confounding is a design flaw, not a statistical decision error."),
     ("A selection bias", "Selection bias concerns how participants entered the sample.")],
    KEYS[7],
    "Rejecting a true null hypothesis is a Type I (alpha) error: reporting an effect that is not "
    "there.",
    PSY))

items.append(build(
    9,
    "A study reports p = 0.03 for the difference between two group means. Which statement "
    "correctly interprets this value?",
    "If the null hypothesis were true, data at least this extreme would occur about 3% of the "
    "time",
    [("There is a 3% probability that the null hypothesis is true",
      "A p-value is not the probability of a hypothesis; it is computed assuming the null holds."),
     ("The effect size is 3% of the standard deviation",
      "p-values say nothing about the magnitude of the effect."),
     ("The result will replicate in 97% of future samples",
      "Replication probability is not given by p; this is a common misreading.")],
    KEYS[8],
    "By definition, p is the probability of obtaining data at least this extreme given that the "
    "null hypothesis is true.",
    PSY))

items.append(build(
    10,
    "Participants in a study of 'cognitive performance under distraction' correctly guess the "
    "hypothesis and deliberately slow down in the control condition. Which threat does this best "
    "illustrate?",
    "Demand characteristics",
    [("Observer bias", "Observer bias is distortion by the researchers recording behavior, not by "
                       "participants."),
     ("Attrition bias", "Attrition involves participants dropping out differentially."),
     ("Regression to the mean", "Regression concerns extreme scores moving toward the average on "
                                "retesting.")],
    KEYS[9],
    "When participants infer the hypothesis and act to confirm or defy it, the study has demand "
    "characteristics.",
    PSY))

items.append(build(
    11,
    "A study of moral decision-making tells participants they are administering shocks but "
    "debriefs them fully afterward, revealing that no real shocks were delivered. What does the "
    "debriefing accomplish?",
    "It removes deception and addresses any distress, satisfying the ethical requirement that "
    "accompanies the use of deception",
    [("It substitutes for informed consent, which can then be skipped",
      "Informed consent is still required; debriefing supplements rather than replaces it."),
     ("It converts the study into an observational design",
      "The design remains experimental; debriefing is an ethical procedure, not a design change."),
     ("It eliminates the need for institutional review",
      "Review by an ethics board is required before any deceptive research begins.")],
    KEYS[10],
    "Deception is permissible only with a plan for thorough debriefing, which restores the "
    "participant's understanding and addresses lingering harm.",
    PSY))

items.append(build(
    12,
    "Participants asked how often they exercise report far more activity than their activity "
    "trackers record. Which bias best explains the discrepancy?",
    "Social desirability bias in self-report",
    [("Acquiescence bias", "Acquiescence is agreeing with items regardless of content; it does not "
                           "explain inflating exercise."),
     ("Hawthorne effect", "The Hawthorne effect is altered behavior from being observed, not "
                          "misreporting on a questionnaire."),
     ("Selection bias", "Selection bias concerns who is in the sample, not how they answer.")],
    KEYS[11],
    "Over-reporting socially valued behavior is the classic social desirability bias, which is why "
    "objective measures are often paired with self-report.",
    PSY))

# ------------------------------------------------- 13-18 methods, perception
items.append(build(
    13,
    "A researcher spends two years living in a fishing village, joining its cooperative labor and "
    "recording ceremonies in field notes, in order to describe the community's economic norms from "
    "the inside. Which method and limitation apply?",
    "Participant observation; findings rest on one community and resist statistical "
    "generalization",
    [("Cross-sectional survey; the researcher cannot establish temporal ordering",
      "No survey is described, and the limitation named does not belong to that method."),
     ("Experiment; participants cannot be randomly assigned to a village",
      "There is no manipulation or control condition here, so it is not an experiment."),
     ("Longitudinal cohort study; the sample is too small to compute a correlation",
      "A cohort study tracks a defined sample over time with repeated measures, which is not what "
      "is described.")],
    KEYS[12],
    "Living inside a group while taking part in its activities is ethnographic participant "
    "observation: rich, context-bound description with limited generalizability.",
    SOC))

items.append(build(
    14,
    "A researcher records playground aggression by watching children from behind a one-way mirror "
    "without intervening. Compared with a laboratory experiment, what tradeoff does this method "
    "make?",
    "Greater ecological validity but less control over extraneous variables",
    [("Greater control over extraneous variables but less ecological validity",
      "That is the laboratory's advantage, not the field observation's."),
     ("Greater internal validity but a smaller sample",
      "Field observation typically weakens internal validity because nothing is manipulated."),
     ("More random assignment but more demand characteristics",
      "No assignment occurs in naturalistic observation, and children do not know they are being "
      "studied here.")],
    KEYS[13],
    "Observing behavior where it naturally occurs raises realism (ecological validity) but removes "
    "the experimenter's control over conditions.",
    PSY))

# 15 income skew
items.append(build(
    15,
    "In a town, most households earn between $30,000 and $60,000, while a handful of households "
    "earn above $2 million. What is the relationship between the mean and the median household "
    "income?",
    "The mean exceeds the median because the distribution is right-skewed",
    [("The median exceeds the mean because the distribution is right-skewed",
      "Right-skew pulls the mean above the median, not below it."),
     ("The mean and median are equal because income is a continuous variable",
      "Continuity does not imply symmetry; a few extreme values dominate the mean."),
     ("The mean falls below every observation because of the outliers",
      "A mean cannot be below all of the values it summarizes.")],
    KEYS[14],
    "A long right tail inflates the mean while the median stays with the bulk of households, so "
    "mean > median in a right-skewed income distribution.",
    "fc10-stratification-and-resources"))

# 16 signal detection
items.append(build(
    16,
    "A radiologist adopts a very lenient criterion for calling a lesion present on a scan. Compared "
    "with a strict criterion, what change in signal-detection outcomes follows?",
    "More hits and more false alarms",
    [("Fewer hits and fewer false alarms", "That is what a strict, conservative criterion "
                                           "produces."),
     ("Fewer hits and more false alarms", "A lenient criterion raises, not lowers, the hit rate."),
     ("More hits and no change in false alarms", "Hits and false alarms move together when only "
                                                 "the criterion shifts, because sensitivity is "
                                                 "unchanged.")],
    KEYS[15],
    "Shifting the response criterion changes the response pattern without changing sensitivity "
    "(d'): a liberal criterion says 'present' more often, raising both hits and false alarms.",
    "6a-sensing-the-environment"))

# 17 top-down processing
items.append(build(
    17,
    "A faded road sign reads only 'SP', but drivers reliably report seeing 'STOP' because of the "
    "octagonal shape and the intersection context. Which perceptual process does this show?",
    "Top-down processing driven by context and expectation",
    [("Bottom-up processing driven by feature detection",
      "The missing letters supply no features to detect; the completion comes from above."),
     ("Sensory adaptation", "Adaptation is a reduced response to a constant stimulus over time."),
     ("Difference threshold", "A threshold concerns detecting a change in intensity, not filling "
                              "in missing letters.")],
    KEYS[16],
    "Context and prior knowledge are filling in sensory gaps, which is top-down (concept-driven) "
    "perception.",
    "6b-making-sense-of-the-environment"))

# 18 Weber's law
jnd18 = calc(18, 0.10 * 500.0, 50.0)
items.append(build(
    18,
    "A person can just notice that a 100 g weight is heavier than a 90 g reference. According to "
    "Weber's law, what difference from a 500 g reference would that person just barely notice?",
    "%.0f g" % jnd18,
    [("10. g", "Applied the absolute difference from the first comparison instead of the Weber "
               "fraction."),
     ("100. g", "Doubled the reference weight's JND, using a fraction of 0.20."),
     ("490. g", "Reported the reference weight itself rather than the increment above it.")],
    KEYS[17],
    "The Weber fraction is 10/100 = 0.10, so the JND scales with the reference: 0.10 x 500 g = "
    "%.0f g." % jnd18,
    "fc6-perceive-think-react"))

# ------------------------------------------------------- 19-25 learning/social
items.append(build(
    19,
    "A dog salivates when meat powder is placed in its mouth. A bell is rung just before the meat "
    "powder on many trials, until the dog salivates at the bell alone. In this preparation, what is "
    "the unconditioned stimulus?",
    "The meat powder",
    [("The bell", "The bell begins as a neutral stimulus and becomes the conditioned stimulus."),
     ("Salivation to the meat powder", "That is the unconditioned response, not the stimulus that "
                                       "elicits it."),
     ("Salivation to the bell", "That is the conditioned response, established by pairing.")],
    KEYS[18],
    "Meat powder elicits salivation with no learning, so it is the unconditioned stimulus; the "
    "paired bell becomes the conditioned stimulus.",
    "6c-responding-to-the-world"))

items.append(build(
    20,
    "A colleague arrives late to a meeting and a teammate concludes that he is careless, ignoring "
    "the closed highway that delayed his commute. Which tendency does the teammate display?",
    "The fundamental attribution error",
    [("The self-serving bias", "Self-serving bias protects one's own self-image, not judgments "
                               "about other people."),
     ("The false consensus effect", "False consensus is overestimating how many others share one's "
                                    "views."),
     ("Cognitive dissonance", "Dissonance is discomfort from inconsistent attitudes and behavior, "
                              "not a judgment error about others.")],
    KEYS[19],
    "Overweighting disposition (carelessness) and underweighting the situation (a closed highway) "
    "when explaining someone else's behavior is the fundamental attribution error.",
    "7a-individual-influences-on-behavior"))

items.append(build(
    21,
    "In a line-judgment study, a participant gives an obviously wrong answer that matches the "
    "unanimous confederates and later says he did not want to look foolish. Which influence "
    "explains the response?",
    "Normative social influence",
    [("Informational social influence", "Informational influence operates when the group seems to "
                                        "know something the participant does not."),
     ("Obedience to authority", "No authority figure issued an order in this setting."),
     ("Groupthink", "Groupthink is a decision-making failure in cohesive groups, not line-judgment "
                    "conformity.")],
    KEYS[20],
    "Conforming to avoid social rejection or ridicule is normative influence; the participant "
    "changed behavior without believing the group was right.",
    "7b-social-processes-that-influence-behavior"))

items.append(build(
    22,
    "A charity asks householders to sign a petition, and a week later asks the same householders to "
    "put a large sign on their lawn; many more agree than in a group asked only for the sign. Which "
    "technique is illustrated?",
    "Foot-in-the-door",
    [("Door-in-the-face", "Door-in-the-face opens with a large request that is then withdrawn in "
                          "favor of a smaller one."),
     ("Low-balling", "Low-balling secures agreement, then changes the terms after commitment."),
     ("Norm of reciprocity", "Reciprocity depends on first giving something to the target, which "
                             "a petition signature does not.")],
    KEYS[21],
    "Securing compliance with a small initial request and following it with a larger one is the "
    "foot-in-the-door technique; commitment and self-perception carry the effect.",
    "7c-attitude-and-behavior-change"))

items.append(build(
    23,
    "After winning a match, a player credits her training; after losing, she blames the officiating. "
    "Which pattern is this?",
    "Self-serving bias",
    [("The fundamental attribution error", "That error concerns judging other people, not one's own "
                                           "outcomes."),
     ("The looking-glass self", "The looking-glass self describes a self-image built from others' "
                                "reactions, not outcome attributions."),
     ("Social loafing", "Social loafing is reduced individual effort in a group task.")],
    KEYS[22],
    "Taking credit for success while externalizing failure protects self-esteem and is the "
    "self-serving bias.",
    "8a-self-identity"))

items.append(build(
  24,
  "Participants are divided into two groups using a trivial coin toss and immediately rate their "
  "own group's painting as better. What does this minimal group paradigm demonstrate?",
    "Mere categorization into an in-group and an out-group is enough to produce favoritism",
    [("Discrimination requires a history of real conflict between the groups",
      "The finding is precisely that no real conflict or interest is needed."),
     ("Favoritism appears only when rewards are tangible",
      "Even with no material stake, in-group favoritism emerges."),
     ("Conformity pressure from other members drives the ratings",
      "The groups are alone in a room with no member pressure; categorization alone suffices.")],
    KEYS[23],
    "Tajfel's minimal group studies show that an arbitrary category label alone produces in-group "
    "favoritism, which is the social-identity account of prejudice.",
    "8b-social-thinking"))

items.append(build(
    25,
    "Told by an experimenter in a lab coat to continue, most participants in a famous study "
    "increased what they believed were painful shocks to a struggling learner. Which variable most "
    "strongly raised compliance?",
    "Proximity to and perceived legitimacy of the authority giving the order",
    [("The participants' underlying aggression toward strangers",
      "Baseline aggression does not explain the sharp variation across the study's conditions."),
     ("Group unanimity of the peers",
      "Peer unanimity drives conformity in Asch's design, not obedience in this one."),
     ("The attractiveness of the learning task",
      "Task appeal was held constant and is not the mechanism of obedience.")],
    KEYS[24],
    "Milgram's obedience studies varied the authority's presence and legitimacy; compliance rose "
    "when the authority was close and credible, and fell when orders came remotely or from a peer.",
    "8c-social-interactions"))

# --------------------------------------------------------- 26-30 social structure
items.append(build(
    26,
    "A nurse who is also a single parent finds that an evening shift and her child's school concert "
    "are scheduled at the same time. Which concept applies?",
    "Role conflict between two different statuses",
    [("Role strain within a single role", "Role strain is tension inside one role, such as two "
                                          "conflicting demands of the nursing job alone."),
     ("Role exit", "Role exit means leaving a role behind altogether, which she has not done."),
     ("Ascribed status", "Both employee and parent are achieved statuses, and the question is about "
                         "competing demands.")],
    KEYS[25],
    "Tension between the expectations of two different statuses held by one person is role "
    "conflict; strain inside one role would be role strain.",
    "9a-understanding-social-structure"))

# 27 crude birth rate
cbr27 = calc(27, 500.0 / 20000.0 * 1000.0, 25.0)
items.append(build(
    27,
    "A country recorded 500,000 live births in a year in a population of 20 million. What is its "
    "crude birth rate?",
    "%.0f per 1,000 population per year" % cbr27,
    [("25 per 100 population per year", "Used the wrong denominator base; rates are conventionally "
                                        "per 1,000."),
     ("0.025 per 1,000 population per year", "Divided the births by the population but never "
                                             "multiplied by 1,000."),
     ("40 per 1,000 population per year", "Inverted the ratio and divided population by births.")],
    KEYS[26],
    "Crude birth rate = (births / total population) x 1,000 = (500,000/20,000,000) x 1,000 = "
    "%.0f per 1,000 per year." % cbr27,
    "9b-demographic-characteristics-and-processes"))

items.append(build(
    28,
    "A job applicant from a working-class neighborhood is hired largely because a neighbor who "
    "already works at the firm vouched for her. Which concept best captures the resource she used?",
    "Social capital",
    [("Human capital", "Human capital is her own schooling and skills, not her network."),
     ("Cultural capital", "Cultural capital is familiarity with elite tastes and credentials, "
                          "which is not what secured the referral."),
     ("Merited achievement", "The hire turned on a connection rather than on measured performance.")],
    KEYS[27],
    "Benefits that flow from network ties and relationships are social capital; the neighbor's "
    "endorsement, not her individual credentials, did the work here.",
    "10a-social-inequality"))

items.append(build(
    29,
    "A gambler keeps feeding coins into a machine that pays out after an unpredictable number of "
    "plays, and the behavior is very hard to extinguish. Which schedule is in force?",
    "Variable-ratio reinforcement",
    [("Fixed-ratio reinforcement", "A fixed ratio pays after a set number of responses, which makes "
                                   "extinction easier to detect."),
     ("Variable-interval reinforcement", "Variable intervals reinforce the first response after "
                                         "varying times, as in checking for mail."),
     ("Fixed-interval reinforcement", "Fixed intervals produce a scalloped pattern, like studying "
                                      "harder just before a scheduled exam.")],
    KEYS[28],
    "Reinforcing after an unpredictable number of responses is the variable-ratio schedule, which "
    "produces high, steady responding and the greatest resistance to extinction.",
    "fc7-behavior-and-behavior-change"))

items.append(build(
    30,
    "Immigrant parents encourage their children to speak the language of their new country at home "
    "and to set aside the family's own language in order to be seen as fully belonging. Which "
    "process is illustrated?",
    "Assimilation",
    [("Cultural relativism", "Cultural relativism is a stance for judging practices within their own "
                             "context, not a process of adopting a host culture."),
     ("Multiculturalism", "Multiculturalism preserves distinct cultural practices alongside the "
                          "host society's."),
     ("Xenophobia", "Xenophobia is hostility toward outsiders; the pressure here comes from within "
                    "the family's own strategy for belonging.")],
    KEYS[29],
    "Shedding a home-culture marker in order to blend into the dominant society is assimilation; "
    "the family is trading language maintenance for perceived belonging.",
    "fc9-cultural-and-social-differences"))

# --------------------------------------------------------------------- assemble
doc = {
    "exam": "mcat",
    "section": "drill-psych-soc",
    "label": "Psych/Soc drill",
    "subject": "psych-soc",
    "block": "psych-soc",
    "_drill": True,
    "items_expected": len(items),
    "items": items,
    "passages": [],
}
assert len(items) == 30 == doc["items_expected"], len(items)
assert len({i["id"] for i in items}) == 30
allowed = {"psychology", SOC, "fc6-perceive-think-react", "fc7-behavior-and-behavior-change",
           "fc8-self-others-interactions", "fc9-cultural-and-social-differences",
           "fc10-stratification-and-resources", "6a-sensing-the-environment",
           "6b-making-sense-of-the-environment", "6c-responding-to-the-world",
           "7a-individual-influences-on-behavior", "7b-social-processes-that-influence-behavior",
           "7c-attitude-and-behavior-change", "8a-self-identity", "8b-social-thinking",
           "8c-social-interactions", "9a-understanding-social-structure",
           "9b-demographic-characteristics-and-processes", "10a-social-inequality"}
assert {i["chapter"] for i in items} <= allowed
letters = Counter(i["answer"] for i in items)
assert max(letters.values()) <= 8, letters
assert len({i["q"] for i in items}) == 30

with open(OUT, "w") as fh:
    yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True, width=100)

print("wrote", OUT)
print("answers:", dict(sorted(letters.items())))
print("chapters:", dict(Counter(i["chapter"] for i in items)))
