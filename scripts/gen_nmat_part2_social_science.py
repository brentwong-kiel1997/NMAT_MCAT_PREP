#!/usr/bin/env python3
"""Generate NMAT Part 2 · Social Science item bank (30 items).

Structural guarantee for the distractor rule: each item is authored as
(correct text + three wrong texts, each with its own note).  The builder
places the correct text at the item's answer letter and the three wrong
texts at the remaining letters, so `distractors` keys are always exactly
the three letters that are NOT the answer and each note addresses that
option's own text.
"""
import os
from collections import Counter

import yaml

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part2-social-science.yml"
LETTERS = ["A", "B", "C", "D"]

PSY = "psychology"
SOC = "sociology-and-anthropology"
FC6 = "fc6-perceive-think-react"
FC7 = "fc7-behavior-and-behavior-change"
FC8 = "fc8-self-others-interactions"
FC9 = "fc9-cultural-and-social-differences"
FC10 = "fc10-stratification-and-resources"

# (answer_letter, chapter, q, correct, [(wrong_text, note), x3])
ITEMS = [
    # ---------------------------------------------------------------- conditioning
    ("C", FC7,
     "A toddler who was never afraid of white rats begins to cry the moment one is shown, "
     "after a researcher repeatedly paired the rat with a frightening loud noise. The rat "
     "has become…",
     "a conditioned stimulus that elicits a learned fear response",
     [("an operant reinforcer that strengthened the fear by reward",
      "Nothing followed or rewarded the child's crying; the fear was elicited by a paired stimulus."),
      ("an unconditioned stimulus for fear",
      "The loud noise was the unconditioned stimulus; the rat only acquired that power through pairing."),
      ("a negative reinforcer removing an aversive state",
      "Negative reinforcement concerns removing something aversive after a behavior, not stimulus pairing.")]),

    ("A", FC7,
     "A car keeps beeping until the driver fastens his seat belt. He now buckles up "
     "immediately on every trip. The beep functions as…",
     "a negative reinforcer, because its removal increases the buckling behavior",
     [("a positive punisher, because it is an unpleasant stimulus",
       "Punishment weakens behavior; here buckling increased, and the beep ended rather than followed it."),
      ("a conditioned stimulus eliciting buckling automatically",
       "Buckling is emitted to escape the beep; it is an operant consequence, not a reflex."),
      ("a fixed-interval schedule maintaining the behavior",
       "Reinforcement depends on the response of buckling, not on the passage of a set time.")]),

    ("D", FC7,
     "A slot-machine player keeps pulling the lever because wins arrive unpredictably after "
     "varying numbers of pulls, and the behavior survives long stretches without a win. "
     "This is which reinforcement schedule?",
     "Variable ratio",
     [("Fixed ratio",
       "A fixed ratio delivers reinforcement after a set number of responses, not a varying one."),
      ("Fixed interval",
       "A fixed interval reinforces the first response after a set time, producing a scalloped pause pattern."),
      ("Variable interval",
       "A variable interval is based on varying amounts of time, not on varying numbers of responses.")]),

    ("B", FC7,
     "Rina, a longtime smoker who knows smoking causes cancer, starts telling friends that "
     "the health warnings are exaggerated. Her new belief most directly reduces…",
     "cognitive dissonance between her behavior and her attitude",
     [("normative social influence from her peer group",
       "No group pressure is described; the discomfort arises from her own inconsistent beliefs and actions."),
      ("a self-serving attribution about her own risk taking",
       "She is not explaining a success or failure; she is easing inconsistency between attitude and behavior."),
      ("reactance against health authorities",
       "Reactance is resistance to a perceived threat to one's freedom, not tension between one's own beliefs and acts.")]),

    # ------------------------------------------------------- emotion and motivation
    ("C", PSY,
     "After a near collision, Paolo's heart pounds. At first he feels only arousal; once he "
     "recognizes that the other car swerved into his lane, the arousal becomes fear. This "
     "sequence best illustrates…",
     "the Schachter-Singer two-factor theory: physiological arousal plus a cognitive label",
     [("the James-Lange theory, in which emotion is the perception of bodily change",
       "James-Lange stops at perceiving the body's response and requires no separate labeling of the situation."),
      ("the Cannon-Bard theory, in which arousal and emotion occur independently",
       "Cannon-Bard treats arousal and felt emotion as simultaneous and independent, not as arousal that is then labeled."),
      ("the Yerkes-Dodson law of optimal arousal for performance",
       "That law links arousal level to task performance, not to how an emotion gets identified.")]),

    # ---------------------------------------------------------------- memory systems
    ("A", PSY,
     "A patient with hippocampal damage cannot form new conscious memories of facts and "
     "events, yet steadily improves at a mirror-tracing task across sessions. This "
     "dissociation shows that…",
     "declarative memory and procedural memory depend on different brain systems",
     [("procedural skills are stored together with facts in the hippocampus",
       "His continued skill learning shows procedural memory survives hippocampal damage."),
      ("all memory consolidation takes place in the amygdala",
       "The amygdala is central to emotional memory, not to general consolidation of facts and events."),
      ("working memory has a very large storage capacity",
       "Nothing here concerns capacity; working memory is famously limited to a few items.")]),

    # ------------------------------------------------------------------ Piaget
    ("B", PSY,
     "A child agrees that two identical glasses hold the same amount of water, but says the "
     "taller, narrower glass has 'more' once the water is poured into it. In Piaget's terms "
     "the child lacks…",
     "conservation of quantity",
     [("object permanence",
       "Object permanence is knowing an object still exists when out of sight, mastered in the sensorimotor stage."),
      ("abstract and hypothetical reasoning",
       "Formal operational reasoning appears in early adolescence, far beyond this liquid task."),
      ("egocentrism",
       "Egocentrism is difficulty taking another's viewpoint; the child here is comparing amounts, not perspectives.")]),

    # ---------------------------------------------------------------- attachment
    ("D", PSY,
     "In Ainsworth's Strange Situation, a toddler plays with the toys while his mother is "
     "present, cries when she leaves, greets her warmly when she returns, and is easily "
     "comforted. This pattern is classified as…",
     "secure attachment",
     [("insecure-avoidant attachment",
       "Avoidant infants show little distress at separation and ignore or avoid the caregiver at reunion."),
      ("insecure-resistant (ambivalent) attachment",
       "Resistant infants cling before separation and remain hard to soothe after reunion, often showing anger."),
      ("disorganized attachment",
       "Disorganized attachment shows contradictory, frozen, or fearful behavior toward the caregiver.")]),

    # ------------------------------------------------------------- neurotransmitters
    ("C", PSY,
     "Which neurotransmitter is most closely tied to the brain's reward pathways, and is "
     "implicated both in Parkinson's disease when depleted and in schizophrenia when "
     "excessive?",
     "Dopamine",
     [("Acetylcholine",
       "Acetylcholine drives muscle activation and memory; it is depleted early in Alzheimer's disease."),
      ("GABA",
       "GABA is the nervous system's principal inhibitory neurotransmitter."),
      ("Serotonin",
       "Serotonin regulates mood, sleep, and appetite; it is not the reward-pathway transmitter.")]),

    # ------------------------------------------------------------------- sleep / REM
    ("A", PSY,
     "After three nights of badly shortened sleep, a student spends an unusually large share "
     "of the next night in rapid-eye-movement sleep. This compensation is called…",
     "REM rebound",
     [("sleep apnea",
       "Sleep apnea is repeated interruption of breathing during sleep, a disorder rather than a recovery effect."),
      ("sleep spindling",
       "Sleep spindles are brief bursts of activity in stage 2 NREM sleep, not a rise in REM."),
      ("narcolepsy",
       "Narcolepsy is a disorder of uncontrollable sleep attacks during the day.")]),

    # ----------------------------------------------------------- sensation/perception
    ("B", FC6,
     "Ana can tell that a 100-gram weight is heavier than a 105-gram weight, but she cannot "
     "distinguish 1,000 grams from 1,005 grams. Weber's law explains this because the "
     "difference threshold…",
     "is a constant proportion of the original stimulus intensity",
     [("is a fixed number of grams regardless of the starting weight",
       "A constant absolute difference is exactly what Weber's law rules out; larger standards need larger differences."),
      ("depends on how long the weights are held",
       "Duration may affect performance, but Weber's law relates the threshold to stimulus intensity."),
      ("is the smallest stimulus intensity that can be detected at all",
       "That defines the absolute threshold, a different concept from the just-noticeable difference.")]),

    # ------------------------------------------------------------------ social psych
    ("D", FC8,
     "In Milgram's studies, most participants delivered the highest shock level to a "
     "protesting learner because an experimenter in a lab coat told them to continue. The "
     "central finding was that…",
     "ordinary people will follow a legitimate authority into harmful actions",
     [("only people with hostile personalities obey destructive orders",
       "The participants were ordinary adults; obedience did not require an aggressive character."),
      ("groups rarely change the judgment of a lone individual",
       "That is the conformity question studied by Asch, not Milgram's authority paradigm."),
      ("people obey only when the victim cannot be seen",
       "Obedience stayed high even when the learner was visible and in the same room.")]),

    ("C", FC8,
     "Asked to say publicly which of three lines matches a standard line, a participant "
     "chooses one he can plainly see is wrong because everyone before him chose it. This "
     "illustrates…",
     "normative conformity to a unanimous majority",
     [("obedience to a legitimate authority",
       "No authority gives an order here; the pressure comes from peers who are not in charge."),
      ("the fundamental attribution error",
       "That error concerns how we explain other people's behavior, not yielding to a group's judgment."),
      ("deindividuation in a large crowd",
       "Deindividuation is a loss of self-awareness in a group; this participant is singled out and answerable.")]),

    ("B", FC8,
     "A man collapses on a busy sidewalk. Dozens of people slow down and glance, but no one "
     "stops to help. The best explanation is…",
     "diffusion of responsibility when many witnesses are present",
     [("social loafing on a shared group task",
       "Social loafing is reduced individual effort on a cooperative task, not failure to help in an emergency."),
      ("groupthink driven by the desire for consensus",
       "Groupthink is a decision-making flaw in cohesive groups that suppresses dissent."),
      ("the mere-exposure effect",
       "Mere exposure is a growing preference for familiar stimuli, unrelated to helping.")]),

    ("A", FC8,
     "Kara watches a stranger trip on a raised curb and concludes, 'He's clumsy.' A minute "
     "later she trips on the same curb and says, 'That curb is broken.' Her first judgment "
     "illustrates…",
     "the fundamental attribution error",
     [("the self-serving bias",
       "The self-serving bias is about our own outcomes — it is her second, situational judgment about herself."),
      ("the false-consensus effect",
       "False consensus is overestimating how many others share one's own attitudes or behavior."),
      ("cognitive dissonance",
       "Dissonance is tension from inconsistent attitudes and behavior, not an explanation of someone's fall.")]),

    # -------------------------------------------------------------- research methods
    ("D", PSY,
     "A researcher randomly assigns one class to study with flashcards and another to reread "
     "their notes, then compares scores on the same exam. The dependent variable is…",
     "the exam score",
     [("the study method",
       "The study method is what the researcher manipulates — the independent variable."),
      ("the class section",
       "Class section belongs to the assignment procedure used to control confounds."),
      ("random assignment",
       "Random assignment is a design procedure, not an outcome that is measured.")]),

    ("C", PSY,
     "A study finds that neighborhoods with more ice cream shops also have higher drowning "
     "rates. The soundest conclusion is that…",
     "the two variables covary, most plausibly through a third factor such as hot weather",
     [("ice cream shops cause swimming, which causes drowning",
       "A correlation alone cannot establish causal direction or exclude a confounding variable."),
      ("drownings attract ice cream shops to an area",
       "The reverse causal direction is equally unsupported by an observed association."),
      ("the correlation establishes a causal link in one direction or the other",
       "Covariation is necessary but not sufficient for causation; a confound can produce the whole pattern.")]),

    # ---------------------------------------------------------------------- culture
    ("B", FC9,
     "Visiting a community that eats with its hands, an engineer calls the practice "
     "'uncivilized' and insists that his own utensils are the proper way to eat. His "
     "reaction illustrates…",
     "ethnocentrism",
     [("cultural relativism",
       "Relativism suspends judgment and asks what the practice means within its own cultural context."),
      ("cultural diffusion",
       "Diffusion is the spread of cultural traits from one society to another, not a judgment about them."),
      ("cultural assimilation",
       "Assimilation is adopting another group's culture, not rating other people's ways as inferior.")]),

    ("A", FC9,
     "In a farming community, eating with one's mouth open brings mild amusement, while "
     "stealing a neighbor's harvest brings lasting disgrace and shunning by the community. "
     "The two behaviors differ in that…",
     "the first violates a folkway, the second a more",
     [("the first violates a more, the second a folkway",
       "The labels are reversed: moral outrage and serious sanction mark mores, not everyday etiquette."),
      ("both are taboos enforced by law",
       "Taboos evoke deep revulsion and are often forbidden outright; neither act described reaches that level."),
      ("both are laws because both carry sanctions",
       "Laws are norms formally enacted and enforced by the state; only the second act approaches that.")]),

    ("D", FC9,
     "A country's courts still apply libel statutes written for print newspapers, and judges "
     "struggle to decide cases about viral social-media posts. Ogburn would call this gap "
     "between technology and the norms governing it…",
     "culture lag",
     [("cultural diffusion",
       "Diffusion is the spread of traits across societies, not a delay in adjusting norms."),
      ("cultural relativism",
       "Relativism is an evaluative stance toward practices, not a mismatch between technology and rules."),
      ("cultural integration",
       "Integration describes how well parts of a culture fit together; the case is a failure to keep pace.")]),

    ("C", FC9,
     "A mother must attend a work meeting at the same hour as her daughter's school recital, "
     "so the demands of being an employee clash with those of being a parent. At work she "
     "also feels torn within her one role as supervisor, wanting to stay an approachable "
     "mentor to her staff while still enforcing hard deadlines. The first situation is role "
     "conflict; the second is…",
     "role strain",
     [("role exit",
       "Role exit is leaving a status altogether, as in retiring or divorcing."),
      ("role engulfment",
       "That term does not name tension among the expectations attached to one status."),
      ("role modeling",
       "Role modeling is imitating another person's behavior, not tension within a role.")]),

    # --------------------------------------------------------------- stratification
    ("B", FC10,
     "Weber analyzed standing in terms of three distinct dimensions. A respected traditional "
     "healer who owns little property but is widely honored in her community illustrates…",
     "status, or social honor and prestige",
     [("class, or economic position in the market",
       "Class is defined by wealth and market position, which the healer lacks."),
      ("party, or organized power in groups",
       "Party refers to organized capacity to influence collective decisions, not general esteem."),
      ("caste, a ritually fixed rank",
       "Caste is a closed birth-ascribed system, not one of Weber's dimensions of standing.")]),

    ("D", FC10,
     "For Marx, the fundamental division of capitalist society separates those who own the "
     "means of production from those who…",
     "must sell their labor for wages",
     [("hold the most honored status positions",
       "Status prestige is Weber's dimension; Marx's divide runs along ownership of capital."),
      ("control the means of coercion",
       "Control of coercion belongs to the state and figures in Weber's analysis, not Marx's class criterion."),
      ("organize the most effective political party",
       "Party is Weber's third dimension, not the boundary of Marx's two classes.")]),

    ("A", FC10,
     "In a society where a person's occupation, marriage partner, and rank are fixed at birth "
     "and cannot be changed, the stratification system is best described as…",
     "a caste system, because status is ascribed and the boundaries are closed",
     [("a class system, because placement rests on achievement",
       "Class systems are open to mobility; the system described forbids it."),
      ("a meritocracy, because ability determines placement",
       "Meritocracy ranks people by talent and effort — the opposite of birth-fixed placement."),
      ("an estate system, because landholding defines the strata",
       "Estate systems, as in feudal Europe, rest on legally defined landholding, not ritual birth rank.")]),

    ("C", FC10,
     "A farmer's daughter qualifies as a physician and earns far more than her parents ever "
     "did. This is an example of…",
     "upward intergenerational mobility",
     [("horizontal mobility",
       "Horizontal mobility is a move within the same rank, not to a higher one."),
      ("structural mobility",
       "Structural mobility comes from change in the economy as a whole, not from an individual trajectory."),
      ("downward intragenerational mobility",
       "Her rank rose rather than fell, and the comparison spans generations, not one career.")]),

    ("B", FC10,
     "In Merton's strain theory, a poor student who accepts the cultural goal of wealth but "
     "reaches it by selling counterfeit documents is using which adaptation?",
     "Innovation",
     [("Conformity",
       "Conformity accepts both the cultural goals and the institutionalized means of reaching them."),
      ("Ritualism",
       "Ritualism abandons the goals but clings rigidly to the rules, like the clerk with no ambition."),
      ("Retreatism",
       "Retreatism rejects both the goals and the means, withdrawing from the race altogether.")]),

    ("D", FC10,
     "A boy caught shoplifting is called a 'delinquent' by his teachers and neighbors; he then "
     "drifts into the company of other labeled youths and offends more often. This sequence is "
     "best explained by…",
     "labeling theory",
     [("Merton's strain theory",
       "Strain explains deviance as the gap between goals and legitimate means, not as a reaction to a public label."),
      ("differential association theory",
       "Differential association explains deviance as learned in intimate groups, without the pivotal public label."),
      ("rational choice theory",
       "Rational choice weighs the costs and benefits of an act and does not center on society's reaction.")]),

    # -------------------------------------------------------------------- demography
    ("A", FC10,
     "A country's death rate has stayed low for a generation while its birth rate has fallen "
     "sharply; the population still grows, but more slowly than before. Which stage of "
     "demographic transition is this?",
     "Stage 3: birth rate falling while the death rate remains low",
     [("Stage 1: high birth rate and high death rate",
       "Stage 1 has both rates high and produces little or no growth."),
      ("Stage 2: death rate falling while the birth rate stays high",
       "Stage 2 is where the death rate drops first, producing very rapid growth."),
      ("Stage 4: both rates low and the population roughly stable",
       "Stage 4 has a low birth rate too, so growth levels off rather than continuing.")]),

    ("C", FC10,
     "A population pyramid shows a very wide base for ages 0-4, with each older band "
     "noticeably narrower. What does this shape indicate?",
     "High birth rate and high potential for future population growth",
     [("Low birth rate and slow population growth",
       "A low-fertility population shows a narrow base, not a broad one."),
      ("An aging population with a shrinking younger cohort",
       "An aging population is top-heavy, with a constricted base and wide older bands."),
      ("Near-zero growth with similar numbers at every age",
       "Zero growth yields a straight-sided or barrel-shaped pyramid.")]),

    # ------------------------------------------------------------- anthropology methods
    ("B", SOC,
     "An anthropologist lives in a barangay for two years, joins the rice-planting rituals, "
     "and records what the harvest means to villagers in their own terms. She later compares "
     "those meanings with harvest rites elsewhere using outside analytical categories. The "
     "first approach is emic; the second is…",
     "etic",
     [("participant observation",
       "Participant observation is the fieldwork method of joining daily life, not the analytical contrast to emic."),
      ("ethnographic interviewing",
       "Interviewing is a data-collection technique, not the outsider's analytical standpoint."),
      ("cultural materialism",
       "Cultural materialism is a theoretical paradigm about explaining culture through material conditions.")]),
]


