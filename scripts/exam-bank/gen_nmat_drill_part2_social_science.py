#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/drill/part2-social-science.yml (25 drills).

Practice-only companion to part2-social-science.yml: standalone scenario MCQs,
no passages, no mock-blueprint role (drill/ files carry _drill). Drills the
angles the main bank skips: second-order conditioning schedules, memory
interference directions, heuristic versus bias discrimination, and the
group-process distinctions students most often blur.

Authoring form is (stem, correct_text, [(wrong_text, error_note) x 3], chapter).
A fixed balanced key pattern places the correct choice; the three wrong choices
fill the remaining letters in order, so an error note can never land on the
answer letter.
"""
import os
from collections import Counter

import yaml

OUT = ("/home/ubuntu/django-wsgi/content/exam-bank/"
       "nmat/drill/part2-social-science.yml")

# 25 slots -> A:6 B:7 C:6 D:6
KEYS = ["A", "B", "C", "D", "D", "A", "B", "C",
        "C", "D", "A", "A", "B", "C", "D", "D",
        "A", "B", "C", "D", "D", "A", "B", "C",
        "B"]

PSY = "psychology"
SocAnth = "sociology-and-anthropology"
FC6 = "fc6-perceive-think-react"
FC7 = "fc7-behavior-and-behavior-change"
FC8 = "fc8-self-others-interactions"
FC9 = "fc9-cultural-and-social-differences"
FC10 = "fc10-stratification-and-resources"

ITEMS = [
    ("A trainer wants a dog to roll over. She first rewards the dog merely for "
     "lying down, then only for rolling onto its side, and finally only for "
     "completing the roll. This procedure is",
     "shaping, reinforcing successive approximations toward the target behavior",
     [("classical conditioning, because the reward follows a signal",
       "no neutral stimulus is being paired with an unconditioned one; consequences, not signals, drive the change"),
      ("punishment, because the earlier responses are no longer rewarded",
       "withholding a reward is omission, not punishment; no aversive stimulus is ever presented"),
      ("negative reinforcement, because a signal stops once the dog complies",
       "nothing aversive is removed; the contingency adds a reward")],
     FC7),

    ("A dog's salivation to a bell was extinguished by repeated bell-without-food "
     "trials. A week later the bell alone again brings a small amount of "
     "salivation. This return is",
     "spontaneous recovery, showing that extinction suppressed rather than erased the association",
     [("acquisition, because the bell is gaining strength for the first time",
       "the association was already learned; this is a reappearance after a rest"),
      ("generalization, because a different tone was presented",
       "no new stimulus is involved; the original conditioned stimulus produced the response"),
      ("extinction, because the conditioned response had disappeared permanently",
       "the response came back, which is exactly what extinction alone does not predict")],
     PSY),

    ("A child who watched a model being praised for hitting an inflatable doll "
     "later hits it far more often than a child who saw the model scolded. The "
     "difference demonstrates",
     "vicarious reinforcement, learning the consequences of an act by watching them "
     "happen to someone else",
     [("classical conditioning, because the model's praise was paired with the doll",
       "the effect depends on observed consequences, not on stimulus pairing"),
      ("direct operant conditioning, since the child was reinforced for hitting",
       "the observer was never rewarded personally; the model's outcome did the work"),
      ("insight learning, a sudden restructuring of how the toy works",
       "nothing about the toy's workings was discovered; only its consequences changed")],
     PSY),

    ("Rats that wandered a maze for days with no food in the goal box ran it almost "
     "flawlessly as soon as food was finally placed there, matching rats rewarded "
     "all along. This shows",
     "latent learning, a cognitive map formed without reward and revealed only when "
     "a reward appears",
     [("shaping, because the delayed reward finally shaped the running response",
       "no successive approximations were reinforced during the unrewarded wandering"),
      ("spontaneous recovery of a previously extinguished response",
       "nothing had been extinguished; the response had never yet been displayed"),
      ("discrimination learning between rewarded and unrewarded arms of the maze",
       "the rats did not learn which arms paid off; they learned the maze's layout")],
     PSY),

    ("A student is quizzed every Friday and studies hardest on Thursday nights, "
     "slacking off just after each quiz. Which schedule of reinforcement is at "
     "work?",
     "fixed interval, which produces a post-reinforcement pause and a burst as the "
     "deadline nears",
     [("fixed ratio, because the quiz rewards a set number of study responses",
       "the contingency is on time since the last quiz, not on a count of responses"),
      ("variable ratio, because the exact study time needed is unpredictable",
       "the interval is perfectly predictable at seven days"),
      ("continuous reinforcement, because every study session earns a quiz",
       "most study sessions earn nothing; reward comes only at the interval's end")],
     FC7),

    ("A child who loved drawing produces far fewer pictures after her preschool "
     "begins giving prizes for each one. The best explanation is",
     "the overjustification effect, an external reward undermines intrinsic interest",
     [("positive reinforcement, which by definition strengthens the rewarded behavior",
       "the behavior fell rather than rose, so reinforcement cannot be the explanation"),
      ("extinction, because her drawings were no longer being noticed",
       "the drawings drew more attention than ever; they were paid for"),
      ("classical conditioning that paired the prize with the crayons",
       "no conditioned emotional response to the crayons is at issue")],
     FC7),

    ("After memorizing her new mobile number, Ana finds she can no longer recall "
     "her old one. This failure is",
     "retroactive interference, in which new learning disrupts recall of older material",
     [("proactive interference, because the old number blocks the new one",
       "that reverses the direction; here the newer item is the one doing the disrupting"),
      ("encoding failure, because the old number was never stored",
       "the old number was stored and used for years; the failure is at retrieval"),
      ("decay, because the memory simply faded with the passage of time",
       "time alone is not the culprit; the interfering new learning is")],
     FC6),

    ("Scuba divers who memorized a word list underwater recall it far better when "
     "tested underwater than on land. This illustrates",
     "context-dependent memory, because the physical setting supplies the retrieval "
     "cues present at encoding",
     [("the testing effect, because retrieval practice strengthened the memory",
       "no repeated retrieval is involved; only the setting of the single test changed"),
      ("mood-congruent memory, because the environment matched the divers' mood",
       "the match is to the external setting, not to an internal emotional state"),
      ("anterograde amnesia for the list learned on land",
       "no memory disorder is involved; both groups encoded normally")],
     FC6),

    ("A manager who is convinced night-shift workers are lazy reads only the "
     "late-clock-in records and never looks at the early ones. This is",
     "confirmation bias, seeking out and weighting evidence that supports an existing belief",
     [("the availability heuristic, because late arrivals spring to mind easily",
       "the issue is selective evidence-gathering, not ease of recall"),
      ("hindsight bias, because the outcome now seems predictable in advance",
       "nothing has happened yet to be judged 'predictable'; the search itself is biased"),
      ("in-group favoritism, since he protects members of his own shift",
       "no group membership or resource allocation is at stake")],
     FC6),

    ("After saturation news coverage of one plane crash, travellers judge flying "
     "far more dangerous than driving. This judgment illustrates",
     "the availability heuristic, estimating frequency by how easily examples come "
     "to mind",
     [("the representativeness heuristic, matching flying to a prototype of disaster",
       "no similarity-to-a-prototype judgment is being made; it is ease of retrieval"),
      ("anchoring, adjusting insufficiently from a first number they were given",
       "no starting figure was offered for adjustment"),
      ("the fundamental attribution error, blaming the pilots' character",
       "the judgment concerns event frequency, not a person's disposition")],
     FC6),

    ("Linda is 31, outspoken, and studied philosophy. Asked whether she is more "
     "likely to be a bank teller or a bank teller active in feminist causes, most "
     "people pick the second. The error is",
     "representativeness with base-rate neglect, since the conjunction of two "
     "categories can never be more probable than one of them alone",
     [("the availability heuristic, because feminist bank tellers are more vivid",
       "the draw is the match between description and category, not vividness in memory"),
      ("anchoring, because her age of 31 anchors the estimate",
       "no numerical anchor drives this judgment"),
      ("functional fixedness, an inability to think of Linda in a new role",
       "that is a problem-solving rigidity, not a probability error")],
     FC6),

    ("A committee that already leans toward a plan spends two hours discussing it, "
     "and members leave more decided and more extreme than when they arrived. This "
     "is",
     "group polarization, in which deliberation among the like-minded intensifies "
     "the prevailing tendency",
     [("groupthink, because dissenting members kept silent to preserve harmony",
       "silence for harmony is groupthink's signature, not the shift toward a stronger view"),
      ("deindividuation, because members lost self-awareness in the crowd",
       "no anonymity or loss of self-awareness is described"),
      ("conformity to a unanimous majority on an obvious judgment",
       "the judgment is not obvious, and the group was unanimous from the start")],
     FC8),

    ("A tightly knit executive team approves a doomed project because nobody wants "
     "to sour the friendly consensus and the chair has signalled his preference "
     "early. This is",
     "groupthink, in which the drive for consensus overrides realistic appraisal of "
     "alternatives",
     [("group polarization, because the team's position became more extreme",
       "extremity is not the problem; the failure to test the decision is"),
      ("social loafing, because individual members let the others do the work",
       "no diffusion of effort is described; effort went into preserving agreement"),
      ("obedience to authority, because members were ordered to approve it",
       "no order was given; the pressure came from the group's own cohesion")],
     FC8),

    ("A homeowner who agreed to put a tiny sticker in her window is later far more "
     "likely to accept a large lawn sign for the same cause. This is",
     "the foot-in-the-door technique, in which a small commitment paves the way to "
     "a larger one",
     [("the door-in-the-face technique, which opens with an unreasonably large request",
       "the sequence is reversed; the first request here was trivially small"),
      ("low-balling, because the terms were changed after she agreed",
       "nothing was withdrawn or made costlier after her agreement"),
      ("the that's-not-all technique, because an extra benefit was added before she replied",
       "no sweetener was offered; only the size of the request changed")],
     FC8),

    ("In a classic tug-of-war study, individuals pull less hard as the group grows "
     "larger, though each believes the others are trying. This is",
     "social loafing, reduced individual effort when one's contribution is pooled "
     "and unidentifiable",
     [("deindividuation, a loss of self-awareness that releases impulsive behavior",
       "the outcome is lowered effort, not disinhibited behavior"),
      ("the bystander effect, diffusion of responsibility during an emergency",
       "nothing here is an emergency requiring intervention"),
      ("groupthink, in which consensus is valued over accuracy",
       "the effect is on effort, not on the quality of a decision")],
     FC8),

    ("Teachers are told that certain pupils, picked at random, are about to bloom. "
     "Months later those pupils score higher, having been given more attention and "
     "clearer feedback. This is",
     "a self-fulfilling prophecy, in which an expectation changes the perceiver's "
     "behavior and so produces the expected outcome",
     [("the fundamental attribution error, explaining the scores by the pupils' character",
       "the gain came from changed treatment, not from a dispositional inference"),
      ("the halo effect, one favorable trait coloring all other judgments",
       "the halo effect is a rating bias and does not itself raise performance"),
      ("regression toward the mean across repeated testings",
       "the randomly chosen group moved up rather than reverting, and treatment differed")],
     FC8),

    ("Strangers are divided into two groups by a coin toss and immediately rate "
     "their own group's members as more likable and allocate them more of a "
     "budget. This shows",
     "in-group favoritism arising from mere categorization, the minimal group effect",
     [("realistic conflict theory, competition over scarce resources",
       "there was no pre-existing conflict or resource scarcity before the coin toss"),
      ("obedience to authority, because the experimenter instructed them to discriminate",
       "no instruction to discriminate was given; the bias appeared on its own"),
      ("the just-world hypothesis, the belief that people get what they deserve",
       "no judgment of deservingness drives the allocation")],
     FC8),

    ("An anthropologist interprets a community's funeral practices in terms of the "
     "meanings those practices carry for that community rather than by her own "
     "standards. Her stance is",
     "cultural relativism, judging a practice within its own cultural context",
     [("ethnocentrism, ranking the other culture against her own",
       "that is the opposite stance, using her own culture as the measuring stick"),
      ("cultural diffusion, the spread of practices from one society to another",
       "nothing is being transmitted between societies here"),
      ("xenocentrism, preferring other cultures' ways over one's own",
       "no preference for foreign ways is expressed")],
     SocAnth),

    ("A nurse who migrated a month ago feels persistently disoriented: the food, "
     "the queues, the jokes and the unspoken rules all feel wrong, and she doubts "
     "her own competence. She is experiencing",
     "culture shock, the disorientation that follows immersion in an unfamiliar culture",
     [("assimilation, because she is adopting the host culture's ways",
       "assimilation is the eventual adoption of the new ways, not the distress of first contact"),
      ("cultural lag, because material culture changed faster than nonmaterial culture",
       "cultural lag describes a society's slow adjustment, not an individual's dislocation"),
      ("resocialization into her new hospital's total institution",
       "no total institution or deliberate retraining is described")],
     FC9),

    ("A teenager who wears the wrong sneakers to school is mocked by classmates "
     "for a week. The mockery is",
     "an informal negative sanction, an unplanned social reaction to a violated norm",
     [("a formal negative sanction, because a written rule was applied by an authority",
       "no written rule, official or enforcement body, is involved"),
      ("a positive sanction, because it raises his standing in the group",
       "the reaction is disapproving and costs him standing"),
      ("an internalized value, because he now believes the sneakers matter",
       "an internalized value is a personal belief, not an external social reaction")],
     SocAnth),

    ("Besides teaching reading, public schools also occupy children through the "
     "workday, which employers and parents quietly depend on. In functionalist "
     "terms this second effect is",
     "a latent function, an unrecognized and unintended consequence of the institution",
     [("a manifest function, because it is deliberate and publicly acknowledged",
       "childcare is not the school's declared purpose, which is instruction"),
      ("a dysfunction, because it disrupts the working of the school system",
       "nothing here is harmful to the institution or society"),
      ("a conflict-theory outcome, because schools reproduce class advantage",
       "that is a different theoretical lens, and it points to inequality, not childcare")],
     SocAnth),

    ("A household's income cannot provide the minimum calories, shelter and "
     "clothing needed to stay alive and healthy. This is",
     "absolute poverty, a shortfall below a fixed subsistence threshold",
     [("relative poverty, because the income falls below half the national median",
       "relative poverty is defined by inequality against the society, not by survival needs"),
      ("subjective poverty, because the household feels poor next to its neighbors",
       "subjective poverty rests on self-assessment rather than a subsistence line"),
      ("the culture of poverty, a set of values transmitted across generations",
       "that refers to an alleged value system, not to a measure of resources")],
     FC10),

    ("Across many countries, life expectancy climbs step by step with income, "
     "education and job grade, even among people who are not poor. This pattern is",
     "the social gradient in health, where each step up the hierarchy buys better "
     "health",
     [("the epidemiological transition, as chronic disease replaces infectious disease",
       "that describes changing causes of death over time, not a status-related gradient"),
      ("the demographic transition, as birth and death rates fall together",
       "that describes population-level rate changes, not health by social position"),
      ("medicalization, the redefinition of social problems as illnesses",
       "no relabeling of problems as disease is involved")],
     FC10),

    ("In one firm, equally qualified women are concentrated in clerical roles and "
     "rarely reach management. The structural barrier at the top is called",
     "the glass ceiling, an invisible institutional barrier to advancing into top positions",
     [("the glass escalator, the fast track men ride in female-dominated occupations",
       "that term describes men's advancement in feminized fields, not women's blockage"),
      ("the second shift, the unpaid household labor done after a paid job",
       "that concerns the domestic division of labor, not workplace promotion"),
      ("tracking, the sorting of students into different school curricula",
       "tracking happens in education, not in an occupational hierarchy")],
     FC10),

    ("A census lumps together people of very different ancestries, rewords its "
     "categories every few decades, and yet people's self-reports stay remarkably "
     "stable. This shows that",
     "race is a social construction, a category made and redefined by society "
     "rather than a fixed biological fact",
     [("race is a straightforward genetic classification that the census measures",
       "the shifting categories and mixed ancestries contradict a pure genetic scheme"),
      ("ethnicity and race are identical, since both describe ancestry",
       "ethnicity centers on culture and identity, while race is imposed by appearance and history"),
      ("assimilation has erased all racial distinctions in the population",
       "the persistence of stable self-reports argues against such erasure")],
     FC9),
]

EXPLANATIONS = [
    "Reinforcing closer and closer approximations to the final act is shaping; the criterion is "
    "raised at each stage until only the complete roll is paid off.",
    "A response that returns after a rest following extinction is spontaneous recovery, evidence "
    "that the original learning was inhibited rather than wiped out.",
    "Bandura's finding: observing a model's consequences changes the observer's behavior, which is "
    "vicarious (or observational) learning rather than personal reinforcement.",
    "Tolman's latent learning: unrewarded exploration still builds a cognitive map, which stays "
    "hidden until a reward makes performance worthwhile.",
    "A fixed interval schedule rewards the first response after a set time, producing the scalloped "
    "pattern of a pause followed by accelerating effort.",
    "Lepper's overjustification effect: paying for an already enjoyed activity shifts the perceived "
    "reason for doing it from interest to reward, and interest falls when the reward stops.",
    "Newer learning interfering with older memories is retroactive interference; proactive "
    "interference would run the other way, old blocking new.",
    "Godden and Baddeley's divers showed context-dependent memory: retrieval is best when the "
    "external cues at recall match those at encoding.",
    "Searching only for evidence that supports a prior belief, and ignoring the rest, is "
    "confirmation bias.",
    "Judging an event's frequency by how easily instances are retrieved is the availability "
    "heuristic; vivid, heavily reported events are overestimated.",
    "The conjunction fallacy (representativeness plus base-rate neglect): adding 'active in "
    "feminist causes' makes the description fit better while making the category strictly smaller "
    "and so less likely.",
    "When a like-minded group deliberates, the group's initial leaning is amplified: group "
    "polarization.",
    "Janis's groupthink: cohesive groups that prize consensus and defer to a directive leader "
    "suppress dissent and skip realistic appraisal.",
    "Securing a small commitment first makes people more likely to comply with a larger later "
    "request: the foot-in-the-door technique.",
    "Ringelmann's social loafing: when individual output is pooled and unidentifiable, each person "
    "exerts less effort than when pulling alone.",
    "Rosenthal and Jacobson's expectancy effect: the teachers' altered treatment, driven by a false "
    "belief, actually produced the predicted gains.",
    "Tajfel's minimal group experiments: merely sorting people into arbitrary categories is enough "
    "to produce in-group favoritism.",
    "Cultural relativism requires reading a practice in the terms of the culture that holds it, "
    "which is the opposite of judging it by one's own standards.",
    "Culture shock is the acute disorientation, self-doubt and stress of early immersion in an "
    "unfamiliar cultural environment.",
    "Spontaneous, socially enforced disapproval of a norm violation is an informal negative "
    "sanction; formal sanctions come from official bodies applying written rules.",
    "Merton distinguishes manifest (intended, recognized) from latent (unintended, often "
    "unrecognized) functions; supervised childcare is the classic latent function of schooling.",
    "Poverty below a fixed subsistence line, regardless of where others sit, is absolute poverty.",
    "The health gradient persists at every income level, showing that relative social standing, not "
    "only deprivation, shapes health outcomes.",
    "The glass ceiling is an invisible but real barrier that keeps women out of the top tiers of an "
    "occupational hierarchy.",
    "Categories that shift with legislation and politics while ancestries do not show that race is "
    "socially constructed rather than biologically fixed.",
]


def main() -> None:
    assert len(ITEMS) == 25 and len(KEYS) == 25 and len(EXPLANATIONS) == 25
    items = []
    for n, ((q, correct, wrongs, chapter), key, explain) in enumerate(
            zip(ITEMS, KEYS, EXPLANATIONS), 1):
        assert len(wrongs) == 3 and all(len(w) == 2 for w in wrongs)
        others = [letter for letter in "ABCD" if letter != key]
        choices = {key: correct}
        distractors = {}
        for letter, (text, note) in zip(others, wrongs):
            choices[letter] = text
            distractors[letter] = note
        assert set(choices) == {"A", "B", "C", "D"}
        assert key not in distractors
        items.append({
            "id": f"nmat-d-p2s-{n:03d}",
            "q": " ".join(q.split()),
            "choices": choices,
            "answer": key,
            "explain": " ".join(explain.split()),
            "distractors": distractors,
            "chapter": chapter,
        })

    doc = {
        "exam": "nmat",
        "section": "drill-part2-social-science",
        "label": "Social Science drill",
        "subject": "behavioral-social",
        "block": "part2",
        "_drill": True,
        "items_expected": 25,
        "passages": [],
        "items": items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=False,
                       default_flow_style=False, width=95)
    print(OUT)
    print(Counter(i["answer"] for i in items))
    print(Counter(i["chapter"] for i in items))


if __name__ == "__main__":
    main()
