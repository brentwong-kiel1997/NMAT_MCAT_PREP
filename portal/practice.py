"""Static high-yield practice items (not official past papers)."""

from __future__ import annotations

PRACTICE: dict[str, list[dict]] = {
    "biology": [
        {
            "id": "bio-1",
            "q_zh": "下列哪项最能区分原核细胞与真核细胞？",
            "q_en": "Which best distinguishes prokaryotic from eukaryotic cells?",
            "choices": {
                "A": {"zh": "是否有核糖体", "en": "Presence of ribosomes"},
                "B": {"zh": "是否有膜包被的细胞核", "en": "Membrane-bound nucleus"},
                "C": {"zh": "是否能进行代谢", "en": "Ability to metabolize"},
                "D": {"zh": "是否有细胞膜", "en": "Presence of a cell membrane"},
            },
            "answer": "B",
            "explain_zh": "真核有膜包细胞核与细胞器分区；核糖体与细胞膜两者都有。",
            "explain_en": "Eukaryotes have a membrane-bound nucleus/compartments; both have ribosomes and membranes.",
            "chapter": "Cells and Cellular Processes",
        },
        {
            "id": "bio-2",
            "q_zh": "负反馈的主要作用是：",
            "q_en": "The main role of negative feedback is to:",
            "choices": {
                "A": {"zh": "放大偏离并完成短暂过程", "en": "Amplify deviation to finish a brief process"},
                "B": {"zh": "维持内环境相对稳定", "en": "Keep the internal environment relatively stable"},
                "C": {"zh": "增加突变率", "en": "Increase mutation rate"},
                "D": {"zh": "阻止所有生理变化", "en": "Block all physiological change"},
            },
            "answer": "B",
            "explain_zh": "负反馈抑制偏离设定点；正反馈才放大过程（如分娩）。",
            "explain_en": "Negative feedback opposes drift from set points; positive feedback amplifies (e.g., labor).",
            "chapter": "Life Processes: Regulation and Homeostasis",
        },
        {
            "id": "bio-3",
            "q_zh": "减数分裂对遗传多样性的关键贡献是：",
            "q_en": "A key meiotic contribution to genetic diversity is:",
            "choices": {
                "A": {"zh": "有丝分裂式复制而不分离", "en": "Mitotic copying without segregation"},
                "B": {"zh": "同源重组与独立分配", "en": "Crossing over and independent assortment"},
                "C": {"zh": "删除全部杂合位点", "en": "Deleting all heterozygous loci"},
                "D": {"zh": "阻止 DNA 复制", "en": "Blocking DNA replication"},
            },
            "answer": "B",
            "explain_zh": "交叉互换与同源染色体独立分配重排等位基因组合。",
            "explain_en": "Crossing over and independent assortment reshuffle allele combinations.",
            "chapter": "Genetics",
        },
        {
            "id": "bio-4",
            "q_zh": "生态系统中能量流动的基本特征是：",
            "q_en": "Energy flow in ecosystems is basically:",
            "choices": {
                "A": {"zh": "完全循环且无损失", "en": "Fully cyclic with no loss"},
                "B": {"zh": "单向流动并逐级耗散", "en": "One-way with stepwise dissipation"},
                "C": {"zh": "只在生产者内部循环", "en": "Cycling only inside producers"},
                "D": {"zh": "与物质流动完全相同", "en": "Identical to matter cycling"},
            },
            "answer": "B",
            "explain_zh": "能量单向流经营养级并有热损失；物质可循环。",
            "explain_en": "Energy moves one way with heat loss; matter can cycle.",
            "chapter": "Organisms and Their Environment",
        },
    ],
    "chemistry": [
        {
            "id": "chem-1",
            "q_zh": "缓冲溶液抵抗 pH 变化，主要因为：",
            "q_en": "A buffer resists pH change mainly because it has:",
            "choices": {
                "A": {"zh": "强酸与强碱等量", "en": "Equal strong acid and strong base"},
                "B": {"zh": "弱酸及其共轭碱（或弱碱及其共轭酸）", "en": "A weak acid and its conjugate base (or weak base + conjugate acid)"},
                "C": {"zh": "只有纯水", "en": "Only pure water"},
                "D": {"zh": "金属单质", "en": "Elemental metals"},
            },
            "answer": "B",
            "explain_zh": "弱酸/共轭碱对可中和少量外加酸或碱。",
            "explain_en": "Weak acid/conjugate-base pairs neutralize small added acid or base.",
            "chapter": "General Chemistry",
        },
        {
            "id": "chem-2",
            "q_zh": "Le Chatelier 原理指出：体系平衡被扰动时会：",
            "q_en": "Le Chatelier’s principle says a stressed equilibrium will:",
            "choices": {
                "A": {"zh": "永久停止反应", "en": "Stop reacting forever"},
                "B": {"zh": "向减弱该扰动的方向移动", "en": "Shift to counteract the stress"},
                "C": {"zh": "只向产物方向移动", "en": "Only shift toward products"},
                "D": {"zh": "改变原子种类", "en": "Change atom identities"},
            },
            "answer": "B",
            "explain_zh": "平衡移动以部分抵消浓度/压力/温度扰动。",
            "explain_en": "The system shifts to partially offset concentration/pressure/temperature stress.",
            "chapter": "General Chemistry",
        },
        {
            "id": "chem-3",
            "q_zh": "准确度与精密度的区别是：",
            "q_en": "Accuracy differs from precision in that accuracy is about:",
            "choices": {
                "A": {"zh": "结果彼此靠近", "en": "Results clustering together"},
                "B": {"zh": "结果接近真值", "en": "Results near the true value"},
                "C": {"zh": "仪器价格", "en": "Instrument price"},
                "D": {"zh": "样品颜色", "en": "Sample color"},
            },
            "answer": "B",
            "explain_zh": "准确度看接近真值；精密度看重复性。",
            "explain_en": "Accuracy = closeness to truth; precision = repeatability.",
            "chapter": "Analytical Chemistry",
        },
        {
            "id": "chem-4",
            "q_zh": "催化剂加快反应的方式是：",
            "q_en": "A catalyst speeds a reaction by:",
            "choices": {
                "A": {"zh": "提高反应的 ΔG", "en": "Raising ΔG of the reaction"},
                "B": {"zh": "提供更低活化能的路径", "en": "Providing a lower-activation-energy path"},
                "C": {"zh": "改变产物元素组成", "en": "Changing product element identities"},
                "D": {"zh": "永久消耗反应物平衡常数方向", "en": "Permanently consuming reactants against K"},
            },
            "answer": "B",
            "explain_zh": "催化剂改变路径、降低活化能；不改变总 ΔG / 平衡位置。",
            "explain_en": "Catalysts change the path and lower Ea; overall ΔG / equilibrium position stay the same.",
            "chapter": "5E · Chemical thermodynamics and kinetics",
        },
    ],
    "physics": [
        {
            "id": "phy-1",
            "q_zh": "若对物体做的净功为正，则其动能：",
            "q_en": "If net work on an object is positive, its kinetic energy:",
            "choices": {
                "A": {"zh": "一定减少", "en": "Must decrease"},
                "B": {"zh": "一定增加", "en": "Must increase"},
                "C": {"zh": "不变", "en": "Stays the same"},
                "D": {"zh": "与功无关", "en": "Is unrelated to work"},
            },
            "answer": "B",
            "explain_zh": "功-能定理：净功等于动能变化。",
            "explain_en": "Work–energy theorem: net work equals change in kinetic energy.",
            "chapter": "Mechanics",
        },
        {
            "id": "phy-2",
            "q_zh": "理想流体连续方程的核心含义是：",
            "q_en": "The continuity equation for ideal flow mainly says:",
            "choices": {
                "A": {"zh": "截面积减小则流速增大（体积流量守恒）", "en": "Smaller area → higher speed (volume flow conserved)"},
                "B": {"zh": "压力处处相等", "en": "Pressure is equal everywhere"},
                "C": {"zh": "温度必须升高", "en": "Temperature must rise"},
                "D": {"zh": "密度必须为零", "en": "Density must be zero"},
            },
            "answer": "A",
            "explain_zh": "不可压缩流：A₁v₁ = A₂v₂。",
            "explain_en": "For incompressible flow: A₁v₁ = A₂v₂.",
            "chapter": "4B · Fluids, circulation, gas exchange",
        },
        {
            "id": "phy-3",
            "q_zh": "欧姆定律把电压、电流、电阻联系起来为：",
            "q_en": "Ohm’s law relates V, I, and R as:",
            "choices": {
                "A": {"zh": "V = I/R", "en": "V = I/R"},
                "B": {"zh": "V = IR", "en": "V = IR"},
                "C": {"zh": "V = I + R", "en": "V = I + R"},
                "D": {"zh": "V = R/I", "en": "V = R/I"},
            },
            "answer": "B",
            "explain_zh": "V = IR 是线性电阻的基本关系。",
            "explain_en": "V = IR is the basic linear-resistor relation.",
            "chapter": "Electricity and Magnetism",
        },
    ],
    "behavioral-social": [
        {
            "id": "beh-1",
            "q_zh": "经典条件反射中，条件刺激最初是：",
            "q_en": "In classical conditioning, the conditioned stimulus starts as:",
            "choices": {
                "A": {"zh": "已能引发反应的刺激", "en": "A stimulus that already elicits the response"},
                "B": {"zh": "中性刺激，经配对后引发反应", "en": "A neutral stimulus that comes to elicit the response after pairing"},
                "C": {"zh": "惩罚物", "en": "A punisher"},
                "D": {"zh": "强化程式", "en": "A reinforcement schedule"},
            },
            "answer": "B",
            "explain_zh": "中性刺激与无条件刺激配对后成为条件刺激。",
            "explain_en": "A neutral cue paired with a UCS becomes a CS.",
            "chapter": "Psychology",
        },
        {
            "id": "beh-2",
            "q_zh": "基本归因错误倾向于：",
            "q_en": "The fundamental attribution error tends to:",
            "choices": {
                "A": {"zh": "高估情境、低估个性", "en": "Overweight situation, underweight disposition"},
                "B": {"zh": "高估个性、低估情境", "en": "Overweight disposition, underweight situation"},
                "C": {"zh": "否认一切归因", "en": "Deny all attribution"},
                "D": {"zh": "只发生在实验室", "en": "Occur only in labs"},
            },
            "answer": "B",
            "explain_zh": "观察他人时常过度归因于人格而非情境。",
            "explain_en": "Observers over-attribute others’ acts to personality vs situation.",
            "chapter": "FC8 · Self, others, interactions",
        },
    ],
    "biochemistry": [
        {
            "id": "bioc-1",
            "q_zh": "酶通过下列哪项加速反应？",
            "q_en": "Enzymes speed reactions primarily by:",
            "choices": {
                "A": {"zh": "提高反应温度", "en": "Raising temperature"},
                "B": {"zh": "降低活化能", "en": "Lowering activation energy"},
                "C": {"zh": "改变 ΔG° 正负号", "en": "Changing the sign of ΔG°"},
                "D": {"zh": "消灭所有产物", "en": "Destroying all products"},
            },
            "answer": "B",
            "explain_zh": "酶稳定过渡态、降低活化能；不改变总热力学 ΔG。",
            "explain_en": "Enzymes stabilize the transition state and lower Ea; overall ΔG is unchanged.",
            "chapter": "1A · Proteins and amino acids",
        },
        {
            "id": "bioc-2",
            "q_zh": "氧化磷酸化直接依赖：",
            "q_en": "Oxidative phosphorylation most directly depends on:",
            "choices": {
                "A": {"zh": "跨线粒体内膜的质子梯度", "en": "A proton gradient across the inner mitochondrial membrane"},
                "B": {"zh": "细胞核内的转录速率", "en": "Nuclear transcription rate"},
                "C": {"zh": "细胞膜胆固醇比例 alone", "en": "Plasma-membrane cholesterol alone"},
                "D": {"zh": "高尔基体出芽", "en": "Golgi budding"},
            },
            "answer": "A",
            "explain_zh": "ETC 泵质子，ATP 合酶利用质子回流合成 ATP。",
            "explain_en": "ETC pumps protons; ATP synthase uses the return flow.",
            "chapter": "1D · Bioenergetics and fuel metabolism",
        },
    ],
    "verbal": [
        {
            "id": "verb-1",
            "q_zh": "WORD : DICTIONARY :: NOTE : ?",
            "q_en": "WORD : DICTIONARY :: NOTE : ?",
            "choices": {
                "A": {"zh": "Symphony（交响曲）", "en": "Symphony"},
                "B": {"zh": "Composer（作曲家）", "en": "Composer"},
                "C": {"zh": "Silence（沉默）", "en": "Silence"},
                "D": {"zh": "Volume（音量）", "en": "Volume"},
            },
            "answer": "A",
            "explain_zh": "词收录于词典；音符组织成交响曲（部分-整体/收录关系）。",
            "explain_en": "Words are collected in a dictionary; notes are organized into a symphony.",
            "chapter": "Analogies（词义类比）",
        },
        {
            "id": "verb-2",
            "q_zh": "阅读理解中，细节题最稳妥的策略是：",
            "q_en": "For reading-comprehension detail items, the safest move is to:",
            "choices": {
                "A": {"zh": "凭第一印象选", "en": "Trust first impressions"},
                "B": {"zh": "回原文定位再比选项", "en": "Relocate in the passage, then compare options"},
                "C": {"zh": "选最长选项", "en": "Pick the longest option"},
                "D": {"zh": "忽略转折词", "en": "Ignore contrast markers"},
            },
            "answer": "B",
            "explain_zh": "细节必须有文本依据，回文定位最稳。",
            "explain_en": "Details need textual support — relocate first.",
            "chapter": "Reading Comprehension（阅读理解）",
        },
    ],
    "inductive-reasoning": [
        {
            "id": "ind-1",
            "q_zh": "图形序列题优先做什么？",
            "q_en": "On figure-series items, prioritize:",
            "choices": {
                "A": {"zh": "同时猜所有规则再放弃", "en": "Guessing every rule at once then quitting"},
                "B": {"zh": "分开跟踪位置、数量、填充、旋转", "en": "Tracking position, count, fill, and rotation separately"},
                "C": {"zh": "只看颜色忽略形状", "en": "Only color, ignore shape"},
                "D": {"zh": "随机选中间项", "en": "Picking the middle option"},
            },
            "answer": "B",
            "explain_zh": "多规则常叠加；分线索更稳。",
            "explain_en": "Rules often stack — separate threads are safer.",
            "chapter": "Figure Series（图形序列）",
        }
    ],
    "quantitative": [
        {
            "id": "quant-1",
            "q_zh": "资料判读第一步通常是：",
            "q_en": "Data-interpretation items usually start by:",
            "choices": {
                "A": {"zh": "先算再看题", "en": "Computing before reading the question"},
                "B": {"zh": "读轴、图例与单位", "en": "Reading axes, legend, and units"},
                "C": {"zh": "忽略标题", "en": "Ignoring the title"},
                "D": {"zh": "只看最大数字", "en": "Looking only at the largest number"},
            },
            "answer": "B",
            "explain_zh": "轴与单位决定数字含义。",
            "explain_en": "Axes and units define what numbers mean.",
            "chapter": "Data Interpretation（资料判读）",
        }
    ],
    "perceptual-acuity": [
        {
            "id": "perc-1",
            "q_zh": "镜像题中最关键的提醒是：",
            "q_en": "The key reminder on mirror-image items is:",
            "choices": {
                "A": {"zh": "镜像等于旋转 180°", "en": "A mirror equals a 180° rotation"},
                "B": {"zh": "左右镜像不等于旋转", "en": "Left–right mirroring is not the same as rotation"},
                "C": {"zh": "可以忽略不对称点", "en": "Asymmetric features can be ignored"},
                "D": {"zh": "只比较面积", "en": "Only compare area"},
            },
            "answer": "B",
            "explain_zh": "镜像翻转左右关系；旋转保持手性方向不同。",
            "explain_en": "Mirroring flips left–right; rotation is a different transform.",
            "chapter": "Mirror Image（镜像）",
        }
    ],
    "cars": [
        {
            "id": "cars-1",
            "q_zh": "CARS 中“说得对但文中未出现”的选项通常：",
            "q_en": "On CARS, an option that is true in the world but absent from the passage is usually:",
            "choices": {
                "A": {"zh": "应优先选择", "en": "Preferred"},
                "B": {"zh": "强干扰项，应排除", "en": "A strong distractor to eliminate"},
                "C": {"zh": "等于主旨", "en": "Equal to the main idea"},
                "D": {"zh": "证明作者偏见", "en": "Proof of author bias"},
            },
            "answer": "B",
            "explain_zh": "CARS 依据文本；外部正确事实若文中无支持就不能选。",
            "explain_en": "CARS is passage-bound; externally true claims without textual support are traps.",
            "chapter": "Reasoning Within the Text",
        },
        {
            "id": "cars-2",
            "q_zh": "Topic 与 Thesis 的关系是：",
            "q_en": "Topic relates to thesis as:",
            "choices": {
                "A": {"zh": "二者永远相同", "en": "Always identical"},
                "B": {"zh": "Topic 是题材，Thesis 是作者主张", "en": "Topic is the subject; thesis is the author’s claim"},
                "C": {"zh": "Thesis 只出现在最后一句", "en": "Thesis only appears in the last sentence"},
                "D": {"zh": "Topic 比 Thesis 更重要所以可不读主张", "en": "Topic matters more so claims can be ignored"},
            },
            "answer": "B",
            "explain_zh": "先分清写什么与主张什么。",
            "explain_en": "Separate what it’s about from what it argues.",
            "chapter": "Foundations of Comprehension",
        },
    ],
    "chem-phys": [
        {
            "id": "cp-1",
            "q_zh": "血管半径略减时，层流流量通常：",
            "q_en": "A small drop in vessel radius typically makes laminar flow:",
            "choices": {
                "A": {"zh": "几乎不变", "en": "Almost unchanged"},
                "B": {"zh": "显著下降（对半径高度敏感）", "en": "Drop sharply (highly radius-sensitive)"},
                "C": {"zh": "一定升高", "en": "Must rise"},
                "D": {"zh": "与半径无关", "en": "Independent of radius"},
            },
            "answer": "B",
            "explain_zh": "Poiseuille 关系中流量与半径四次方相关。",
            "explain_en": "Poiseuille flow scales with radius to the fourth power.",
            "chapter": "4B · Fluids for circulation and gas exchange",
        }
    ],
    "bio-biochem": [
        {
            "id": "bb-1",
            "q_zh": "肽键形成时发生的是：",
            "q_en": "Peptide-bond formation involves:",
            "choices": {
                "A": {"zh": "水解消耗水", "en": "Hydrolysis that consumes water"},
                "B": {"zh": "缩合脱水连接氨基酸", "en": "Condensation linking amino acids with water loss"},
                "C": {"zh": "打破所有氢键", "en": "Breaking all hydrogen bonds"},
                "D": {"zh": "改变元素种类", "en": "Changing element identities"},
            },
            "answer": "B",
            "explain_zh": "羧基与氨基缩合脱水形成肽键；水解则相反。",
            "explain_en": "Carboxyl + amino condense with water loss; hydrolysis reverses it.",
            "chapter": "1A · Proteins and amino acids",
        }
    ],
    "psych-soc": [
        {
            "id": "ps-1",
            "q_zh": "绝对阈值指的是：",
            "q_en": "An absolute threshold is:",
            "choices": {
                "A": {"zh": "刚能察觉刺激的最小强度（统计定义下）", "en": "The minimum intensity detectable (under a statistical definition)"},
                "B": {"zh": "两刺激间可分辨的最小差别", "en": "The smallest difference between two stimuli"},
                "C": {"zh": "最大可耐受刺激", "en": "The maximum tolerable stimulus"},
                "D": {"zh": "反应时平均值", "en": "Mean reaction time"},
            },
            "answer": "A",
            "explain_zh": "绝对阈值是察觉有无；差别阈值是分辨差异。",
            "explain_en": "Absolute = detect presence; difference = detect change.",
            "chapter": "6A · Sensing the environment",
        }
    ],
}


