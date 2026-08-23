"""High-yield study notes under official chapter headings.

These deepen Gabay outlines without inventing new exam sections.
Chinese + English pairs for bilingual UI.
"""

from __future__ import annotations

import re

# subject_slug -> chapter_title -> list[{zh,en}]
NOTES: dict[str, dict[str, list[dict[str, str]]]] = {
    "biology": {
        "Unity and Diversity of Life": [
            {"zh": "生命共同特征：细胞、代谢、稳态、繁殖、进化适应", "en": "Shared traits: cells, metabolism, homeostasis, reproduction, adaptation"},
            {"zh": "域/界层级用于组织多样性，不是死记全部物种名", "en": "Domain/kingdom hierarchy organizes diversity — not rote species lists"},
            {"zh": "同源 vs 同功：进化关系 vs 功能相似", "en": "Homology vs analogy: shared ancestry vs similar function"},
        ],
        "Cells and Cellular Processes": [
            {"zh": "原核无膜包细胞核；真核有细胞器分区", "en": "Prokaryotes lack membrane-bound nucleus; eukaryotes have compartmentalization"},
            {"zh": "膜转运：简单扩散、协助扩散、主动转运、胞吞/胞吐", "en": "Transport: simple/facilitated diffusion, active transport, endo/exocytosis"},
            {"zh": "酶：降低活化能；受温度、pH、抑制剂影响", "en": "Enzymes lower activation energy; affected by T, pH, inhibitors"},
            {"zh": "细胞呼吸主线：糖酵解 → 丙酮酸氧化 → TCA → ETC/氧化磷酸化", "en": "Respiration spine: glycolysis → pyruvate oxidation → TCA → ETC/oxphos"},
        ],
        "Genetics": [
            {"zh": "中心法则：DNA → RNA → 蛋白质（及常见例外语境）", "en": "Central dogma: DNA → RNA → protein (plus common caveats)"},
            {"zh": "孟德尔：分离与自由组合；表型/基因型比", "en": "Mendel: segregation & independent assortment; phenotype/genotype ratios"},
            {"zh": "突变类型：点突变、移码、染色体结构/数目异常", "en": "Mutations: point, frameshift, chromosomal structure/number"},
            {"zh": "减数分裂产生单倍体配子并重组遗传多样性", "en": "Meiosis yields haploid gametes and reassorts diversity"},
        ],
        "The World of Plants and Animals": [
            {"zh": "植物：光合作用光反应/暗反应分工；气孔与蒸腾", "en": "Plants: light/dark reactions; stomata and transpiration"},
            {"zh": "动物：交换表面积、循环与气体交换的权衡", "en": "Animals: surface-area tradeoffs for exchange, circulation, gas exchange"},
            {"zh": "比较解剖关注功能约束，不堆术语", "en": "Comparative anatomy emphasizes functional constraints, not jargon piles"},
        ],
        "Development": [
            {"zh": "受精 → 卵裂 → 囊胚 → 原肠胚 → 器官发生（导论级）", "en": "Fertilization → cleavage → blastula → gastrula → organogenesis (intro)"},
            {"zh": "细胞分化：基因选择性表达，而非基因组丢失（多数情况）", "en": "Differentiation: selective gene expression, not genome loss (usually)"},
            {"zh": "诱导与信号决定细胞命运", "en": "Induction and signaling set cell fates"},
        ],
        "Life Processes: Regulation and Homeostasis": [
            {"zh": "负反馈维持稳态；正反馈放大短暂过程", "en": "Negative feedback stabilizes; positive feedback amplifies brief events"},
            {"zh": "内分泌与神经是两大协调系统", "en": "Endocrine and nervous systems are the two major coordinators"},
            {"zh": "体温、血糖、渗透压是经典稳态例子", "en": "Temperature, glucose, and osmolarity are classic homeostasis examples"},
        ],
        "Organisms and Their Environment": [
            {"zh": "种群、群落、生态系统层次", "en": "Population, community, ecosystem levels"},
            {"zh": "能量流单向、物质循环", "en": "Energy flows one way; matter cycles"},
            {"zh": "种间关系：捕食、竞争、共生", "en": "Species interactions: predation, competition, symbiosis"},
        ],
        "1C · Heritable information & genetic diversity": [
            {"zh": "DNA 复制半保守；突变是变异原料", "en": "Semiconservative replication; mutation feeds variation"},
            {"zh": "减数分裂重组 + 独立分配 → 配子多样性", "en": "Meiotic recombination + assortment → gamete diversity"},
            {"zh": "Hardy–Weinberg 条件：无突变/选择/漂变/迁徙且随机交配（理想）", "en": "HWE ideal: no mutation/selection/drift/migration + random mating"},
        ],
        "2A · Assemblies of molecules, cells, and cell groups": [
            {"zh": "从大分子 → 细胞器 → 组织的层级组装", "en": "Hierarchy: macromolecules → organelles → tissues"},
            {"zh": "细胞连接与细胞外基质支持组织功能", "en": "Junctions and ECM support tissue function"},
        ],
        "2B · Prokaryotes and viruses": [
            {"zh": "细菌：细胞壁、质粒、二元分裂", "en": "Bacteria: cell wall, plasmids, binary fission"},
            {"zh": "病毒：需宿主；溶原/裂解周期思想", "en": "Viruses need hosts; lysogeny/lysis idea"},
            {"zh": "抗生素靶点常是原核特有结构（如细胞壁）", "en": "Antibiotics often hit prokaryote-specific targets (e.g., cell wall)"},
        ],
        "2C · Cell division, differentiation, specialization": [
            {"zh": "有丝分裂保染色体数；减数分裂减半", "en": "Mitosis keeps chromosome number; meiosis halves it"},
            {"zh": "细胞周期检查点与癌变失控（导论）", "en": "Checkpoints vs uncontrolled growth (intro)"},
            {"zh": "干细胞：自我更新 + 分化潜能", "en": "Stem cells: self-renewal + differentiation potential"},
        ],
        "3A · Nervous & endocrine coordination": [
            {"zh": "神经：快、局部；内分泌：慢、广泛", "en": "Neural: fast/local; endocrine: slower/broad"},
            {"zh": "动作电位：去极化→复极化；突触化学传递", "en": "AP: depol→repol; chemical synaptic transmission"},
            {"zh": "激素：肽类/类固醇信号路径不同", "en": "Peptide vs steroid hormone signaling differs"},
        ],
        "3B · Main organ systems": [
            {"zh": "交换界面：肺泡、小肠绒毛、肾单位", "en": "Exchange surfaces: alveoli, villi, nephrons"},
            {"zh": "循环：心输出、血压与阻力关系直觉", "en": "Circulation: cardiac output, pressure, resistance intuition"},
            {"zh": "每个系统问：输入、处理、输出、稳态回路", "en": "Per system ask: input, processing, output, feedback loop"},
        ],
    },
    "chemistry": {
        "General Chemistry": [
            {"zh": "摩尔、限量反应物、产率", "en": "Mole, limiting reagent, yield"},
            {"zh": "酸碱：pH、缓冲、滴定曲线直觉", "en": "Acids/bases: pH, buffers, titration-curve intuition"},
            {"zh": "平衡：Le Chatelier；K 与 Q", "en": "Equilibrium: Le Chatelier; K vs Q"},
            {"zh": "氧化还原：氧化数、半反应", "en": "Redox: oxidation numbers, half-reactions"},
        ],
        "Analytical Chemistry": [
            {"zh": "准确度 vs 精密度", "en": "Accuracy vs precision"},
            {"zh": "滴定、分光、色谱的“测什么/怎么分开”", "en": "Titration/spectroscopy/chromatography: what is measured vs separated"},
            {"zh": "校准曲线与空白对照思想", "en": "Calibration curves and blank controls"},
        ],
        "Organic Chemistry": [
            {"zh": "官能团决定反应性（醇、羰基、羧酸、胺）", "en": "Functional groups drive reactivity (alcohol, carbonyl, acid, amine)"},
            {"zh": "亲核/亲电、酸碱性影响反应路径", "en": "Nucleophile/electrophile and acid-base character shape pathways"},
            {"zh": "异构：结构异构与立体异构（导论）", "en": "Isomerism: structural and stereo (intro)"},
        ],
        "Biochemistry": [
            {"zh": "氨基酸侧链极性/电荷决定蛋白质折叠与功能", "en": "Side-chain polarity/charge shape folding and function"},
            {"zh": "酶动力学：Vmax、Km 的直觉含义", "en": "Enzyme kinetics: intuitive Vmax and Km"},
            {"zh": "代谢枢纽：葡萄糖、乙酰 CoA、ATP/NADH", "en": "Metabolic hubs: glucose, acetyl-CoA, ATP/NADH"},
        ],
        "5A · Water and its solutions": [
            {"zh": "水的氢键解释高比热与溶解能力", "en": "H-bonding explains heat capacity and solvent power"},
            {"zh": "亲水/疏水驱动折叠与胶束", "en": "Hydrophilic/hydrophobic drive folding and micelles"},
            {"zh": "pH、pKa 与电离分数", "en": "pH, pKa, and ionization fractions"},
        ],
        "5B · Molecules and intermolecular interactions": [
            {"zh": "离子键、氢键、范德华、疏水效应强度层级直觉", "en": "Ion, H-bond, van der Waals, hydrophobic hierarchy"},
            {"zh": "极性决定溶解度与沸点趋势", "en": "Polarity shapes solubility and boiling trends"},
        ],
        "5C · Separation and purification methods": [
            {"zh": "萃取：分配系数思想", "en": "Extraction: partition-coefficient idea"},
            {"zh": "色谱：极性/大小/电荷分离原理", "en": "Chromatography: polarity/size/charge separation"},
            {"zh": "蒸馏与重结晶适用场景", "en": "When distillation vs recrystallization fit"},
        ],
        "5D · Biologically relevant molecules": [
            {"zh": "官能团在水中的酸碱/氢键行为", "en": "Acid-base/H-bonding of groups in water"},
            {"zh": "肽键形成/水解；糖苷键", "en": "Peptide bond formation/hydrolysis; glycosidic bonds"},
            {"zh": "脂质：两亲性与膜双层", "en": "Lipids: amphiphilicity and bilayers"},
        ],
        "5E · Chemical thermodynamics and kinetics": [
            {"zh": "ΔG 决定自发；动力学决定快慢", "en": "ΔG = spontaneity; kinetics = rate"},
            {"zh": "酶/催化剂改路径不改 ΔG", "en": "Catalysts change path, not ΔG"},
            {"zh": "反应级数与速率定律读法", "en": "How to read rate laws and reaction order"},
        ],
        "4E · Atoms, nuclear decay, electronic structure": [
            {"zh": "电子构型与周期性趋势（半径、电负性）", "en": "Configs and periodic trends (radius, electronegativity)"},
            {"zh": "衰变类型与半衰期指数直觉", "en": "Decay modes and half-life exponential intuition"},
        ],
    },
    "physics": {
        "Mechanics": [
            {"zh": "牛顿定律与自由体图", "en": "Newton’s laws and free-body diagrams"},
            {"zh": "功-能定理；机械能守恒条件", "en": "Work–energy theorem; when mechanical energy is conserved"},
            {"zh": "动量守恒：碰撞与冲量", "en": "Momentum conservation: collisions and impulse"},
        ],
        "Thermodynamics": [
            {"zh": "温度、内能、热量区分", "en": "Distinguish temperature, internal energy, heat"},
            {"zh": "第一定律：ΔU = Q − W（注意符号约定）", "en": "First law: ΔU = Q − W (watch sign convention)"},
            {"zh": "熵与不可逆过程直觉", "en": "Entropy intuition and irreversible processes"},
        ],
        "Vibrations, Waves, and Optics": [
            {"zh": "简谐运动：周期与能量交换", "en": "SHM: period and energy exchange"},
            {"zh": "波速 v = fλ；干涉与衍射条件", "en": "Wave speed v = fλ; interference/diffraction conditions"},
            {"zh": "反射/折射；透镜成像符号约定要统一", "en": "Reflection/refraction; keep lens-sign conventions consistent"},
        ],
        "Electricity and Magnetism": [
            {"zh": "库仑力与电场；电势差与功", "en": "Coulomb force/fields; potential difference and work"},
            {"zh": "欧姆定律、串并联、电路功率", "en": "Ohm’s law, series/parallel, power in circuits"},
            {"zh": "磁场对运动电荷的力（洛伦兹力直觉）", "en": "Magnetic force on moving charges (Lorentz intuition)"},
        ],
        "Modern Physics": [
            {"zh": "光子能量 E = hf；光电效应要点", "en": "Photon energy E = hf; photoelectric highlights"},
            {"zh": "能级与光谱线", "en": "Energy levels and spectral lines"},
            {"zh": "核衰变：半衰期与守恒量", "en": "Nuclear decay: half-life and conserved quantities"},
        ],
        "4A · Motion, forces, work, energy, equilibrium": [
            {"zh": "把生理情境翻译成受力/能量问题", "en": "Translate physio scenarios into force/energy problems"},
            {"zh": "静力平衡：合力与合力矩为零", "en": "Static equilibrium: net force and torque zero"},
            {"zh": "功与功率在肌肉/循环题中常见", "en": "Work and power show up in muscle/circulation items"},
        ],
        "4B · Fluids, circulation, gas exchange": [
            {"zh": "连续性方程 A₁v₁ = A₂v₂", "en": "Continuity: A₁v₁ = A₂v₂"},
            {"zh": "伯努利：速度↑ 压力↓（理想流体直觉）", "en": "Bernoulli: speed up → pressure down (ideal intuition)"},
            {"zh": "Poiseuille：流量对半径极度敏感", "en": "Poiseuille: flow extremely sensitive to radius"},
        ],
        "4C · Electrochemistry and circuits": [
            {"zh": "电池：氧化还原与电子流向", "en": "Cells: redox and electron flow"},
            {"zh": "串并联电阻与等效电路", "en": "Series/parallel resistance and equivalents"},
            {"zh": "电容充放电与时间常数思想", "en": "Capacitor charge/discharge and time-constant idea"},
        ],
        "4D · Light and sound with matter": [
            {"zh": "声波：强度、衰减、多普勒", "en": "Sound: intensity, attenuation, Doppler"},
            {"zh": "光：折射指数、全反射、透镜成像", "en": "Light: index, TIR, lens imaging"},
            {"zh": "超声/光学在诊断中的物理约束（导论）", "en": "Physical limits of ultrasound/optics in diagnosis (intro)"},
        ],
        "4E · Atoms and electronic structure": [
            {"zh": "能级跃迁与吸收/发射光谱", "en": "Level transitions and absorption/emission spectra"},
            {"zh": "光电效应：阈值阈值与动能", "en": "Photoelectric: frequency threshold and KE"},
        ],
    },
    "behavioral-social": {
        "Psychology": [
            {"zh": "感觉 vs 知觉；自上而下/自下而上加工", "en": "Sensation vs perception; top-down/bottom-up processing"},
            {"zh": "学习：经典/操作条件反射；强化与惩罚", "en": "Learning: classical/operant conditioning; reinforcement vs punishment"},
            {"zh": "记忆：编码、储存、提取；工作记忆限制", "en": "Memory: encoding, storage, retrieval; working-memory limits"},
            {"zh": "情绪与应激：交感/副交感与应对", "en": "Emotion/stress: sympathetic/parasympathetic and coping"},
        ],
        "Sociology and Anthropology": [
            {"zh": "社会化、规范、角色、地位", "en": "Socialization, norms, roles, status"},
            {"zh": "文化：物质/非物质；文化相对 vs 民族中心", "en": "Culture: material/nonmaterial; relativism vs ethnocentrism"},
            {"zh": "分层、不平等与健康差异（导论）", "en": "Stratification, inequality, and health disparities (intro)"},
            {"zh": "人类学视角：比较文化与人类共性", "en": "Anthropological lens: compare cultures and human commonalities"},
        ],
        "FC6 · Perceive, think, react": [
            {"zh": "阈值、信号检测、注意选择性", "en": "Thresholds, signal detection, selective attention"},
            {"zh": "认知偏差影响判断（启发式）", "en": "Biases and heuristics shape judgment"},
        ],
        "FC7 · Behavior and behavior change": [
            {"zh": "态度—行为差距；认知失调", "en": "Attitude–behavior gap; cognitive dissonance"},
            {"zh": "说服：中心路径 vs 外周路径", "en": "Persuasion: central vs peripheral routes"},
            {"zh": "习惯化与敏感化", "en": "Habituation vs sensitization"},
        ],
        "FC8 · Self, others, interactions": [
            {"zh": "自我概念、自尊、社会认同", "en": "Self-concept, self-esteem, social identity"},
            {"zh": "归因：内因/外因；基本归因错误", "en": "Attribution: internal/external; fundamental attribution error"},
            {"zh": "从众、服从、群体极化", "en": "Conformity, obedience, group polarization"},
        ],
        "FC9 · Cultural and social differences": [
            {"zh": "文化规范塑造行为期望", "en": "Cultural norms shape behavioral expectations"},
            {"zh": "偏见、刻板印象、歧视区分", "en": "Distinguish prejudice, stereotype, discrimination"},
        ],
        "FC10 · Stratification and resources": [
            {"zh": "SES 与健康结果相关", "en": "SES correlates with health outcomes"},
            {"zh": "文化资本与社会资本", "en": "Cultural and social capital"},
            {"zh": "医疗可及性受结构因素影响", "en": "Access to care is structurally constrained"},
        ],
    },
    "biochemistry": {
        "Chemistry · Biochemistry（CEM）": [
            {"zh": "NMAT Chemistry 内的生化块：氨基酸、酶、代谢枢纽", "en": "NMAT Chemistry biochem block: amino acids, enzymes, metabolic hubs"},
            {"zh": "与 MCAT Bio/Biochem FC1 重叠，可共用复习", "en": "Overlaps MCAT Bio/Biochem FC1 — shared review works"},
        ],
        "1A · Proteins and amino acids": [
            {"zh": "20 种常见氨基酸：非极性/极性/酸碱侧链", "en": "20 common amino acids: nonpolar/polar/acidic/basic sides"},
            {"zh": "一级→四级结构；变性破坏高级结构", "en": "Primary→quaternary structure; denaturation hits higher order"},
            {"zh": "酶：活性部位、辅因子、别构调节", "en": "Enzymes: active site, cofactors, allosteric regulation"},
        ],
        "1B · Gene to protein": [
            {"zh": "转录与 RNA 加工（真核）", "en": "Transcription and eukaryotic RNA processing"},
            {"zh": "遗传密码简并；起止密码子", "en": "Degenerate code; start/stop codons"},
            {"zh": "翻译：核糖体、tRNA、多肽延伸", "en": "Translation: ribosome, tRNA, peptide elongation"},
        ],
        "1C · Heritable information & diversity": [
            {"zh": "DNA 复制半保守；校对与修复", "en": "Semiconservative replication; proofreading/repair"},
            {"zh": "减数分裂重组与独立分配", "en": "Meiotic recombination and independent assortment"},
            {"zh": "突变与选择/漂变改变等位基因频率（导论）", "en": "Mutation plus selection/drift change allele frequencies (intro)"},
        ],
        "1D · Bioenergetics and fuel metabolism": [
            {"zh": "ATP 作为能量货币；偶联反应", "en": "ATP as energy currency; coupled reactions"},
            {"zh": "糖酵解/糖异生对照；糖原调节", "en": "Glycolysis vs gluconeogenesis; glycogen regulation"},
            {"zh": "脂肪酸氧化与酮体（导论）", "en": "Fatty-acid oxidation and ketone bodies (intro)"},
            {"zh": "氧化磷酸化：质子梯度驱动 ATP 合成", "en": "OxPhos: proton gradient drives ATP synthesis"},
        ],
    },
    "verbal": {
        "Analogies（词义类比）": [
            {"zh": "先用一句话定义词对关系，再套到选项", "en": "State the pair relation in one sentence, then test options"},
            {"zh": "警惕同题材但关系不同的干扰项", "en": "Watch same-topic distractors with different relations"},
            {"zh": "程度/因果/部分-整体是高频关系", "en": "Degree, cause-effect, and part-whole are high-frequency"},
        ],
        "Reading Comprehension（阅读理解）": [
            {"zh": "先抓主旨句与转折词", "en": "Hunt thesis sentences and contrast markers first"},
            {"zh": "细节题回文定位，避免凭印象", "en": "Detail items: relocate in text; don’t rely on memory"},
            {"zh": "推断必须被文本支持", "en": "Inferences must be text-supported"},
        ],
    },
    "inductive-reasoning": {
        "Figure Series（图形序列）": [
            {"zh": "分别跟踪位置、数量、填充、旋转四条线索", "en": "Track position, count, fill, and rotation as separate threads"},
            {"zh": "可能多规则叠加，先找最稳定的变化", "en": "Multiple rules may stack — find the steadiest change first"},
        ],
        "Figure Grouping（图形归类）": [
            {"zh": "找共同点或唯一例外", "en": "Find the shared trait or the odd one out"},
            {"zh": "先忽略装饰，抓拓扑/数量结构", "en": "Ignore decoration; grab topology/count structure"},
        ],
        "Number and Letter Series（数字与字母序列）": [
            {"zh": "检查等差、倍比、交替、位值", "en": "Check arithmetic, multiplicative, alternating, place-value rules"},
            {"zh": "字母常映射到位置序号", "en": "Letters often map to alphabet indices"},
        ],
    },
    "quantitative": {
        "Fundamental Operations（基本运算）": [
            {"zh": "分数/百分数互换要熟练", "en": "Be fluent converting fractions ↔ percents"},
            {"zh": "估算可排除离谱选项", "en": "Estimation kills absurd options"},
        ],
        "Problem Solving（应用题）": [
            {"zh": "先定义未知数与单位", "en": "Define unknowns and units first"},
            {"zh": "画关系再计算", "en": "Sketch the relation before computing"},
        ],
        "Data Interpretation（资料判读）": [
            {"zh": "先读轴、图例、单位", "en": "Read axes, legend, units first"},
            {"zh": "问的是差值、比例还是趋势", "en": "Ask: difference, ratio, or trend?"},
        ],
    },
    "perceptual-acuity": {
        "Hidden Figure（隐藏图形）": [
            {"zh": "盯轮廓而非填充", "en": "Track outline, not fill"},
            {"zh": "分段匹配比整体硬找更快", "en": "Match in segments faster than whole-figure search"},
        ],
        "Mirror Image（镜像）": [
            {"zh": "左右镜像 ≠ 旋转", "en": "Left-right mirror ≠ rotation"},
            {"zh": "对不对称特征做快速检查", "en": "Spot-check asymmetric features quickly"},
        ],
        "Identical Information（相同信息）": [
            {"zh": "系统扫视：上→下或左→右", "en": "Scan systematically: top→bottom or left→right"},
            {"zh": "先找决定性差异", "en": "Hunt decisive differences first"},
        ],
    },
    "chem-phys": {
        "4A · Motion, forces, work, energy, equilibrium": [
            {"zh": "把生理情境翻译成受力/能量问题", "en": "Translate physio scenarios into force/energy problems"},
            {"zh": "静力平衡：合力与合力矩为零", "en": "Static equilibrium: net force and torque zero"},
        ],
        "4B · Fluids for circulation and gas exchange": [
            {"zh": "连续性方程与伯努利直觉", "en": "Continuity equation and Bernoulli intuition"},
            {"zh": "阻力、半径与流量关系（Poiseuille 思想）", "en": "Resistance, radius, flow (Poiseuille idea)"},
        ],
        "4C · Electrochemistry and electrical circuits": [
            {"zh": "氧化还原半反应与电子流向", "en": "Half-reactions and electron flow"},
            {"zh": "欧姆定律与串并联", "en": "Ohm’s law with series/parallel"},
        ],
        "4D · Light and sound interacting with matter": [
            {"zh": "折射、全反射、透镜；声波强度与多普勒", "en": "Refraction/TIR/lenses; sound intensity and Doppler"},
        ],
        "4E · Atoms, nuclear decay, electronic structure": [
            {"zh": "能级、光谱、半衰期指数衰减", "en": "Levels, spectra, exponential half-life"},
        ],
        "5A · Unique nature of water and its solutions": [
            {"zh": "氢键、比热、疏水效应", "en": "H-bonding, heat capacity, hydrophobic effect"},
            {"zh": "酸碱平衡与缓冲", "en": "Acid–base balance and buffers"},
        ],
        "5B · Molecules and intermolecular interactions": [
            {"zh": "分子间作用力决定熔点/溶解度", "en": "IMFs shape melting point and solubility"},
        ],
        "5C · Separation and purification methods": [
            {"zh": "色谱/电泳：按性质分离", "en": "Chromatography/electrophoresis separate by property"},
        ],
        "5D · Biologically relevant molecules": [
            {"zh": "官能团在水中的酸碱/氢键行为", "en": "Acid-base/H-bonding behavior of groups in water"},
            {"zh": "肽键形成/水解", "en": "Peptide bond formation/hydrolysis"},
        ],
        "5E · Chemical thermodynamics and kinetics": [
            {"zh": "ΔG vs 速率；催化剂不改平衡常数本质位置", "en": "ΔG vs rate; catalysts don’t change equilibrium position"},
        ],
    },
    "cars": {
        "Foundations of Comprehension": [
            {"zh": "Topic ≠ Thesis", "en": "Topic ≠ Thesis"},
            {"zh": "标出例证、让步、转折的功能", "en": "Label functions: example, concession, contrast"},
        ],
        "Reasoning Within the Text": [
            {"zh": "问“作者凭什么支持这个主张”", "en": "Ask what supports the author’s claim"},
            {"zh": "强干扰项：说得对但不在文中", "en": "Strong distractor: true in world, absent in passage"},
        ],
        "Reasoning Beyond the Text": [
            {"zh": "新情境必须保持原则一致", "en": "New scenarios must keep the principle intact"},
            {"zh": "类推失败常常是关系不匹配", "en": "Failed analogies usually mismatch the relation"},
        ],
    },
    "bio-biochem": {
        "1A · Proteins and amino acids": [
            {"zh": "侧链化学决定酶催化与结合", "en": "Side-chain chemistry drives catalysis and binding"},
            {"zh": "电泳/层析分离逻辑", "en": "Logic of electrophoresis/chromatography separations"},
        ],
        "1B · Gene to protein": [
            {"zh": "转录调控与翻译起始是高频考点", "en": "Transcriptional control and translation initiation are high-yield"},
            {"zh": "密码子简并降低部分突变影响", "en": "Degeneracy softens some mutation effects"},
        ],
        "1C · Heritable information & diversity": [
            {"zh": "复制保真与修复路径（导论）", "en": "Replication fidelity and repair paths (intro)"},
            {"zh": "减数分裂错误 → 非整倍体思想", "en": "Meiotic errors → aneuploidy idea"},
        ],
        "1D · Bioenergetics and fuel metabolism": [
            {"zh": "代谢路径按能量状态（ATP/NADH）调节", "en": "Pathways regulated by energy charge (ATP/NADH)"},
            {"zh": "有氧 vs 无氧产物与 ATP 产率对比", "en": "Aerobic vs anaerobic products and ATP yield"},
        ],
        "2A · Assemblies of molecules, cells, cell groups": [
            {"zh": "膜结构：流动镶嵌与选择性通透", "en": "Fluid mosaic and selective permeability"},
            {"zh": "组织类型与功能匹配", "en": "Tissue types matched to function"},
        ],
        "2B · Prokaryotes and viruses": [
            {"zh": "原核与真核基因表达差异", "en": "Prokaryotic vs eukaryotic gene expression differences"},
            {"zh": "病毒生命周期决定治疗靶点思路", "en": "Viral life cycle shapes therapy-target thinking"},
        ],
        "2C · Division, differentiation, specialization": [
            {"zh": "细胞周期阶段与检查点", "en": "Cell-cycle phases and checkpoints"},
            {"zh": "凋亡 vs 坏死（导论）", "en": "Apoptosis vs necrosis (intro)"},
        ],
        "3A · Nervous and endocrine systems": [
            {"zh": "突触传递与神经递质类别直觉", "en": "Synaptic transmission and transmitter-class intuition"},
            {"zh": "反馈环：下丘脑—垂体—靶腺", "en": "Feedback: hypothalamus–pituitary–target gland"},
        ],
        "3B · Main organ systems": [
            {"zh": "交换界面：肺泡、绒毛、肾单位", "en": "Exchange interfaces: alveoli, villi, nephrons"},
            {"zh": "稳态回路：感受器-整合-效应器", "en": "Homeostasis loop: sensor–integrator–effector"},
        ],
    },
    "psych-soc": {
        "6A · Sensing the environment": [
            {"zh": "绝对阈值与差别阈值", "en": "Absolute and difference thresholds"},
            {"zh": "信号检测：击中/虚报", "en": "Signal detection: hits/false alarms"},
        ],
        "6B · Making sense of the environment": [
            {"zh": "格式塔组织原则；深度线索", "en": "Gestalt organization; depth cues"},
            {"zh": "自上而下期望塑造知觉", "en": "Top-down expectations shape perception"},
        ],
        "6C · Responding to the world": [
            {"zh": "情绪理论对照（导论）", "en": "Emotion theories contrasted (intro)"},
            {"zh": "应激：原发/次级评估与应对", "en": "Stress: primary/secondary appraisal and coping"},
        ],
        "7A · Individual influences on behavior": [
            {"zh": "人格特质 vs 情境论张力", "en": "Trait vs situationist tension"},
            {"zh": "生物因素与行为的交互", "en": "Biological factors interact with behavior"},
        ],
        "7B · Social processes that influence behavior": [
            {"zh": "从众、服从、群体影响", "en": "Conformity, obedience, group influence"},
            {"zh": "社会促进与社会懈怠", "en": "Social facilitation and social loafing"},
        ],
        "7C · Attitude and behavior change": [
            {"zh": "认知失调与说服双路径", "en": "Cognitive dissonance and dual-process persuasion"},
            {"zh": "习惯化 vs 敏感化", "en": "Habituation vs sensitization"},
        ],
        "8A · Self-identity": [
            {"zh": "自我概念、角色认同、社会认同", "en": "Self-concept, role identity, social identity"},
            {"zh": "自我呈现与印象管理", "en": "Self-presentation and impression management"},
        ],
        "8B · Social thinking": [
            {"zh": "归因偏差与刻板印象", "en": "Attribution biases and stereotypes"},
            {"zh": "态度形成：情感、行为、认知成分", "en": "Attitudes: affective, behavioral, cognitive components"},
        ],
        "8C · Social interactions": [
            {"zh": "吸引、依恋、攻击与利他（导论）", "en": "Attraction, attachment, aggression, altruism (intro)"},
            {"zh": "歧视行为 vs 偏见态度", "en": "Discriminatory behavior vs prejudiced attitudes"},
        ],
        "9A · Understanding social structure": [
            {"zh": "地位、角色、群体、网络", "en": "Status, roles, groups, networks"},
            {"zh": "制度如何塑造机会结构", "en": "Institutions shape opportunity structures"},
        ],
        "9B · Demographic characteristics and processes": [
            {"zh": "年龄、性别、种族/族群、移民作为社会类别", "en": "Age, gender, race/ethnicity, migration as social categories"},
            {"zh": "人口过程：出生、死亡、迁移", "en": "Demographic processes: fertility, mortality, migration"},
        ],
        "10A · Social inequality": [
            {"zh": "社会经济地位与健康结果", "en": "SES and health outcomes"},
            {"zh": "文化资本、社会资本概念", "en": "Cultural and social capital concepts"},
        ],
    },
}

