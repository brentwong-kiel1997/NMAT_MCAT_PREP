"""Second enrichment pack: denser notes, more MCQs, glossary, tips, checklists.

Merged at import time by notes / practice / materials_data helpers.
"""

from __future__ import annotations

import copy

# —— Extra high-yield note bullets (thin chapters first) ——
PACK_NOTES: dict[str, dict[str, list[dict[str, str]]]] = {
    "chemistry": {
        "4E · Atoms, nuclear decay, electronic structure": [
            {"zh": "α 衰变减核电荷 2、质量数 4；β⁻ 增质子数 1", "en": "α decay: −2 Z, −4 A; β⁻ decay: +1 proton"},
            {"zh": "半衰期与初始量无关；指数衰减 N=N₀e^(−λt)", "en": "Half-life independent of amount; N=N₀e^(−λt)"},
            {"zh": "电子构型决定周期表族化学相似性", "en": "Electron configuration drives group chemical similarity"},
            {"zh": "电离能沿周期大致升高；原子半径大致减小", "en": "Ionization energy rises across a period; atomic radius shrinks"},
        ],
        "5B · Molecules and intermolecular interactions": [
            {"zh": "氢键：N/O/F 与 H 的强偶极作用", "en": "H-bonds: strong dipole interactions with H on N/O/F"},
            {"zh": "伦敦色散随极化率与表面积增大", "en": "London dispersion grows with polarizability and surface area"},
            {"zh": "极性分子偶极–偶极提高沸点", "en": "Dipole–dipole interactions raise boiling points of polar molecules"},
        ],
        "5C · Separation and purification methods": [
            {"zh": "蒸馏按沸点差分离液体混合物", "en": "Distillation separates liquids by boiling-point differences"},
            {"zh": "萃取利用分配系数在两相间转移溶质", "en": "Extraction moves solute between phases by partition coefficient"},
            {"zh": "色谱：固定相亲和差异 → 保留时间不同", "en": "Chromatography: affinity for stationary phase → different retention"},
        ],
        "5D · Biologically relevant molecules": [
            {"zh": "氨基酸两性：羧基与氨基可质子化/去质子化", "en": "Amino acids are zwitterionic; carboxyl and amino groups ionize"},
            {"zh": "糖：醛糖/酮糖；环状半缩醛形式常见", "en": "Sugars: aldose/ketose; cyclic hemiacetals dominate in solution"},
            {"zh": "脂质：疏水尾驱动双层自组装", "en": "Lipids: hydrophobic tails drive bilayer self-assembly"},
        ],
        "5E · Chemical thermodynamics and kinetics": [
            {"zh": "ΔG° = −RT ln K；K>1 偏向产物", "en": "ΔG° = −RT ln K; K>1 favors products"},
            {"zh": "催化剂降活化能，不改 ΔG 或平衡组成", "en": "Catalysts lower Ea; they do not change ΔG or equilibrium composition"},
            {"zh": "速率定律由机制决定，不一定等于总反应计量", "en": "Rate law follows mechanism, not necessarily overall stoichiometry"},
        ],
    },
    "physics": {
        "4E · Atoms, nuclear decay, electronic structure": [
            {"zh": "光子能量 E=hf=hc/λ；光电效应 KE_max=hf−φ", "en": "Photon energy E=hf=hc/λ; photoelectric KE_max=hf−φ"},
            {"zh": "玻尔模型：能级量子化；吸收/发射对应跃迁", "en": "Bohr model: quantized levels; absorption/emission from transitions"},
            {"zh": "结合能缺陷：质量亏损转化为核能", "en": "Binding energy: mass defect converts to nuclear energy"},
        ],
        "4D · Light and sound interacting with matter": [
            {"zh": "反射：入射角=反射角；折射遵循斯涅尔定律", "en": "Reflection: i=r; refraction follows Snell’s law"},
            {"zh": "干涉条件：光程差为 λ 整数倍（相长）", "en": "Interference: path difference of integer λ → constructive"},
            {"zh": "声音强度级用分贝；对数压缩动态范围", "en": "Sound intensity level in dB compresses dynamic range logarithmically"},
            {"zh": "多普勒：靠近升高频率，远离降低", "en": "Doppler: approach raises frequency; recession lowers it"},
        ],
    },
    "chem-phys": {
        "4E · Atoms, nuclear decay, electronic structure": [
            {"zh": "MCAT：核衰变常与半衰期、半衰期曲线读图联考", "en": "MCAT often pairs nuclear decay with half-life graphs"},
            {"zh": "电子跃迁能量差对应吸收/发射光谱线", "en": "Electronic energy gaps map to absorption/emission lines"},
            {"zh": "质量数 A = 质子 + 中子；同位素同 Z 异 A", "en": "Mass number A = protons + neutrons; isotopes share Z, differ in A"},
        ],
        "5B · Molecules and intermolecular interactions": [
            {"zh": "分子间力强弱：离子 > 氢键 > 偶极 > 色散（粗略）", "en": "Rough IMF strength: ionic > H-bond > dipole > dispersion"},
            {"zh": "理想溶液拉乌尔定律：蒸气压与摩尔分数相关", "en": "Raoult’s law: vapor pressure tracks mole fraction in ideal solutions"},
        ],
        "5C · Separation and purification methods": [
            {"zh": "薄层色谱 Rf = 斑点距离 / 溶剂前沿距离", "en": "TLC Rf = spot distance / solvent-front distance"},
            {"zh": "电泳按电荷/质量比分离；等电点用于蛋白", "en": "Electrophoresis separates by charge/mass; pI used for proteins"},
        ],
        "5D · Biologically relevant molecules": [
            {"zh": "磷酸二酯键连接核酸主链", "en": "Phosphodiester bonds link nucleic-acid backbones"},
            {"zh": "肽键平面共振限制旋转", "en": "Peptide-bond resonance planarizes and restricts rotation"},
        ],
        "5E · Chemical thermodynamics and kinetics": [
            {"zh": "篇章常给能量图：读出 ΔH、Ea、中间体", "en": "Passage energy diagrams: read ΔH, Ea, and intermediates"},
            {"zh": "零级/一级/二级：浓度–时间图形状不同", "en": "Zero/first/second order: distinct concentration–time plots"},
        ],
        "4D · Light and sound interacting with matter": [
            {"zh": "超声成像依赖反射与组织声阻抗差", "en": "Ultrasound imaging uses reflection from acoustic-impedance mismatches"},
            {"zh": "透镜公式 1/f=1/o+1/i；放大率 m=−i/o", "en": "Lens: 1/f=1/o+1/i; magnification m=−i/o"},
        ],
    },
    "biochemistry": {
        "Amino acids, peptides, and proteins": [
            {"zh": "必需氨基酸须从饮食摄入", "en": "Essential amino acids must come from the diet"},
            {"zh": "一级结构：肽键序列；高级结构靠非共价作用", "en": "Primary structure is peptide sequence; higher orders use noncovalent forces"},
            {"zh": "变性破坏高级结构，不一定断肽键", "en": "Denaturation disrupts higher structure without necessarily breaking peptide bonds"},
        ],
        "Enzymes and regulation": [
            {"zh": "别构效应：效应物结合远位点改变活性", "en": "Allostery: effector at a distant site changes activity"},
            {"zh": "反馈抑制：通路末端产物抑制上游酶", "en": "Feedback inhibition: end product inhibits an upstream enzyme"},
            {"zh": "协同酶：底物结合改变其他亚基亲和力", "en": "Cooperative enzymes: substrate binding alters affinity of other subunits"},
        ],
        "Metabolism and bioenergetics": [
            {"zh": "糖异生主要在肝；逆转糖酵解非平衡步骤", "en": "Gluconeogenesis is mainly hepatic; bypasses irreversible glycolytic steps"},
            {"zh": "酮体在长期禁食时供脑部分能量", "en": "Ketone bodies partially fuel the brain in prolonged fasting"},
            {"zh": "NADH/FADH₂ 进入 ETC 的入口不同，ATP 当量不同", "en": "NADH and FADH₂ enter the ETC at different points → different ATP yields"},
        ],
        "Nucleic acids and gene expression": [
            {"zh": "密码子简并：多数氨基酸对应多个密码子", "en": "Codon degeneracy: most amino acids have multiple codons"},
            {"zh": "剪接：内含子去除；可变剪接增加蛋白多样", "en": "Splicing removes introns; alternative splicing increases protein diversity"},
        ],
        "Lab techniques and analysis": [
            {"zh": "PCR：变性–退火–延伸循环扩增 DNA", "en": "PCR: denature–anneal–extend cycles amplify DNA"},
            {"zh": "Western blot 检测特定蛋白；Southern 检测 DNA", "en": "Western detects specific proteins; Southern detects DNA"},
        ],
    },
    "bio-biochem": {
        "1A · Proteins and amino acids": [
            {"zh": "侧链分类：非极性、极性不带电、酸碱性", "en": "Side-chain classes: nonpolar, polar uncharged, acidic/basic"},
            {"zh": "二硫键稳定胞外蛋白三级/四级结构", "en": "Disulfide bonds stabilize extracellular tertiary/quaternary structure"},
            {"zh": "血红蛋白协同与波尔效应：O₂ 与 CO₂/H⁺ 互调", "en": "Hb cooperativity and Bohr effect: O₂ traded with CO₂/H⁺"},
        ],
        "1B · Gene to protein": [
            {"zh": "启动子与转录因子决定表达时机", "en": "Promoters and transcription factors set expression timing"},
            {"zh": "tRNA 反密码子配对 mRNA；氨酰-tRNA 合成酶保真", "en": "tRNA anticodons pair mRNA; aminoacyl-tRNA synthetases ensure fidelity"},
            {"zh": "翻译：起始→延伸→终止；核糖体三相位点", "en": "Translation: initiation→elongation→termination; A/P/E sites"},
        ],
        "1C · Heritable information & diversity": [
            {"zh": "点突变 vs 移码：后果严重程度常不同", "en": "Point vs frameshift mutations often differ in severity"},
            {"zh": "杂合优势可维持有害等位基因频率", "en": "Heterozygote advantage can maintain deleterious allele frequencies"},
        ],
        "1D · Bioenergetics and fuel metabolism": [
            {"zh": "进食态：胰岛素主导储存；空腹：胰高血糖素动员", "en": "Fed: insulin-driven storage; fasting: glucagon mobilization"},
            {"zh": "β 氧化在线粒体基质产生乙酰 CoA", "en": "β-oxidation in the mitochondrial matrix yields acetyl-CoA"},
        ],
        "2A · Assemblies of molecules, cells, cell groups": [
            {"zh": "细胞骨架：微管、微丝、中间丝分工", "en": "Cytoskeleton roles: microtubules, microfilaments, intermediate filaments"},
            {"zh": "细胞外基质胶原提供张力强度", "en": "ECM collagen supplies tensile strength"},
        ],
        "2B · Prokaryotes and viruses": [
            {"zh": "质粒可携带抗性基因水平转移", "en": "Plasmids can carry resistance genes via horizontal transfer"},
            {"zh": "病毒生活史：吸附→进入→复制→装配→释放", "en": "Viral life cycle: attach→enter→replicate→assemble→release"},
        ],
    },
    "behavioral-social": {
        "FC6 · Perceive, think, react": [
            {"zh": "感觉适应：持续刺激下感受器反应下降", "en": "Sensory adaptation: receptor response falls with sustained stimulus"},
            {"zh": "工作记忆容量有限；组块可扩大有效容量", "en": "Working memory is limited; chunking expands effective capacity"},
            {"zh": "情绪与决策：边缘系统与前额叶互动", "en": "Emotion and decision-making: limbic–prefrontal interaction"},
        ],
        "FC9 · Cultural and social differences": [
            {"zh": "文化相对主义：按文化语境理解行为", "en": "Cultural relativism: interpret behavior in cultural context"},
            {"zh": "同化 vs 多元文化：融入主流或保持多元认同", "en": "Assimilation vs multiculturalism: merge vs retain plural identities"},
            {"zh": "健康信念模型：感知威胁与效能影响就医", "en": "Health belief model: perceived threat and efficacy shape care-seeking"},
        ],
    },
    "inductive-reasoning": {
        "Figure Grouping（图形归类）": [
            {"zh": "先找共同特征：边数、对称、填充、旋转", "en": "Seek shared features: sides, symmetry, fill, rotation"},
            {"zh": "排除“几乎一样”的干扰项", "en": "Eliminate near-miss distractors that almost match"},
            {"zh": "分组常按规则一致性，而非主观好看", "en": "Group by rule consistency, not subjective preference"},
        ],
    },
    "perceptual-acuity": {
        "Hidden Figure（隐藏图形）": [
            {"zh": "锁定目标轮廓，忽略背景纹理", "en": "Lock onto target contours; ignore background texture"},
            {"zh": "旋转/镜像后仍识别同一形状", "en": "Recognize the same shape after rotation or mirroring"},
        ],
        "Identical Information（相同信息）": [
            {"zh": "逐项比对数字/字母串，防漏看一位", "en": "Compare digit/letter strings item-by-item; don’t skip a place"},
            {"zh": "注意大小写与符号差异", "en": "Watch case and symbol differences"},
        ],
        "Mirror Image（镜像）": [
            {"zh": "先判镜像轴（竖直/水平），再比对特征", "en": "Decide mirror axis (vertical/horizontal), then compare features"},
            {"zh": "旋转 ≠ 镜像；易混干扰项常见", "en": "Rotation ≠ reflection; common trap distractors"},
        ],
    },
    "verbal": {
        "Analogies（词义类比）": [
            {"zh": "先写清 A:B 关系，再套到 C:?", "en": "State the A:B relation first, then map C:?"},
            {"zh": "常见关系：同义、反义、部分–整体、因果、程度", "en": "Common relations: synonym, antonym, part–whole, cause, degree"},
        ],
        "Reading Comprehension（阅读理解）": [
            {"zh": "主旨题优先看首尾段与转折词", "en": "Main-idea items: prioritize openings, closings, and contrast markers"},
            {"zh": "细节题回文定位，忌凭记忆选题", "en": "Detail items: return to the text; don’t rely on memory alone"},
        ],
        "Word Analogies / Vocabulary": [
            {"zh": "先写清 A:B 关系，再套到 C:?", "en": "State the A:B relation first, then map C:?"},
            {"zh": "常见关系：同义、反义、部分–整体、因果、程度", "en": "Common relations: synonym, antonym, part–whole, cause, degree"},
        ],
        "Reading Comprehension / Verbal Ability": [
            {"zh": "主旨题优先看首尾段与转折词", "en": "Main-idea items: prioritize openings, closings, and contrast markers"},
            {"zh": "细节题回文定位，忌凭记忆选题", "en": "Detail items: return to the text; don’t rely on memory alone"},
        ],
    },
    "quantitative": {
        "Fundamental Operations（基本运算）": [
            {"zh": "先估数量级，再精算；排除离谱选项", "en": "Estimate magnitude first, then compute; drop absurd choices"},
            {"zh": "百分数变化：分清“增加了多少点”与“增加了百分之几”", "en": "Percent change: distinguish percentage points from relative percent"},
        ],
        "Problem Solving（应用题）": [
            {"zh": "设未知数，翻译句子为方程", "en": "Define unknowns and translate sentences into equations"},
            {"zh": "单位换算先统一再计算", "en": "Convert units to a common system before computing"},
        ],
        "Data Interpretation（资料判读）": [
            {"zh": "图表题先读轴标签与单位", "en": "Graph items: read axis labels and units first"},
            {"zh": "均值受极端值拉扯；中位数更稳健", "en": "Mean is pulled by outliers; median is more robust"},
        ],
        "Arithmetic and Number Sense": [
            {"zh": "先估数量级，再精算；排除离谱选项", "en": "Estimate magnitude first, then compute; drop absurd choices"},
            {"zh": "百分数变化：分清“增加了多少点”与“增加了百分之几”", "en": "Percent change: distinguish percentage points from relative percent"},
        ],
        "Algebra, Data, and Word Problems": [
            {"zh": "设未知数，翻译句子为方程", "en": "Define unknowns and translate sentences into equations"},
            {"zh": "图表题先读轴标签与单位", "en": "Graph items: read axis labels and units first"},
        ],
        "Probability and Basic Statistics": [
            {"zh": "独立事件 P(A∩B)=P(A)P(B)", "en": "Independent events: P(A∩B)=P(A)P(B)"},
            {"zh": "均值受极端值拉扯；中位数更稳健", "en": "Mean is pulled by outliers; median is more robust"},
        ],
    },
    "cars": {
        "Foundations of Comprehension": [
            {"zh": "标出作者态度词：强调、质疑、让步", "en": "Mark attitude cues: emphasis, skepticism, concession"},
            {"zh": "段落功能：举例、对比、定义、推进论点", "en": "Paragraph jobs: exemplify, contrast, define, advance claim"},
        ],
        "Reasoning Within the Text": [
            {"zh": "推断必须被文本支持，不能引入课外知识当证据", "en": "Inferences must be text-supported; outside knowledge isn’t evidence"},
            {"zh": "找支持句：同义改写常是正确答案特征", "en": "Find support lines: correct answers often paraphrase the text"},
        ],
        "Reasoning Beyond the Text": [
            {"zh": "应用题：把文中原则迁移到新情境", "en": "Application: transfer a passage principle to a new scenario"},
            {"zh": "削弱/加强：瞄准论证的关键假设", "en": "Weaken/strengthen: target the argument’s key assumption"},
        ],
    },
    "psych-soc": {
        "6A · Sensing the environment": [
            {"zh": "绝对阈值 vs 差别阈值（Weber）", "en": "Absolute threshold vs difference threshold (Weber)"},
            {"zh": "信号检测：击中、虚报、漏报、正确拒绝", "en": "Signal detection: hit, false alarm, miss, correct rejection"},
        ],
        "6B · Making sense of the environment": [
            {"zh": "自上而下加工：期望与知识塑造知觉", "en": "Top-down processing: expectations and knowledge shape perception"},
            {"zh": "格式塔原则：邻近、相似、闭合、连续", "en": "Gestalt: proximity, similarity, closure, continuity"},
        ],
        "6C · Responding to the world": [
            {"zh": "应激：警报–抵抗–耗竭（GAS）", "en": "Stress: alarm–resistance–exhaustion (GAS)"},
            {"zh": "应对：问题中心 vs 情绪中心", "en": "Coping: problem-focused vs emotion-focused"},
        ],
    },
}


