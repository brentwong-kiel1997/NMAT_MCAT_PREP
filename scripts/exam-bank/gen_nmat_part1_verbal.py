#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/part1-verbal.yml (30-item NMAT Verbal bank).

Each item is authored as (correct text, [(wrong text, why-wrong note) x 3]).
Letters are assigned from a fixed balanced sequence; the three notes are then
mapped to the three NON-answer letters in ascending letter order, so the
distractor dict can never contain the answer's letter.
"""
import os
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part1-verbal.yml"

# Balanced answer letters: A:8 B:8 C:7 D:7 (max 8).
LETTERS = ["A", "C", "B", "D", "B", "A", "D", "C", "A", "B", "D", "C",
           "B", "A", "C", "D", "C", "B", "A", "D", "A", "C", "B", "D",
           "D", "A", "C", "B", "B", "A"]
assert len(LETTERS) == 30 and Counter(LETTERS) == Counter({"A": 8, "B": 8, "C": 7, "D": 7})

# ---------------------------------------------------------------- analogies
# (stem, answer, [(wrong, note) x3], explain, relation)
ANALOGIES = [
    ("METICULOUS : CAREFUL :: MENDACIOUS : ?",
     "dishonest",
     [("truthful", "Truthful is the opposite of mendacious, not its equivalent."),
      ("careless", "Careless pairs with sloppy, not with mendacious; it merely echoes the first pair."),
      ("hasty", "Hasty describes speed, while mendacious describes untruthfulness.")],
     "Mendacious means given to lying, just as meticulous means careful.",
     "synonyms"),

    ("PLACATE : APPEASE :: OBFUSCATE : ?",
     "confuse",
     [("clarify", "Clarify is the opposite of obfuscate."),
      ("anger", "Anger is what placating relieves; obfuscating does not produce anger."),
      ("ignore", "Ignoring someone leaves them uninformed, but obfuscating actively muddles them.")],
     "Obfuscate means to make unclear, matching the synonym pair placate/appease.",
     "synonyms"),

    ("GARRULOUS : TALKATIVE :: BENEVOLENT : ?",
     "kind",
     [("malevolent", "Malevolent is the antonym of benevolent."),
      ("greedy", "Greedy names self-interest, which benevolence is opposed to."),
      ("wealthy", "Wealth may fund generosity, but benevolence itself is a disposition, not money.")],
     "Benevolent means kind and well-meaning, matching garrulous/talkative.",
     "synonyms"),

    ("STINGY : GENEROUS :: PRODIGAL : ?",
     "thrifty",
     [("lavish", "Lavish is a synonym of prodigal, not its opposite."),
      ("wasteful", "Wasteful restates prodigal; the pair demands a contrast."),
      ("prosperous", "Prosperity is about wealth held, not about how freely one spends it.")],
     "Prodigal means wastefully extravagant, so its opposite is thrifty, as generous opposes stingy.",
     "antonyms"),

    ("TRANSPARENT : OPAQUE :: CANDID : ?",
     "evasive",
     [("honest", "Honest is a synonym of candid, so it fails to supply the contrast."),
      ("blunt", "Blunt candor is still candor; the pair requires an opposite."),
      ("frank", "Frank is another synonym of candid, not its opposite.")],
     "Candid means open and direct, the opposite of evasive, as opaque opposes transparent.",
     "antonyms"),

    ("COMMENCE : CONCLUDE :: INITIATE : ?",
     "terminate",
     [("begin", "Begin is a synonym of initiate, not a contrast to it."),
      ("launch", "Launch also means to start something."),
      ("propose", "Proposing is putting an idea forward, not ending one.")],
     "Initiate is to terminate as commence is to conclude: starting against ending.",
     "antonyms"),

    ("PETAL : FLOWER :: PAGE : ?",
     "book",
     [("library", "A library is a collection of books, one level of organization above a book."),
      ("ink", "Ink is the material a page carries, not the whole the page belongs to."),
      ("chapter", "A chapter is itself only a part of a book, so it cannot be the whole.")],
     "A page is a part of a book, as a petal is a part of a flower.",
     "part-whole"),

    ("CHAPTER : BOOK :: EPISODE : ?",
     "season",
     [("television", "Television is the medium the episode appears on, not a unit composed of episodes."),
      ("commercial", "A commercial interrupts an episode; it is not built out of them."),
      ("series", "A series is made of seasons, one level above the answer.")],
     "An episode is one unit of a season, as a chapter is one unit of a book.",
     "part-whole"),

    ("ISLAND : ARCHIPELAGO :: LETTER : ?",
     "word",
     [("sentence", "Letters form words first; a sentence is built from words, one level up."),
      ("page", "A page holds letters but is not composed of them as a word is."),
      ("pen", "A pen is the instrument used to write, not a whole made of letters.")],
     "A letter is a unit that combines with others to form a word, as an island combines into an archipelago.",
     "part-whole"),

    ("PILOT : COCKPIT :: SURGEON : ?",
     "operating room",
     [("hospital", "A hospital is the larger institution; the surgeon's specific workplace is the operating room."),
      ("waiting room", "The waiting room is where patients sit before treatment."),
      ("pharmacy", "A pharmacy dispenses medication and is not where surgery is performed.")],
     "A surgeon works in an operating room, as a pilot works in a cockpit.",
     "worker-workplace"),

    ("MECHANIC : GARAGE :: PHYSICIAN : ?",
     "clinic",
     [("patient", "The patient is the person worked on, which corresponds to the car, not to the workplace."),
      ("stethoscope", "A stethoscope is an instrument of the trade, not a place of work."),
      ("prescription", "A prescription is an output of the work, not the setting.")],
     "A physician's workplace is a clinic, as a mechanic's is a garage.",
     "worker-workplace"),

    ("FRICTION : HEAT :: VIRUS : ?",
     "illness",
     [("bacteria", "Bacteria are a rival cause of illness, not the effect of a virus."),
      ("medicine", "Medicine treats the illness that follows; it is not produced by the virus."),
      ("immunity", "Immunity is the body's defense against a virus, not its product.")],
     "A virus produces illness, as friction produces heat.",
     "cause-effect"),

    ("CARELESSNESS : ACCIDENT :: INDUSTRY : ?",
     "success",
     [("laziness", "Laziness is the antonym of industry, not its effect."),
      ("factory", "This reads 'industry' as manufacturing; the pair uses it to mean diligent work."),
      ("salary", "A salary is what an employer pays, not what diligence itself produces.")],
     "Industry, meaning diligent effort, brings success, as carelessness brings accidents.",
     "cause-effect"),

    ("BREEZE : GALE :: DRIZZLE : ?",
     "downpour",
     [("cloud", "The cloud is where the rain comes from, not a heavier form of drizzle."),
      ("puddle", "A puddle is water that has already collected on the ground."),
      ("humidity", "Humidity is water vapor in the air, not a volume of falling rain.")],
     "A downpour is drizzle intensified, as a gale is a breeze intensified.",
     "degree"),

    ("PEBBLE : BOULDER :: STREAM : ?",
     "river",
     [("ocean", "An ocean is a far larger category of water body, not the next size up from a stream."),
      ("brook", "A brook is smaller than a stream, which reverses the direction of the scale."),
      ("delta", "A delta is the landform at a river's mouth, not a larger stream.")],
     "A river is a stream on a larger scale, as a boulder is a pebble on a larger scale.",
     "degree"),
]

# ------------------------------------------------- reading comprehension
RC = [
    ("For decades the jeepney has been the backbone of Philippine public transport, prized for low fares "
     "and for routes that reach streets the buses ignore. Under the government's modernization program, older "
     "units are being phased out in favor of minibus-style vehicles with standardized routes and higher fares. "
     "Operators of traditional units warn that the equity payments required for new vehicles would bankrupt "
     "small drivers. Which statement best expresses the main idea of the passage?",
     "Modernization promises cleaner and more orderly service but threatens the livelihoods of small jeepney operators.",
     [("Jeepney fares will fall once vehicles are modernized.",
       "The passage states the new vehicles carry higher fares."),
      ("Buses have already replaced jeepneys on most Philippine routes.",
       "Nothing has been replaced yet; the program is only phasing out older units."),
      ("Jeepneys survive mainly because tourists find them picturesque.",
       "Tourism is never mentioned; the passage credits low fares and wide route coverage.")],
     "The passage weighs the program's promised benefits against the small operators' warning that equity payments would bankrupt them."),

    ("The Ifugao rice terraces of the Cordillera, carved into the mountainside many centuries ago, are watered by "
     "channels that draw from the forests above them. Those forests, called muyong, are tended by families who hold "
     "them in trust for the community; when a watershed is cleared, the springs that feed the channels begin to fail. "
     "According to the passage, the terraces remain productive chiefly because of",
     "the protected forests that feed their irrigation channels.",
     [("modern pumps installed by the national government.",
       "No pumps or government works are mentioned; the water arrives through channels fed by the muyong."),
      ("the mild climate of the lowland plains.",
       "The terraces stand in the mountains, and climate is never given as the reason."),
      ("chemical fertilizers introduced after the Second World War.",
       "The passage attributes productivity to the watershed above, not to fertilizers.")],
     "The passage states that clearing a watershed makes the springs fail, so the protected muyong forests are what keep water flowing to the terraces."),

    ("Jose Rizal printed the first edition of Noli Me Tangere in Berlin in 1887 after borrowing money to cover the "
     "costs. Colonial authorities in Manila banned the book, yet copies crossed into the islands anyway, passed hand "
     "to hand among Filipinos who could read Spanish. Which inference is best supported by the passage?",
     "The novel found Filipino readers despite official prohibition.",
     [("Most Filipinos in 1887 could read Spanish.",
       "The passage says copies passed among those who could read Spanish, which implies such readers were a limited group."),
      ("Spanish friars secretly financed the printing.",
       "The passage says Rizal borrowed money to cover the costs."),
      ("Rizal wrote the novel in Tagalog for a mass audience.",
       "It circulated among readers of Spanish, and no Tagalog version is mentioned.")],
     "A book that circulates hand to hand after being banned shows the prohibition failed to stop its spread."),

    ("Few officials matched Jesse Robredo's habit of taking the bus home to Naga every weekend, or his decision to "
     "post the city's budget online so that any resident could question it. He left behind fewer possessions than many "
     "of the people he had served. The tone of the passage is best described as",
     "admiring",
     [("sarcastic", "Sarcasm would mock its subject; every detail here credits him."),
      ("indifferent", "The writer has selected details that celebrate Robredo, which is the opposite of detachment."),
      ("hostile", "Nothing in the passage criticizes or attacks him.")],
     "The details chosen, from bus rides to published budgets to modest belongings, are all presented favorably."),

    ("The Sinulog festival of Cebu reenacts the acceptance of Christianity through dancers who step twice forward and "
     "once back, a movement said to imitate the sway of the river current. The name sinulog itself comes from the "
     "Cebuano word sulog, meaning current. According to the passage, the festival's name is derived from a word meaning",
     "current",
     [("dance", "The dance is named for the current, not the other way around."),
      ("river", "Sulog names the current of the water, not the river itself."),
      ("Christianity", "The festival commemorates the acceptance of Christianity, but its name comes from sulog.")],
     "The passage states directly that sinulog comes from sulog, which means current."),

    ("Critics once dismissed Taglish, the alternating of Tagalog and English within a single sentence, as evidence of "
     "poor schooling. Linguists now describe it as systematic, governed by rules about where a switch may fall, and note "
     "that bilingual communities around the world behave the same way. Which statement best expresses the main idea of "
     "the passage?",
     "Code-switching follows a grammar of its own rather than reflecting carelessness.",
     [("Taglish should be made the sole language of instruction.",
       "The passage makes no recommendation about schooling policy."),
      ("Linguists agree with the earlier critics of Taglish.",
       "The linguists' view is presented as a correction of the critics', not an endorsement."),
      ("Only Filipino speakers combine languages in one sentence.",
       "The passage says bilingual communities worldwide do the same thing.")],
     "The passage moves from an old criticism to the linguists' finding that the practice is rule-governed and widespread."),

    ("After a dengue outbreak, one barangay emptied its canals and held weekly clean-up drives while neighboring areas "
     "changed nothing, and cases in the barangay fell by half. Health officials point out that the mosquito carrying "
     "dengue breeds in clean, stagnant water collected in containers, drains, and discarded tires. Which inference is "
     "best supported by the passage?",
     "Removing standing water reduced the barangay's dengue cases.",
     [("Dengue is transmitted by dirty canal water.",
       "Mosquitoes, not water, transmit dengue, and the officials specify clean stagnant water."),
      ("The mosquito breeds only in polluted water.",
       "The passage says the opposite: clean, stagnant water."),
      ("The clean-up drives made the outbreak worse.",
       "Cases fell by half after the drives began.")],
     "Cases fell where standing water was removed, which matches the officials' account of where the mosquito breeds."),

    ("Spanish officials described the 1896 uprising as precipitate, by which they meant that it had been launched "
     "before the Katipunan was ready. The Katipunan's leaders answered that waiting longer would only give the "
     "authorities time to hunt them down. As used in the passage, precipitate most nearly means",
     "hasty",
     [("condensed from vapor, as in a chemistry laboratory",
       "That is the laboratory sense of the word; the passage is discussing timing."),
      ("delayed until conditions improved",
       "The officials' complaint was that the uprising came too soon, not too late."),
      ("unusually violent",
       "The objection raised was to the timing of the rising, not to its bloodshed.")],
     "The officials meant the rising came before the Katipunan was ready, which is exactly what hasty conveys."),

    ("Money sent home by overseas Filipino workers amounts to roughly a tenth of the country's economic output, paying "
     "tuition, building houses, and stocking small shops in thousands of towns. Economists caution, however, that such "
     "dependence leaves households exposed when host economies slow, as it did for workers in the Gulf when oil prices "
     "fell. Which statement best expresses the main idea of the passage?",
     "Remittances sustain many families but leave the economy exposed to shocks abroad.",
     [("Remittances are too small to matter to the economy.",
       "The passage places them at about a tenth of economic output."),
      ("Overseas workers exaggerate their earnings to their families.",
       "Nothing in the passage concerns exaggeration or underreporting."),
      ("Host countries deliberately cut migrant wages during downturns.",
       "The passage describes work slowing down, not a deliberate policy.")],
     "The passage sets the scale of remittances against the vulnerability created by relying on foreign labor markets."),

    ("The city unveiled its new flood-control pump station with a brass band and a ribbon, and the pumps failed during "
     "the first heavy rain that same week. Officials have since announced a second, larger station, to be built by the "
     "same contractor. The tone of the passage is best described as",
     "ironic",
     [("celebratory", "The brass band belongs to the city's ceremony; the writer's point is the failure that followed it."),
      ("apologetic", "The writer offers no defense of the officials."),
      ("sorrowful", "The passage registers folly and waste, not grief.")],
     "The deadpan sequence of a ribbon-cutting, an immediate failure, and the same contractor rehired invites the reader to notice the contradiction."),

    ("The tamaraw, a small buffalo found only on the island of Mindoro, once numbered in the thousands. Hunting and the "
     "clearing of habitat have reduced it to a few hundred, and it now survives mainly inside a single protected park "
     "where rangers patrol against poachers. Which inference is best supported by the passage?",
     "The tamaraw's survival depends on protecting the habitat it has left.",
     [("Tamaraws breed readily on other Philippine islands.",
       "The passage says the species is found only on Mindoro."),
      ("Hunting has never been a threat to the species.",
       "Hunting is named as one of the two causes of the decline."),
      ("The park population is already too large for Mindoro.",
       "Only a few hundred survive, so no overcrowding is suggested.")],
     "With only a few hundred animals confined to one park, the species' future turns on keeping that habitat intact."),

    ("The University of Santo Tomas, founded in Manila in 1611, is a quarter of a century older than Harvard, which "
     "opened in 1636. Both institutions began as schools for the training of clergy before expanding into law, medicine, "
     "and the secular disciplines. According to the passage, Harvard differs from Santo Tomas in that Harvard",
     "opened later.",
     [("was founded first.", "Santo Tomas dates from 1611 and Harvard from 1636."),
      ("began as a secular institution.", "The passage says both began by training clergy."),
      ("never expanded beyond theology.", "Both are described as expanding into law, medicine, and other fields.")],
     "The only difference the passage states is the founding date, 1636 against 1611."),

    ("Coconut farmers in Quezon earn little from copra because buyers at the farm gate pay prices set far from the farm. "
     "Cooperatives that mill their own oil and sell directly to processors have raised members' incomes considerably, but "
     "they demand capital and management skills that small farmers rarely have. Which statement best expresses the main "
     "idea of the passage?",
     "Farmer cooperatives can raise incomes, but obstacles keep most small farmers from forming them.",
     [("World demand alone sets the price of copra.",
       "The passage blames farm-gate buyers and prices set far from the farm, not world demand."),
      ("Middlemen should be prohibited by law.",
       "The passage reports the problem; it never calls for a ban."),
      ("Coconut farming cannot be made profitable anywhere.",
       "Cooperatives are described as raising members' incomes considerably.")],
     "The passage pairs the cooperatives' success with the capital and skills they require, which most small farmers lack."),

    ("For two and a half centuries, Manila galleons carried Mexican silver to Manila and Chinese silk, porcelain, and "
     "spices back to Acapulco. The trade enriched a small circle of Spanish merchants inside Intramuros, while most "
     "Filipinos in the countryside went on farming much as before. Which inference is best supported by the passage?",
     "The gains from the galleon trade were concentrated in few hands.",
     [("Filipino farmers directed the galleon trade.",
       "The beneficiaries named are Spanish merchants inside Intramuros."),
      ("The Philippines exported silver to Mexico.",
       "Silver flowed from Mexico to Manila; silk and porcelain went the other way."),
      ("Galleons sailed directly to Spain.",
       "The route named runs between Manila and Acapulco.")],
     "A small circle of merchants profited while the rural majority was untouched, so the benefits were narrow."),

    ("Jeepney drivers pay the vehicle's owner a fixed daily amount called the boundary and keep whatever fare money "
     "remains. Drivers say the arrangement pushes them to stay on the road for shifts of fourteen hours, and that a "
     "driver who falls ill still owes the boundary for that day. According to the passage, the boundary system pressures "
     "drivers to",
     "work shifts far longer than a normal day.",
     [("buy the jeepney from its owner.",
       "No purchase is described; drivers rent the vehicle day by day."),
      ("withhold the boundary when earnings are low.",
       "The passage says the boundary is still owed even when a driver is sick."),
      ("carry fewer passengers to save fuel.",
       "Nothing about fuel or limiting passengers appears in the passage.")],
     "Drivers keep what remains after a fixed payment, so they extend their shifts to cover the boundary and still earn something."),
]


def build():
    items = []
    pool = []
    for stem, ans, wrongs, explain, rel in ANALOGIES:
        pool.append(dict(q=stem, right=ans, wrongs=wrongs, explain=explain, chapter="analogies"))
    for stem, ans, wrongs, explain in RC:
        pool.append(dict(q=stem, right=ans, wrongs=wrongs, explain=explain,
                         chapter="reading-comprehension"))
    assert len(pool) == 30, len(pool)
    assert len({p["q"] for p in pool}) == 30, "duplicate stems"

    for idx, (p, letter) in enumerate(zip(pool, LETTERS), start=1):
        wrong_letters = [L for L in "ABCD" if L != letter]
        assert len(p["wrongs"]) == 3
        choices, distractors = {}, {}
        choices[letter] = p["right"]
        for L, (text, note) in zip(wrong_letters, p["wrongs"]):
            choices[L] = text
            distractors[L] = note
        items.append({
            "id": "nmat-p1v-%03d" % idx,
            "q": p["q"],
            "choices": {L: choices[L] for L in "ABCD"},
            "answer": letter,
            "explain": p["explain"],
            "distractors": {L: distractors[L] for L in wrong_letters},
            "chapter": p["chapter"],
        })
    return {
        "exam": "nmat",
        "section": "part1-verbal",
        "label": "Verbal",
        "subject": "verbal",
        "block": "part1",
        "items_expected": 30,
        "items": items,
        "passages": [],
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