def build():
    items = []
    for n, (ans, chapter, q, correct, wrongs) in enumerate(ITEMS, start=1):
        assert len(wrongs) == 3, f"item {n} needs exactly 3 wrong options"
        others = [l for l in LETTERS if l != ans]
        choices = {ans: correct}
        distractors = {}
        for letter, (text, note) in zip(others, wrongs):
            choices[letter] = text
            distractors[letter] = note
        choices = {l: choices[l] for l in LETTERS}
        items.append({
            "id": f"nmat-p2s-{n:03d}",
            "q": q,
            "choices": choices,
            "answer": ans,
            "explain": None,  # filled in VERIFY pass below
            "distractors": distractors,
            "chapter": chapter,
        })
    return items


# Explanations keyed by item number.
EXPLAIN = {
    1: "Watson and Rayner's Little Albert design: a neutral stimulus repeatedly paired with an "
       "unconditioned stimulus acquires the power to elicit a conditioned response.",
    2: "Reinforcement is defined by its effect — it increases the behavior. Removing an aversive "
       "stimulus after a response is negative reinforcement; the 'negative' marks the removal.",
    3: "Reinforcement after an unpredictable number of responses is a variable-ratio schedule; it "
       "produces high, steady response rates and the greatest resistance to extinction.",
    4: "Festinger's cognitive dissonance theory: inconsistency between attitude and behavior creates "
       "tension, which people reduce by changing the attitude or adding justifying beliefs.",
    5: "Schachter's two-factor theory holds that experienced emotion equals physiological arousal plus "
       "a cognitive interpretation of the situation; the same arousal can become fear, anger, or joy.",
    6: "The hippocampus is essential for forming new declarative memories, whereas skill learning "
       "(procedural memory) relies on basal ganglia and cerebellar circuits.",
    7: "Conservation — knowing quantity is unchanged by a change in appearance — is the hallmark of "
       "moving from the preoperational to the concrete operational stage.",
    8: "Securely attached infants use the caregiver as a safe base, show distress on separation, and "
       "are readily soothed at reunion.",
    9: "Dopamine mediates reward in the mesolimbic pathway; loss of dopaminergic neurons in the "
       "substantia nigra causes Parkinsonian symptoms, and excess activity is linked to psychosis.",
    10: "Deprived of REM sleep, the brain increases the proportion and intensity of REM on recovery "
        "nights — the REM rebound effect.",
    11: "Weber's law: the just-noticeable difference is a constant fraction of the standard stimulus, "
        "so heavier weights require proportionally larger differences to be told apart.",
    12: "Milgram showed the power of legitimate authority: about two-thirds of ordinary adult "
        "participants went to the maximum shock level despite voicing discomfort.",
    13: "Asch's line studies demonstrated normative social influence — people conform to a unanimous "
        "majority to avoid rejection even against clear perceptual evidence.",
    14: "Darley and Latané's bystander effect: responsibility is divided among everyone present, so "
        "each individual feels less personally obliged to intervene.",
    15: "The fundamental attribution error is the tendency to overattribute others' behavior to their "
        "dispositions while underweighting situational causes.",
    16: "The dependent variable is the measured outcome presumed to depend on the manipulated "
        "independent variable — here, the study method.",
    17: "A correlation shows association only. A third variable — summer heat raises both ice-cream "
        "sales and swimming — can generate the whole relationship.",
    18: "Ethnocentrism judges another culture by the standards of one's own and treats one's own as "
        "superior; relativism evaluates practices inside their own cultural frame.",
    19: "Folkways are everyday etiquette norms backed by weak sanctions; mores carry moral weight and "
        "bring serious sanctions — here, disgrace and shunning.",
    20: "Ogburn's culture lag: material culture (technology) changes faster than the nonmaterial "
        "culture (laws, norms, beliefs) that has to regulate it.",
    21: "Role conflict pits the expectations of different statuses against each other; role strain is "
        "tension among the expectations attached to a single status.",
    22: "Weber separated class (wealth and market position), status (prestige or honor), and party "
        "(organized power). Honor without property is status standing alone.",
    23: "Marx's two-class model pits the bourgeoisie, who own capital, against the proletariat, whose "
        "only resource is labor power sold for wages.",
    24: "Castes are closed systems of birth-ascribed rank with strict endogamy and fixed occupation; "
        "classes are at least partly achieved and open to mobility.",
    25: "Intergenerational mobility compares a person's position with her parents'; movement to a "
        "higher rank is upward mobility.",
    26: "Innovation accepts society's goals while rejecting or lacking the legitimate means, turning "
        "to illegitimate routes to reach them.",
    27: "Labeling theory: the label applied by others can become a master status that channels the "
        "person into further, or secondary, deviance.",
    28: "In stage 3 fertility falls while mortality stays low, so the gap opened in stage 2 narrows "
        "and growth slows.",
    29: "A broad-based pyramid means many children relative to adults — high fertility and a cohort "
        "wave that will keep the population growing as it ages.",
    30: "Etic analysis applies the observer's external, comparative categories; emic description "
        "captures what the practice means to the members themselves.",
}


def main():
    items = build()
    for it in items:
        n = int(it["id"].split("-")[-1])
        it["explain"] = EXPLAIN[n]

    data = {
        "exam": "nmat",
        "section": "part2-social-science",
        "label": "Social Science",
        "subject": "behavioral-social",
        "block": "part2",
        "items_expected": len(items),
        "items": items,
        "passages": [],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        yaml.safe_dump(
            data, fh, sort_keys=False, allow_unicode=True, width=100, default_flow_style=False
        )

    counts = Counter(i["answer"] for i in items)
    print(f"wrote {OUT}")
    print(f"items: {len(items)}  answers: {dict(sorted(counts.items()))}")
    print("chapters:", dict(Counter(i['chapter'] for i in items)))


if __name__ == "__main__":
    main()