PACK_PRACTICE: dict[str, list[dict]] = {
    "biology": [
        {
            "id": "bio-13",
            "q_zh": "转录主要发生在真核细胞的何处？",
            "q_en": "Where does transcription mainly occur in eukaryotic cells?",
            "choices": {
                "A": {"zh": "细胞质", "en": "Cytoplasm"},
                "B": {"zh": "细胞核", "en": "Nucleus"},
                "C": {"zh": "高尔基体", "en": "Golgi apparatus"},
                "D": {"zh": "溶酶体", "en": "Lysosome"},
            },
            "answer": "B",
            "explain_zh": "真核转录在核内；翻译在细胞质核糖体。",
            "explain_en": "Eukaryotic transcription is nuclear; translation occurs on cytoplasmic ribosomes.",
            "chapter": "Genetics",
        },
        {
            "id": "bio-14",
            "q_zh": "下列哪项最符合自然选择？",
            "q_en": "Which best matches natural selection?",
            "choices": {
                "A": {"zh": "个体主动改变基因以适应环境", "en": "Individuals actively change genes to fit the environment"},
                "B": {"zh": "有利变异个体留下更多后代", "en": "Individuals with advantageous variants leave more offspring"},
                "C": {"zh": "所有变异同等传递", "en": "All variants are transmitted equally"},
                "D": {"zh": "环境直接创造所需突变", "en": "The environment directly creates needed mutations"},
            },
            "answer": "B",
            "explain_zh": "选择作用于已有变异的差异繁殖成功。",
            "explain_en": "Selection acts via differential reproductive success on existing variation.",
            "chapter": "Unity and Diversity of Life",
        },
    ],
    "chemistry": [
        {
            "id": "chem-11",
            "q_zh": "弱酸 HA 的 pKa=4.8。当 pH=4.8 时，[A⁻]/[HA] 约为：",
            "q_en": "For weak acid HA with pKa=4.8, at pH=4.8 the ratio [A⁻]/[HA] is about:",
            "choices": {
                "A": {"zh": "0.1", "en": "0.1"},
                "B": {"zh": "1", "en": "1"},
                "C": {"zh": "10", "en": "10"},
                "D": {"zh": "100", "en": "100"},
            },
            "answer": "B",
            "explain_zh": "Henderson–Hasselbalch：pH=pKa 时共轭碱与酸浓度比约为 1。",
            "explain_en": "Henderson–Hasselbalch: at pH=pKa the conjugate base/acid ratio is ~1.",
            "chapter": "General Chemistry",
        },
        {
            "id": "chem-12",
            "q_zh": "催化剂如何影响可逆反应？",
            "q_en": "How does a catalyst affect a reversible reaction?",
            "choices": {
                "A": {"zh": "改变平衡常数 K", "en": "Changes equilibrium constant K"},
                "B": {"zh": "加快正逆反应速率，更快达平衡", "en": "Speeds forward and reverse rates, reaching equilibrium sooner"},
                "C": {"zh": "只加快正反应", "en": "Speeds only the forward reaction"},
                "D": {"zh": "提高 ΔG", "en": "Raises ΔG"},
            },
            "answer": "B",
            "explain_zh": "催化剂同等影响正逆路径，不改平衡组成。",
            "explain_en": "Catalysts affect both directions equally and do not change equilibrium composition.",
            "chapter": "5E · Chemical thermodynamics and kinetics",
        },
    ],
    "physics": [
        {
            "id": "phy-11",
            "q_zh": "理想流体中，管道变窄处流速如何变化？",
            "q_en": "In ideal flow, what happens to speed where a pipe narrows?",
            "choices": {
                "A": {"zh": "减小", "en": "Decreases"},
                "B": {"zh": "增大", "en": "Increases"},
                "C": {"zh": "不变", "en": "Stays the same"},
                "D": {"zh": "变为零", "en": "Becomes zero"},
            },
            "answer": "B",
            "explain_zh": "连续性：A₁v₁=A₂v₂，截面积减小则速度增大。",
            "explain_en": "Continuity: A₁v₁=A₂v₂; smaller area means higher speed.",
            "chapter": "Fluids",
        },
        {
            "id": "phy-12",
            "q_zh": "电容两端电压加倍、电容不变，储存电荷：",
            "q_en": "If voltage across a capacitor doubles at fixed C, stored charge:",
            "choices": {
                "A": {"zh": "减半", "en": "Halves"},
                "B": {"zh": "不变", "en": "Unchanged"},
                "C": {"zh": "加倍", "en": "Doubles"},
                "D": {"zh": "变为四倍", "en": "Quadruples"},
            },
            "answer": "C",
            "explain_zh": "Q=CV，C 不变则 Q 与 V 成正比。",
            "explain_en": "Q=CV; at fixed C, Q scales with V.",
            "chapter": "Electricity and Magnetism",
        },
    ],
    "biochemistry": [
        {
            "id": "bch-8",
            "q_zh": "竞争性抑制典型地使：",
            "q_en": "Competitive inhibition typically:",
            "choices": {
                "A": {"zh": "Km 升高，Vmax 不变", "en": "Raises Km, leaves Vmax unchanged"},
                "B": {"zh": "Km 降低，Vmax 升高", "en": "Lowers Km and raises Vmax"},
                "C": {"zh": "Km 与 Vmax 都降低", "en": "Lowers both Km and Vmax"},
                "D": {"zh": "Km 不变，Vmax 升高", "en": "Leaves Km unchanged and raises Vmax"},
            },
            "answer": "A",
            "explain_zh": "竞争抑制剂与底物争活性位点，可用更多底物克服（Vmax 可达）。",
            "explain_en": "Competitor fights for the active site; more substrate can still reach Vmax.",
            "chapter": "Enzymes and regulation",
        },
        {
            "id": "bch-9",
            "q_zh": "糖酵解净产 ATP（每葡萄糖）约为：",
            "q_en": "Net ATP from glycolysis per glucose is about:",
            "choices": {
                "A": {"zh": "0", "en": "0"},
                "B": {"zh": "2", "en": "2"},
                "C": {"zh": "32", "en": "32"},
                "D": {"zh": "36–38", "en": "36–38"},
            },
            "answer": "B",
            "explain_zh": "消耗 2、产生 4，净 2 ATP（另有 NADH）。",
            "explain_en": "Uses 2 and makes 4 → net 2 ATP (plus NADH).",
            "chapter": "Metabolism and bioenergetics",
        },
    ],
    "verbal": [
        {
            "id": "ver-7",
            "q_zh": "类比：医生 : 医院 :: 教师 : ?",
            "q_en": "Analogy: doctor : hospital :: teacher : ?",
            "choices": {
                "A": {"zh": "课本", "en": "textbook"},
                "B": {"zh": "学校", "en": "school"},
                "C": {"zh": "学生", "en": "student"},
                "D": {"zh": "粉笔", "en": "chalk"},
            },
            "answer": "B",
            "explain_zh": "职业与主要工作场所的关系。",
            "explain_en": "Profession mapped to primary workplace.",
            "chapter": "Word Analogies / Vocabulary",
        },
        {
            "id": "ver-8",
            "q_zh": "阅读主旨题最应优先寻找：",
            "q_en": "Main-idea reading items should prioritize finding:",
            "choices": {
                "A": {"zh": "最生动的例子", "en": "The most vivid example"},
                "B": {"zh": "作者核心主张", "en": "The author’s central claim"},
                "C": {"zh": "生僻词定义", "en": "Definitions of rare words"},
                "D": {"zh": "作者家乡", "en": "The author’s hometown"},
            },
            "answer": "B",
            "explain_zh": "主旨是作者要证明/传达的核心主张，不是细节例子。",
            "explain_en": "Main idea is the author’s central claim, not a detail or example.",
            "chapter": "Reading Comprehension / Verbal Ability",
        },
    ],
    "inductive-reasoning": [
        {
            "id": "ind-5",
            "q_zh": "图形归类时，最可靠的策略是：",
            "q_en": "In figure grouping, the most reliable strategy is to:",
            "choices": {
                "A": {"zh": "选自己觉得最美的一组", "en": "Pick the group that looks nicest"},
                "B": {"zh": "找一致规则并检验所有选项", "en": "Find a consistent rule and test all options"},
                "C": {"zh": "随机猜测", "en": "Guess randomly"},
                "D": {"zh": "只看颜色忽略形状", "en": "Ignore shape and use color only"},
            },
            "answer": "B",
            "explain_zh": "归纳推理考规则一致性，不是审美偏好。",
            "explain_en": "Inductive items test rule consistency, not aesthetic preference.",
            "chapter": "Figure Grouping（图形归类）",
        },
    ],
    "quantitative": [
        {
            "id": "quan-5",
            "q_zh": "一组数 2, 3, 3, 100 的中位数是：",
            "q_en": "For 2, 3, 3, 100 the median is:",
            "choices": {
                "A": {"zh": "2", "en": "2"},
                "B": {"zh": "3", "en": "3"},
                "C": {"zh": "27", "en": "27"},
                "D": {"zh": "100", "en": "100"},
            },
            "answer": "B",
            "explain_zh": "偶数个数据取中间两数平均：(3+3)/2=3。",
            "explain_en": "Even count: average the two middle values (3+3)/2=3.",
            "chapter": "Probability and Basic Statistics",
        },
        {
            "id": "quan-6",
            "q_zh": "若 x/3 = 12/9，则 x =",
            "q_en": "If x/3 = 12/9, then x =",
            "choices": {
                "A": {"zh": "3", "en": "3"},
                "B": {"zh": "4", "en": "4"},
                "C": {"zh": "9", "en": "9"},
                "D": {"zh": "36", "en": "36"},
            },
            "answer": "B",
            "explain_zh": "交叉相乘：9x=36 → x=4。",
            "explain_en": "Cross-multiply: 9x=36 → x=4.",
            "chapter": "Arithmetic and Number Sense",
        },
    ],
    "perceptual-acuity": [
        {
            "id": "per-5",
            "q_zh": "镜像题中，竖直轴镜像主要改变：",
            "q_en": "In mirror items, a vertical-axis reflection mainly changes:",
            "choices": {
                "A": {"zh": "上下位置", "en": "Up–down positions"},
                "B": {"zh": "左右位置", "en": "Left–right positions"},
                "C": {"zh": "颜色", "en": "Color"},
                "D": {"zh": "边数", "en": "Number of sides"},
            },
            "answer": "B",
            "explain_zh": "竖直轴镜像左右对调；水平轴才上下对调。",
            "explain_en": "Vertical-axis mirrors swap left–right; horizontal mirrors swap up–down.",
            "chapter": "Mirror Image（镜像）",
        },
    ],
    "cars": [
        {
            "id": "cars-8",
            "q_zh": "CARS “削弱论点”题应优先攻击：",
            "q_en": "CARS weaken questions should preferentially attack:",
            "choices": {
                "A": {"zh": "作者家乡背景", "en": "The author’s hometown"},
                "B": {"zh": "论证关键假设或证据链", "en": "A key assumption or evidence link"},
                "C": {"zh": "字体大小", "en": "Font size"},
                "D": {"zh": "段落数量", "en": "Paragraph count"},
            },
            "answer": "B",
            "explain_zh": "削弱针对推理结构，而非无关作者信息。",
            "explain_en": "Weaken targets the reasoning structure, not irrelevant author trivia.",
            "chapter": "Reasoning Beyond the Text",
        },
        {
            "id": "cars-9",
            "q_zh": "文内推理题的答案必须：",
            "q_en": "Within-the-text reasoning answers must:",
            "choices": {
                "A": {"zh": "依赖课外专业知识", "en": "Rely on outside specialist knowledge"},
                "B": {"zh": "被篇章证据支持", "en": "Be supported by passage evidence"},
                "C": {"zh": "与作者相反才对", "en": "Always contradict the author"},
                "D": {"zh": "越长越好", "en": "Be as long as possible"},
            },
            "answer": "B",
            "explain_zh": "Within the Text 强调文本证据定位。",
            "explain_en": "Within the Text emphasizes locating textual support.",
            "chapter": "Reasoning Within the Text",
        },
    ],
    "chem-phys": [
        {
            "id": "cp-8",
            "q_zh": "光电效应中，增大光强（频率高于阈值）主要增加：",
            "q_en": "In the photoelectric effect, raising intensity (above threshold frequency) mainly increases:",
            "choices": {
                "A": {"zh": "每个电子最大动能", "en": "Max KE per electron"},
                "B": {"zh": "单位时间发射电子数", "en": "Number of electrons emitted per time"},
                "C": {"zh": "功函数", "en": "Work function"},
                "D": {"zh": "阈值频率", "en": "Threshold frequency"},
            },
            "answer": "B",
            "explain_zh": "强度影响光子数→光电流；频率影响最大动能。",
            "explain_en": "Intensity sets photon count → photocurrent; frequency sets max KE.",
            "chapter": "4E · Atoms, nuclear decay, electronic structure",
        },
    ],
    "bio-biochem": [
        {
            "id": "bb-8",
            "q_zh": "氧化磷酸化直接依赖：",
            "q_en": "Oxidative phosphorylation directly depends on:",
            "choices": {
                "A": {"zh": "高尔基体囊泡运输", "en": "Golgi vesicle traffic"},
                "B": {"zh": "线粒体内膜质子梯度驱动 ATP 合酶", "en": "Inner-membrane proton gradient driving ATP synthase"},
                "C": {"zh": "细胞核转录", "en": "Nuclear transcription"},
                "D": {"zh": "细胞骨架收缩", "en": "Cytoskeletal contraction"},
            },
            "answer": "B",
            "explain_zh": "ETC 泵出质子，ATP 合酶利用回流合成 ATP。",
            "explain_en": "ETC pumps protons; ATP synthase uses the return flow to make ATP.",
            "chapter": "1D · Bioenergetics and fuel metabolism",
        },
    ],
    "psych-soc": [
        {
            "id": "ps-10",
            "q_zh": "经典条件反射中，铃声在食物配对后单独引发唾液，铃声是：",
            "q_en": "After pairing a bell with food, the bell alone elicits salivation. The bell is the:",
            "choices": {
                "A": {"zh": "无条件刺激", "en": "Unconditioned stimulus"},
                "B": {"zh": "条件刺激", "en": "Conditioned stimulus"},
                "C": {"zh": "无条件反应", "en": "Unconditioned response"},
                "D": {"zh": "强化物消退", "en": "Extinguished reinforcer"},
            },
            "answer": "B",
            "explain_zh": "原中性刺激经配对成为条件刺激（CS）。",
            "explain_en": "The once-neutral cue becomes the conditioned stimulus (CS).",
            "chapter": "6B · Making sense of the environment",
        },
        {
            "id": "ps-11",
            "q_zh": "社会经济地位（SES）通常不包括：",
            "q_en": "Socioeconomic status (SES) usually does NOT include:",
            "choices": {
                "A": {"zh": "收入", "en": "Income"},
                "B": {"zh": "教育", "en": "Education"},
                "C": {"zh": "职业", "en": "Occupation"},
                "D": {"zh": "血型", "en": "Blood type"},
            },
            "answer": "D",
            "explain_zh": "SES 综合收入、教育、职业等社会地位指标。",
            "explain_en": "SES composites income, education, occupation — not blood type.",
            "chapter": "10A · Social inequality",
        },
    ],
    "behavioral-social": [
        {
            "id": "beh-9",
            "q_zh": "社会促进通常表现为：",
            "q_en": "Social facilitation typically means:",
            "choices": {
                "A": {"zh": "他人在场提高简单/熟练任务表现", "en": "Others’ presence improves simple/well-learned performance"},
                "B": {"zh": "他人在场总是降低所有任务表现", "en": "Others’ presence always worsens all performance"},
                "C": {"zh": "完全无社会影响", "en": "No social influence at all"},
                "D": {"zh": "只发生在网络环境", "en": "Occurs only online"},
            },
            "answer": "A",
            "explain_zh": "简单任务易被唤醒促进；复杂新任务可能受损（抑制）。",
            "explain_en": "Arousal helps simple tasks; complex novel tasks may suffer.",
            "chapter": "FC9 · Cultural and social differences",
        },
    ],
}