LABELS = {
    "biology": {"zh": "生物学", "en": "Biology"},
    "chemistry": {"zh": "化学", "en": "Chemistry"},
    "physics": {"zh": "物理", "en": "Physics"},
    "behavioral-social": {"zh": "行为与社会", "en": "Behavioral & Social"},
    "biochemistry": {"zh": "生物化学", "en": "Biochemistry"},
    "verbal": {"zh": "言语", "en": "Verbal"},
    "inductive-reasoning": {"zh": "归纳推理", "en": "Inductive Reasoning"},
    "quantitative": {"zh": "数量", "en": "Quantitative"},
    "perceptual-acuity": {"zh": "知觉敏锐", "en": "Perceptual Acuity"},
    "chem-phys": {"zh": "Chem/Phys", "en": "Chem/Phys"},
    "cars": {"zh": "CARS", "en": "CARS"},
    "bio-biochem": {"zh": "Bio/Biochem", "en": "Bio/Biochem"},
    "psych-soc": {"zh": "Psych/Soc", "en": "Psych/Soc"},
}


def practice_for(slug: str) -> list[dict]:
    try:
        from knowledge.models import PracticeQuestion

        qs = PracticeQuestion.objects.filter(subject_slug=slug).order_by(
            "sort_order", "id"
        )
        rows = [q.as_dict() for q in qs]
        if rows:
            return rows
    except Exception:
        pass
    return list(PRACTICE.get(slug) or [])


def all_practice_slugs() -> list[str]:
    try:
        from knowledge.models import PracticeQuestion

        slugs = list(
            PracticeQuestion.objects.order_by("subject_slug")
            .values_list("subject_slug", flat=True)
            .distinct()
        )
        if slugs:
            return slugs
    except Exception:
        pass
    return sorted(PRACTICE.keys())


def practice_catalog() -> list[dict]:
    out = []
    for slug in all_practice_slugs():
        label = LABELS.get(slug, {"zh": slug, "en": slug})
        try:
            from knowledge.models import PracticeQuestion, SubjectRef

            ref = SubjectRef.objects.filter(slug=slug).first()
            if ref:
                label = {"zh": ref.label_zh, "en": ref.label_en}
            count = PracticeQuestion.objects.filter(subject_slug=slug).count()
            if not count:
                count = len(PRACTICE.get(slug) or [])
        except Exception:
            count = len(PRACTICE.get(slug) or [])
        out.append(
            {
                "slug": slug,
                "label_zh": label["zh"],
                "label_en": label["en"],
                "count": count,
            }
        )
    return out