# Merge overlapping buckets so shared subject pages pick up MCAT chapter notes
NOTES["biology"] = {**NOTES["biology"], **NOTES["bio-biochem"]}
NOTES["chemistry"] = {**NOTES["chemistry"], **{k: v for k, v in NOTES["chem-phys"].items() if k.startswith("5") or k.startswith("4E")}}
NOTES["physics"] = {**NOTES["physics"], **{k: v for k, v in NOTES["chem-phys"].items() if k.startswith("4")}}
NOTES["chem-phys"] = {
    **NOTES.get("physics", {}),
    **NOTES.get("chemistry", {}),
    **NOTES.get("chem-phys", {}),
}
NOTES["bio-biochem"] = {
    **NOTES.get("biology", {}),
    **NOTES.get("biochemistry", {}),
    **NOTES.get("bio-biochem", {}),
}
NOTES["psych-soc"] = {
    **NOTES.get("behavioral-social", {}),
    **NOTES.get("psych-soc", {}),
}


def _chapter_id(title: str, index: int) -> str:
    raw = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", title).strip("-").lower()
    raw = raw[:48] or "ch"
    return f"ch-{index}-{raw}"


def notes_for(slug: str, chapter_title: str) -> list[dict[str, str]]:
    try:
        from knowledge.models import ChapterNote

        rows = list(
            ChapterNote.objects.filter(subject_slug=slug, chapter_title=chapter_title)
            .order_by("sort_order", "id")
            .values("text_zh", "text_en")
        )
        if rows:
            return [{"zh": r["text_zh"], "en": r["text_en"]} for r in rows]
        title_l = chapter_title.lower()
        left = chapter_title.split("·")[0].strip().lower()
        qs = ChapterNote.objects.filter(subject_slug=slug).order_by(
            "chapter_title", "sort_order", "id"
        )
        grouped: dict[str, list[dict[str, str]]] = {}
        for r in qs:
            grouped.setdefault(r.chapter_title, []).append(
                {"zh": r.text_zh, "en": r.text_en}
            )
        for key, val in grouped.items():
            k = key.lower()
            if k in title_l or title_l in k:
                return list(val)
            kleft = key.split("·")[0].strip().lower()
            if left and kleft == left and len(left) <= 4:
                return list(val)
    except Exception:
        pass

    bucket = NOTES.get(slug) or {}
    if chapter_title in bucket:
        return list(bucket[chapter_title])
    title_l = chapter_title.lower()
    for key, val in bucket.items():
        k = key.lower()
        if k in title_l or title_l in k:
            return list(val)
        left = key.split("·")[0].strip().lower()
        right = chapter_title.split("·")[0].strip().lower()
        if left and left == right and len(left) <= 4:
            return list(val)
    return []


def attach_notes(subject: dict) -> dict:
    """Return subject with study_notes and chapter_id on matching items."""
    if not subject:
        return subject
    slug = subject.get("slug") or ""
    idx = 0
    for group in subject.get("chapters") or []:
        for item in group.get("items") or []:
            title = item.get("title") or ""
            idx += 1
            item["chapter_id"] = _chapter_id(title, idx)
            notes = notes_for(slug, title)
            if notes:
                item["study_notes"] = notes
    return subject


def flashcards_for(slug: str, limit: int = 40) -> list[dict]:
    """Derive flashcards from study notes for a subject slug."""
    try:
        from knowledge.models import ChapterNote

        qs = ChapterNote.objects.filter(subject_slug=slug).order_by(
            "chapter_title", "sort_order", "id"
        )[:limit]
        cards = [
            {"chapter": r.chapter_title, "zh": r.text_zh, "en": r.text_en} for r in qs
        ]
        if cards:
            return cards
    except Exception:
        pass

    cards: list[dict] = []
    for title, notes in (NOTES.get(slug) or {}).items():
        for note in notes:
            cards.append({"chapter": title, "zh": note["zh"], "en": note["en"]})
            if len(cards) >= limit:
                return cards
    return cards