PACK_GLOSSARY: list[dict] = [
    {"term": "Henderson–Hasselbalch", "term_zh": "亨德森–哈塞尔巴尔赫方程", "def_zh": "pH = pKa + log([A⁻]/[HA])，描述缓冲体系。", "def_en": "pH = pKa + log([A⁻]/[HA]) for buffer systems.", "subjects": ["chemistry", "chem-phys", "biochemistry"]},
    {"term": "Le Chatelier's principle", "term_zh": "勒夏特列原理", "def_zh": "平衡体系受扰动时向减弱扰动的方向移动。", "def_en": "Equilibria shift to counteract applied disturbances.", "subjects": ["chemistry", "chem-phys"]},
    {"term": "Raoult's law", "term_zh": "拉乌尔定律", "def_zh": "理想溶液组分蒸气压正比于其摩尔分数。", "def_en": "Ideal-solution component vapor pressure proportional to mole fraction.", "subjects": ["chemistry", "chem-phys"]},
    {"term": "Nernst equation", "term_zh": "能斯特方程", "def_zh": "电极电位随离子浓度/反应商变化。", "def_en": "Electrode potential changes with ion concentrations/reaction quotient.", "subjects": ["chemistry", "chem-phys", "physics"]},
    {"term": "Continuity equation", "term_zh": "连续性方程", "def_zh": "不可压缩流体 A₁v₁ = A₂v₂。", "def_en": "Incompressible flow: A₁v₁ = A₂v₂.", "subjects": ["physics", "chem-phys"]},
    {"term": "Coulomb's law", "term_zh": "库仑定律", "def_zh": "点电荷作用力 F ∝ q₁q₂/r²。", "def_en": "Point-charge force F ∝ q₁q₂/r².", "subjects": ["physics", "chem-phys"]},
    {"term": "Refraction", "term_zh": "折射", "def_zh": "波进入另一介质时因波速变化而偏折。", "def_en": "Wave bending when speed changes across media.", "subjects": ["physics", "chem-phys"]},
    {"term": "Diffraction", "term_zh": "衍射", "def_zh": "波绕过障碍或通过狭缝后的扩展。", "def_en": "Wave spreading past obstacles or through apertures.", "subjects": ["physics", "chem-phys"]},
    {"term": "Work function", "term_zh": "功函数", "def_zh": "使电子脱离金属表面所需最小能量。", "def_en": "Minimum energy to free an electron from a metal surface.", "subjects": ["physics", "chem-phys"]},
    {"term": "Allosteric regulation", "term_zh": "别构调节", "def_zh": "效应物结合非活性位点改变酶活性。", "def_en": "Effector binding away from the active site alters enzyme activity.", "subjects": ["biochemistry", "bio-biochem"]},
    {"term": "Competitive inhibition", "term_zh": "竞争性抑制", "def_zh": "抑制剂与底物竞争活性位点；Km↑，Vmax 不变。", "def_en": "Inhibitor competes for active site; Km↑, Vmax unchanged.", "subjects": ["biochemistry", "bio-biochem"]},
    {"term": "Noncompetitive inhibition", "term_zh": "非竞争性抑制", "def_zh": "抑制剂结合其他位点；Vmax↓，Km 常不变。", "def_en": "Inhibitor binds elsewhere; Vmax↓, Km often unchanged.", "subjects": ["biochemistry", "bio-biochem"]},
    {"term": "Gluconeogenesis", "term_zh": "糖异生", "def_zh": "非糖前体合成葡萄糖，主要在肝。", "def_en": "Glucose synthesis from noncarbohydrate precursors, mainly in liver.", "subjects": ["biochemistry", "bio-biochem"]},
    {"term": "Beta oxidation", "term_zh": "β 氧化", "def_zh": "脂肪酸在线粒体降解为乙酰 CoA。", "def_en": "Mitochondrial fatty-acid breakdown to acetyl-CoA.", "subjects": ["biochemistry", "bio-biochem"]},
    {"term": "Transcription factor", "term_zh": "转录因子", "def_zh": "结合 DNA 调控转录的蛋白质。", "def_en": "Protein that binds DNA to regulate transcription.", "subjects": ["biology", "bio-biochem"]},
    {"term": "Operant extinction", "term_zh": "操作性消退", "def_zh": "停止强化后反应频率下降。", "def_en": "Response rate falls when reinforcement stops.", "subjects": ["behavioral-social", "psych-soc"]},
    {"term": "Fundamental attribution error", "term_zh": "基本归因错误", "def_zh": "高估特质、低估情境对他人行为的影响。", "def_en": "Overweight traits and underweight situations for others’ behavior.", "subjects": ["behavioral-social", "psych-soc"]},
    {"term": "Groupthink", "term_zh": "群体思维", "def_zh": "追求一致压制异议，损害决策质量。", "def_en": "Pressure for consensus suppresses dissent and harms decisions.", "subjects": ["behavioral-social", "psych-soc"]},
    {"term": "Social loafing", "term_zh": "社会懈怠", "def_zh": "群体作业中个人努力下降。", "def_en": "Reduced individual effort in group tasks.", "subjects": ["behavioral-social", "psych-soc"]},
    {"term": "Confirmation bias", "term_zh": "确认偏误", "def_zh": "偏好寻找支持已有信念的证据。", "def_en": "Preferentially seeking evidence that supports existing beliefs.", "subjects": ["psych-soc", "cars"]},
    {"term": "Working memory", "term_zh": "工作记忆", "def_zh": "短暂保存并操作信息的有限容量系统。", "def_en": "Limited-capacity system for briefly holding and manipulating information.", "subjects": ["psych-soc", "behavioral-social"]},
    {"term": "Semantic memory", "term_zh": "语义记忆", "def_zh": "关于事实与概念的长时记忆。", "def_en": "Long-term memory for facts and concepts.", "subjects": ["psych-soc"]},
    {"term": "Episodic memory", "term_zh": "情景记忆", "def_zh": "关于个人经历事件的长时记忆。", "def_en": "Long-term memory for personally experienced events.", "subjects": ["psych-soc"]},
    {"term": "Incidence", "term_zh": "发病率", "def_zh": "特定时期内新发病例数。", "def_en": "Number of new cases in a defined period.", "subjects": ["behavioral-social", "psych-soc"]},
    {"term": "Prevalence", "term_zh": "患病率", "def_zh": "特定时点存在的病例总数（新旧合计）。", "def_en": "Total existing cases (new + old) at a time point.", "subjects": ["behavioral-social", "psych-soc"]},
    {"term": "Independent assortment", "term_zh": "自由组合", "def_zh": "不同基因座等位基因在减数分裂中独立分配。", "def_en": "Alleles at different loci segregate independently in meiosis.", "subjects": ["biology", "bio-biochem"]},
    {"term": "Crossing over", "term_zh": "交叉互换", "def_zh": "同源染色体非姐妹染色单体交换片段。", "def_en": "Exchange of segments between nonsister chromatids of homologs.", "subjects": ["biology", "bio-biochem"]},
    {"term": "Endosymbiosis", "term_zh": "内共生", "def_zh": "线粒体/叶绿体起源于被吞噬的原核生物假说。", "def_en": "Hypothesis that mitochondria/chloroplasts arose from engulfed prokaryotes.", "subjects": ["biology", "bio-biochem"]},
    {"term": "Action spectrum", "term_zh": "作用光谱", "def_zh": "不同波长光引起生理反应的效率曲线。", "def_en": "Efficiency of physiological response across wavelengths.", "subjects": ["biology", "chem-phys"]},
    {"term": "Titration", "term_zh": "滴定", "def_zh": "用已知浓度试剂测定未知浓度分析物。", "def_en": "Using a known reagent concentration to determine an analyte.", "subjects": ["chemistry", "chem-phys"]},
    {"term": "Equivalence point", "term_zh": "等当点", "def_zh": "滴定中化学计量恰好完全反应的点。", "def_en": "Point where stoichiometrically equivalent amounts have reacted.", "subjects": ["chemistry", "chem-phys"]},
    {"term": "Buffer capacity", "term_zh": "缓冲容量", "def_zh": "缓冲液抵抗 pH 变化的能力，与组分浓度相关。", "def_en": "Ability of a buffer to resist pH change; depends on component amounts.", "subjects": ["chemistry", "biochemistry"]},
    {"term": "Series circuit", "term_zh": "串联电路", "def_zh": "同一电流流经各元件；总阻相加。", "def_en": "Same current through components; resistances add.", "subjects": ["physics", "chem-phys"]},
    {"term": "Parallel circuit", "term_zh": "并联电路", "def_zh": "各支路电压相同；电导相加。", "def_en": "Same voltage across branches; conductances add.", "subjects": ["physics", "chem-phys"]},
    {"term": "Focal length", "term_zh": "焦距", "def_zh": "平行光线经透镜后会聚（或反向延长线会聚）的距离。", "def_en": "Distance where parallel rays meet after a lens (or appear to meet).", "subjects": ["physics", "chem-phys"]},
    {"term": "Impulse", "term_zh": "冲量", "def_zh": "力对时间的积分，等于动量变化。", "def_en": "Integral of force over time; equals change in momentum.", "subjects": ["physics", "chem-phys"]},
    {"term": "Elastic collision", "term_zh": "弹性碰撞", "def_zh": "动量与动能均守恒的碰撞。", "def_en": "Collision conserving both momentum and kinetic energy.", "subjects": ["physics", "chem-phys"]},
    {"term": "Inelastic collision", "term_zh": "非弹性碰撞", "def_zh": "动量守恒但动能不守恒（部分转为其他形式）。", "def_en": "Momentum conserved but kinetic energy not (some converts).", "subjects": ["physics", "chem-phys"]},
    {"term": "Passage map", "term_zh": "篇章地图", "def_zh": "CARS/阅读中快速标注段落功能与作者态度。", "def_en": "Quick CARS/reading annotation of paragraph roles and attitude.", "subjects": ["cars", "verbal"]},
    {"term": "Scope trap", "term_zh": "范围陷阱", "def_zh": "选项过宽/过窄或引入文外内容的干扰。", "def_en": "Distractor that is too broad/narrow or outside the passage.", "subjects": ["cars", "verbal"]},
]


PACK_TIPS: list[dict] = [
    {
        "exam": "NMAT",
        "title_zh": "Part 1 知觉题防疲劳",
        "title_en": "Part 1 perceptual fatigue control",
        "body_zh": "Hidden Figure / Mirror 连续做易眼疲劳。每 8–10 题短暂眨眼休息；先做 Identical Information 热身再进隐藏图形。",
        "body_en": "Hidden Figure / Mirror sets tire the eyes. Blink-rest every 8–10 items; warm up with Identical Information before hidden figures.",
    },
    {
        "exam": "NMAT",
        "title_zh": "Part 2 四科时间盒",
        "title_en": "Part 2 four-subject time boxes",
        "body_zh": "每科约 30 题。建议单科内部也分“必会 / 可猜 / 标记回看”，避免在一道计算卡死整科。",
        "body_en": "About 30 items per subject. Inside each subject, triage must-know / guess / mark-and-return so one calculation doesn’t sink the section.",
    },
    {
        "exam": "MCAT",
        "title_zh": "实验设计题清单",
        "title_en": "Experimental-design checklist",
        "body_zh": "看自变量、因变量、对照组、混淆变量与样本。很多 Chem/Phys、Bio/Biochem 篇章题考的是设计逻辑而非背公式。",
        "body_en": "Track IV, DV, controls, confounders, and sample. Many Chem/Phys and Bio/Biochem items test design logic more than formula recall.",
    },
    {
        "exam": "MCAT",
        "title_zh": "Psych/Soc 术语精确度",
        "title_en": "Psych/Soc term precision",
        "body_zh": "区分经典/操作条件、同化/顺应、发病率/患病率、刻板印象/歧视/偏见。近义词陷阱极多。",
        "body_en": "Distinguish classical/operant, assimilation/accommodation, incidence/prevalence, stereotype/discrimination/prejudice. Near-synonym traps are common.",
    },
    {
        "exam": "BOTH",
        "title_zh": "错题本三问",
        "title_en": "Wrong-item three questions",
        "body_zh": "① 概念缺口还是粗心？② 对应哪条官方章节？③ 能否用一句话教给别人？教不出来就回 Gabay 笔记与闪卡。",
        "body_en": "① Concept gap or carelessness? ② Which official chapter? ③ Can you teach it in one sentence? If not, return to Gabay notes and cards.",
    },
    {
        "exam": "BOTH",
        "title_zh": "公式卡用法",
        "title_en": "How to use formula sheets",
        "body_zh": "公式页是“触发器”不是题库。看到公式先说物理意义与典型陷阱，再去做对应练习集。",
        "body_en": "Formula sheets are triggers, not a question bank. State meaning and traps, then drill the matching practice set.",
    },
    {
        "exam": "BOTH",
        "title_zh": "考前 48 小时",
        "title_en": "Final 48 hours",
        "body_zh": "停开新章节；只复习错题、术语表与高频公式。保证睡眠与通勤路线，比临时抱佛脚更提分。",
        "body_en": "Stop opening new chapters; review misses, glossary, and high-yield formulas. Sleep and logistics beat last-minute cramming.",
    },
]


PACK_PATHS: list[dict] = [
    {
        "id": "exam-week-final",
        "title_zh": "考前一周总复习",
        "title_en": "Final-week review",
        "blurb_zh": "术语表 + 公式卡 + 错题练习 + 策略提示，不再开新大章。",
        "blurb_en": "Glossary + formulas + miss drills + tips — no new major chapters.",
        "steps": [
            {"label_zh": "术语表", "label_en": "Glossary", "href": "/materials/glossary/"},
            {"label_zh": "考试策略", "label_en": "Exam tips", "href": "/materials/tips/"},
            {"label_zh": "清单", "label_en": "Checklists", "href": "/materials/checklists/"},
            {"label_zh": "练习总览", "label_en": "Practice hub", "href": "/practice/"},
        ],
    },
    {
        "id": "daily-loop",
        "title_zh": "每日 90 分钟学习环",
        "title_en": "Daily 90-minute loop",
        "blurb_zh": "30 分钟笔记 → 20 分钟闪卡 → 30 分钟练习 → 10 分钟教练答疑。",
        "blurb_en": "30 min notes → 20 min cards → 30 min drills → 10 min coach.",
        "steps": [
            {"label_zh": "教材资料台", "label_en": "Materials desk", "href": "/materials/"},
            {"label_zh": "生物学笔记", "label_en": "Biology notes", "href": "/subjects/biology/"},
            {"label_zh": "生物练习", "label_en": "Biology practice", "href": "/practice/biology/"},
            {"label_zh": "学习台教练", "label_en": "Study coach", "href": "/study/"},
        ],
    },
]


CHECKLISTS: list[dict] = [
    {
        "id": "nmat-day",
        "exam": "NMAT",
        "title_zh": "NMAT 考试日清单",
        "title_en": "NMAT exam-day checklist",
        "items_zh": [
            "确认准考证与身份证件",
            "提前到达考场，预留安检时间",
            "Part 1 先稳准确再提速；知觉题防眼疲劳",
            "Part 2 四科按时间盒推进，标记难题回看",
            "交卷前快速扫未作答题",
        ],
        "items_en": [
            "Confirm permit and ID",
            "Arrive early; allow security time",
            "Part 1: accuracy before speed; watch eye fatigue on perceptual items",
            "Part 2: time-box each subject; mark hard items to revisit",
            "Final sweep for unanswered items",
        ],
    },
    {
        "id": "mcat-day",
        "exam": "MCAT",
        "title_zh": "MCAT 考试日清单",
        "title_en": "MCAT exam-day checklist",
        "items_zh": [
            "确认 AAMC 预约与身份要求",
            "按官方休息节奏进食补水",
            "科学科：图表与实验设计优先定位",
            "CARS：先段落地图再答题，避免超时纠缠",
            "每科结束用 1–2 分钟检查标记题",
        ],
        "items_en": [
            "Confirm AAMC appointment and ID rules",
            "Eat/hydrate on the official break rhythm",
            "Science: prioritize figures and experimental design",
            "CARS: map paragraphs before answering; don’t over-invest",
            "Use 1–2 minutes at section end for marked items",
        ],
    },
    {
        "id": "weekly-review",
        "exam": "BOTH",
        "title_zh": "每周复习清单",
        "title_en": "Weekly review checklist",
        "items_zh": [
            "本周新笔记 → 闪卡过一遍",
            "错题按科目归档并回看解析",
            "术语表抽 15 个词英汉互译",
            "公式卡说出物理意义 + 一个陷阱",
            "用学习台教练讲清一个卡点",
        ],
        "items_en": [
            "Run flashcards on this week’s new notes",
            "File misses by subject and reread explanations",
            "Quiz 15 glossary terms ZH↔EN",
            "For each formula: meaning + one trap",
            "Use the study coach on one stuck point",
        ],
    },
]


PACK_FORMULAS: dict[str, list[dict[str, str]]] = {
    "verbal": [
        {
            "title_zh": "类比模板",
            "title_en": "Analogy template",
            "formula": "A : B :: C : ?",
            "note_zh": "先写清 A→B 关系，再映射到 C。",
            "note_en": "State A→B relation, then map onto C.",
        },
    ],
    "cars": [
        {
            "title_zh": "篇章地图",
            "title_en": "Passage map",
            "formula": "Claim → Support → Turn → Close",
            "note_zh": "标注主张、证据、转折与收束。",
            "note_en": "Mark claim, support, turn, and close.",
        },
    ],
    "quantitative": [
        {
            "title_zh": "百分变化",
            "title_en": "Percent change",
            "formula": "%Δ = (new−old)/old × 100%",
            "note_zh": "分清相对百分与百分点。",
            "note_en": "Distinguish relative percent from percentage points.",
        },
        {
            "title_zh": "组合（不计序）",
            "title_en": "Combinations",
            "formula": "C(n,k) = n! / (k!(n−k)!)",
            "note_zh": "选组不论顺序；排列用 P(n,k)。",
            "note_en": "Unordered selections; use P(n,k) when order matters.",
        },
    ],
    "inductive-reasoning": [
        {
            "title_zh": "归类检验",
            "title_en": "Grouping check",
            "formula": "Rule → Test all → Exclude near-miss",
            "note_zh": "规则必须覆盖组内全部成员。",
            "note_en": "The rule must cover every in-group member.",
        },
    ],
    "perceptual-acuity": [
        {
            "title_zh": "镜像轴",
            "title_en": "Mirror axis",
            "formula": "vertical ↔ L/R · horizontal ↔ U/D",
            "note_zh": "竖直轴左右对调；水平轴上下对调。",
            "note_en": "Vertical axis swaps L/R; horizontal swaps U/D.",
        },
    ],
}


def merge_note_pack(base: dict) -> dict:
    merged = copy.deepcopy(base)
    for slug, chapters in PACK_NOTES.items():
        merged.setdefault(slug, {})
        for title, notes in chapters.items():
            merged[slug].setdefault(title, [])
            merged[slug][title] = list(merged[slug][title]) + list(notes)
    return merged


def merge_practice_pack(base: dict) -> dict:
    merged = copy.deepcopy(base)
    for slug, items in PACK_PRACTICE.items():
        merged.setdefault(slug, [])
        seen = {i.get("id") for i in merged[slug] if i.get("id")}
        for item in items:
            iid = item.get("id")
            if iid and iid in seen:
                continue
            merged[slug].append(copy.deepcopy(item))
            if iid:
                seen.add(iid)
    return merged


def merge_glossary(base: list) -> list:
    seen = {g["term"].lower() for g in base}
    out = list(base)
    for g in PACK_GLOSSARY:
        if g["term"].lower() in seen:
            continue
        out.append(g)
        seen.add(g["term"].lower())
    return out


def merge_tips(base: list) -> list:
    seen = {(t["exam"], t["title_en"]) for t in base}
    out = list(base)
    for tip in PACK_TIPS:
        key = (tip["exam"], tip["title_en"])
        if key in seen:
            continue
        out.append(tip)
        seen.add(key)
    return out


def merge_paths(base: list) -> list:
    seen = {p["id"] for p in base}
    out = list(base)
    for path in PACK_PATHS:
        if path["id"] in seen:
            continue
        out.append(path)
        seen.add(path["id"])
    return out


def merge_formulas(base: dict) -> dict:
    merged = copy.deepcopy(base)
    for slug, items in PACK_FORMULAS.items():
        merged.setdefault(slug, [])
        seen = {f["formula"] for f in merged[slug]}
        for f in items:
            if f["formula"] in seen:
                continue
            merged[slug].append(copy.deepcopy(f))
            seen.add(f["formula"])
    return merged
