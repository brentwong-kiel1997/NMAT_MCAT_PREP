"""Supplemental high-yield notes merged into portal/notes.py NOTES at load time.

Structure mirrors NOTES: subject_slug -> chapter_title -> list[{zh, en}].
"""

from __future__ import annotations

EXTRA_NOTES: dict[str, dict[str, list[dict[str, str]]]] = {
    "biology": {
        "Unity and Diversity of Life": [
            {"zh": "三域系统：细菌、古菌、真核生物", "en": "Three-domain system: Bacteria, Archaea, Eukarya"},
            {"zh": "自然选择：变异 + 选择 + 时间 → 适应", "en": "Natural selection: variation + selection + time → adaptation"},
            {"zh": "物种概念：可繁殖隔离是核心判据之一", "en": "Species concept: reproductive isolation is a core criterion"},
        ],
        "Cells and Cellular Processes": [
            {"zh": "线粒体与叶绿体支持内共生理论", "en": "Mitochondria and chloroplasts support endosymbiosis theory"},
            {"zh": "Na⁺/K⁺泵维持膜电位与细胞体积", "en": "Na⁺/K⁺ pump maintains membrane potential and cell volume"},
            {"zh": "竞争性 vs 非竞争性抑制：Km 与 Vmax 变化不同", "en": "Competitive vs noncompetitive inhibition: different Km/Vmax shifts"},
            {"zh": "有氧呼吸最终电子受体是 O₂；无氧用其他受体", "en": "Aerobic ETC uses O₂ as terminal acceptor; anaerobic uses alternatives"},
        ],
        "Genetics": [
            {"zh": "显性/隐性/共显性/不完全显性改变表型比", "en": "Dominant/recessive/codominant/incomplete dominance alter ratios"},
            {"zh": "连锁基因偏离 9:3:3:1；重组率反映距离", "en": "Linked genes deviate from 9:3:3:1; recombination rate reflects distance"},
            {"zh": "X 连锁：男性更易表现隐性性状", "en": "X-linked: males more often express recessive traits"},
            {"zh": "表观遗传：不改变 DNA 序列的可遗传表达改变", "en": "Epigenetics: heritable expression changes without DNA sequence change"},
        ],
        "The World of Plants and Animals": [
            {"zh": "C₃/C₄/ CAM 植物：固碳路径与气候适应", "en": "C₃/C₄/CAM plants: carbon-fixation paths and climate adaptation"},
            {"zh": "开管式 vs 闭管式循环：昆虫 vs 脊椎动物", "en": "Open vs closed circulation: insects vs vertebrates"},
            {"zh": "适应性辐射：共同祖先 → 多生态位形态", "en": "Adaptive radiation: common ancestor → diverse niche forms"},
        ],
        "Development": [
            {"zh": "形态发生素梯度决定体轴与器官位置", "en": "Morphogen gradients set body axes and organ positions"},
            {"zh": "同源框基因（Hox）保守调控发育模式", "en": "Hox genes conservatively pattern development"},
            {"zh": "干细胞全能性随发育阶段递减", "en": "Stem-cell potency decreases with developmental stage"},
        ],
        "Life Processes: Regulation and Homeostasis": [
            {"zh": "胰岛素↓血糖；胰高血糖素↑血糖", "en": "Insulin lowers glucose; glucagon raises glucose"},
            {"zh": "肾单位：滤过→重吸收→分泌调节体液", "en": "Nephron: filtration → reabsorption → secretion regulates fluids"},
            {"zh": "体温调节：出汗/血管舒缩 + 行为调节", "en": "Thermoregulation: sweating/vasomotion plus behavioral adjustments"},
        ],
        "Organisms and Their Environment": [
            {"zh": "10% 能量传递法则：营养级间大量耗散", "en": "~10% energy transfer rule: heavy loss between trophic levels"},
            {"zh": "演替：先锋物种改变环境 → 群落更替", "en": "Succession: pioneer species alter environment → community turnover"},
            {"zh": "生态位：资源与时间维度的功能角色", "en": "Niche: functional role across resource and time dimensions"},
        ],
        "1C · Heritable information & genetic diversity": [
            {"zh": "DNA 聚合酶校对 + 错配修复保真度", "en": "Polymerase proofreading + mismatch repair boost fidelity"},
            {"zh": "交叉互换发生在减数分裂前期 I", "en": "Crossing over occurs in prophase I of meiosis"},
            {"zh": "Hardy–Weinberg：p² + 2pq + q² = 1", "en": "Hardy–Weinberg: p² + 2pq + q² = 1"},
        ],
        "2A · Assemblies of molecules, cells, and cell groups": [
            {"zh": "磷脂双层的两亲性决定膜基本结构", "en": "Amphipathic phospholipids define the bilayer core"},
            {"zh": "紧密连接阻旁细胞泄漏；桥粒抗牵拉", "en": "Tight junctions block leak; desmosomes resist pull"},
            {"zh": "组织：上皮、结缔、肌肉、神经四大类", "en": "Tissues: epithelial, connective, muscle, nervous"},
        ],
        "2B · Prokaryotes and viruses": [
            {"zh": "革兰阳性壁厚肽聚糖；阴性有外膜", "en": "Gram-positive thick peptidoglycan; negative outer membrane"},
            {"zh": "操纵子：原核基因共调控单元", "en": "Operon: prokaryotic co-regulated gene cluster"},
            {"zh": "逆转录病毒携带逆转录酶整合宿主基因组", "en": "Retroviruses use reverse transcriptase to integrate into host genome"},
        ],
        "2C · Cell division, differentiation, specialization": [
            {"zh": "G₁/S/G₂/M 检查点：DNA 损伤与纺锤体监控", "en": "G₁/S/G₂/M checkpoints monitor DNA damage and spindle attachment"},
            {"zh": "cyclin–CDK 复合体驱动细胞周期", "en": "Cyclin–CDK complexes drive the cell cycle"},
            {"zh": "接触抑制丧失是体外培养癌细胞特征", "en": "Loss of contact inhibition marks cultured cancer cells"},
        ],
        "3A · Nervous & endocrine coordination": [
            {"zh": "静息电位 ≈ K⁺外流；动作电位 Na⁺内流", "en": "Resting potential ≈ K⁺ outflow; AP peak from Na⁺ influx"},
            {"zh": "髓鞘盐跃传导加速长距离信号", "en": "Myelin enables saltatory conduction over long distances"},
            {"zh": "负反馈轴：甲状腺轴、肾上腺皮质轴范例", "en": "Negative-feedback axes: thyroid and adrenal cortex examples"},
        ],
        "3B · Main organ systems": [
            {"zh": "血红蛋白 O₂ 结合曲线：协同结合、 Bohr 效应", "en": "Hb-O₂ curve: cooperative binding and Bohr effect"},
            {"zh": "心输出量 = 心率 × 每搏输出量", "en": "Cardiac output = heart rate × stroke volume"},
            {"zh": "免疫：先天（速发）vs 适应性（特异记忆）", "en": "Immunity: innate (fast) vs adaptive (specific memory)"},
        ],
    },
    "chemistry": {
        "General Chemistry": [
            {"zh": "理想气体 PV = nRT；注意 R 单位匹配", "en": "Ideal gas PV = nRT; match R units to pressure/volume"},
            {"zh": "ΔG = ΔH − TΔS；自发需 ΔG < 0", "en": "ΔG = ΔH − TΔS; spontaneity requires ΔG < 0"},
            {"zh": "缓冲：弱酸 + 共轭碱抵抗 pH 变化", "en": "Buffer: weak acid + conjugate base resists pH change"},
            {"zh": "氧化还原：电子从还原剂流向氧化剂", "en": "Redox: electrons flow from reductant to oxidant"},
        ],
        "Analytical Chemistry": [
            {"zh": "Beer 定律：A = εlc（稀溶液线性区）", "en": "Beer’s law: A = εlc (linear region for dilute solutions)"},
            {"zh": "系统误差可校正；随机误差靠重复减小", "en": "Systematic error is correctable; random error shrinks with replication"},
            {"zh": "内标法校正进样与仪器漂移", "en": "Internal standards correct injection and instrument drift"},
        ],
        "Organic Chemistry": [
            {"zh": "SN1：三级底物、弱亲核、溶剂稳定碳正离子", "en": "SN1: tertiary substrate, weak nucleophile, solvent stabilizes carbocation"},
            {"zh": "SN2：一级底物、强亲核、背面进攻立体化学翻转", "en": "SN2: primary substrate, strong nucleophile, backside attack inversion"},
            {"zh": "羰基亲核加成：醛酮 vs 羧酸衍生物反应性差异", "en": "Carbonyl addition: aldehyde/ketone vs carboxyl derivative reactivity"},
        ],
        "Biochemistry": [
            {"zh": "肽键平面性限制主链旋转", "en": "Peptide bond planarity restricts backbone rotation"},
            {"zh": "别构酶：底物结合改变其他位点亲和力", "en": "Allosteric enzymes: substrate binding alters other-site affinity"},
            {"zh": "辅酶 NAD⁺/FAD 作氧化还原载体", "en": "Coenzymes NAD⁺/FAD serve as redox carriers"},
        ],
        "5A · Water and its solutions": [
            {"zh": "Henderson–Hasselbalch：pH = pKa + log([A⁻]/[HA])", "en": "Henderson–Hasselbalch: pH = pKa + log([A⁻]/[HA])"},
            {"zh": "疏水效应：水合壳破坏驱动折叠/聚集", "en": "Hydrophobic effect: hydration-shell disruption drives folding/aggregation"},
            {"zh": "依数性：蒸气压降、沸点升、凝固点降", "en": "Colligative properties: vapor-pressure lowering, boiling-point elevation, freezing-point depression"},
        ],
        "5B · Molecules and intermolecular interactions": [
            {"zh": "氢键方向性与强度低于共价键", "en": "Hydrogen bonds are directional and weaker than covalent bonds"},
            {"zh": "London 色散力：瞬时偶极诱导所有分子", "en": "London dispersion: instantaneous dipoles affect all molecules"},
            {"zh": "极性分子溶解极性溶剂（相似相溶）", "en": "Polar molecules dissolve in polar solvents (like dissolves like)"},
        ],
        "5C · Separation and purification methods": [
            {"zh": "凝胶过滤：按分子大小分离", "en": "Size-exclusion chromatography separates by molecular size"},
            {"zh": "离子交换：按净电荷与 pH 分离蛋白", "en": "Ion exchange separates proteins by net charge at given pH"},
            {"zh": "SDS-PAGE：变性胶按分子量分离", "en": "SDS-PAGE separates denatured proteins by molecular weight"},
        ],
        "5D · Biologically relevant molecules": [
            {"zh": "α 螺旋/β 折叠靠主链氢键稳定", "en": "α-helix/β-sheet stabilized by backbone hydrogen bonds"},
            {"zh": "糖异构：葡萄糖/果糖/半乳糖结构差异", "en": "Sugar isomers: glucose/fructose/galactose structural differences"},
            {"zh": "脂肪酸饱和度影响熔点与膜流动性", "en": "Fatty-acid saturation affects melting point and membrane fluidity"},
        ],
        "5E · Chemical thermodynamics and kinetics": [
            {"zh": "活化能：过渡态与反应速率相关", "en": "Activation energy links transition state to reaction rate"},
            {"zh": "催化剂提供低能路径，不改变 ΔG", "en": "Catalysts lower pathway energy without changing ΔG"},
            {"zh": "平衡常数 K 只随温度变（理想条件下）", "en": "Equilibrium constant K depends on temperature only (ideal conditions)"},
        ],
        "4E · Atoms, nuclear decay, electronic structure": [
            {"zh": " aufbau + Pauli + Hund 填电子", "en": "Aufbau + Pauli + Hund rules fill orbitals"},
            {"zh": "同周期电负性右增；同族金属性下增", "en": "Electronegativity rises right across period; metallic character rises down group"},
            {"zh": "α/β/γ 衰变：质量数与电荷变化不同", "en": "α/β/γ decay differ in mass-number and charge changes"},
        ],
    },
    "physics": {
        "Mechanics": [
            {"zh": "牛顿第二定律：ΣF = ma（矢量）", "en": "Newton’s second law: ΣF = ma (vector form)"},
            {"zh": "动能 Ek = ½mv²；重力势能 Ep = mgh", "en": "Kinetic energy Ek = ½mv²; gravitational Ep = mgh"},
            {"zh": "冲量 J = FΔt = Δp", "en": "Impulse J = FΔt = Δp"},
            {"zh": "转动：τ = Iα；角动量 L = Iω", "en": "Rotation: τ = Iα; angular momentum L = Iω"},
        ],
        "Thermodynamics": [
            {"zh": "热机效率受卡诺极限约束", "en": "Heat-engine efficiency bounded by Carnot limit"},
            {"zh": "等温 vs 绝热过程：Q 与 ΔU 关系不同", "en": "Isothermal vs adiabatic: different Q and ΔU relations"},
            {"zh": "熵增：孤立系统自发过程 ΔS > 0", "en": "Entropy increase: spontaneous processes in isolated systems raise ΔS"},
        ],
        "Vibrations, Waves, and Optics": [
            {"zh": "简谐振子周期 T = 2π√(m/k)", "en": "SHM period T = 2π√(m/k)"},
            {"zh": "驻波：节点与腹点位置固定", "en": "Standing waves: fixed node and antinode positions"},
            {"zh": "薄透镜 1/f = 1/do + 1/di", "en": "Thin lens: 1/f = 1/do + 1/di"},
        ],
        "Electricity and Magnetism": [
            {"zh": "库仑 F = kq₁q₂/r²", "en": "Coulomb force F = kq₁q₂/r²"},
            {"zh": "并联电阻 1/R = Σ1/Ri；串联 R = ΣRi", "en": "Parallel 1/R = Σ1/Ri; series R = ΣRi"},
            {"zh": "楞次定律：感应电流反抗磁通变化", "en": "Lenz’s law: induced current opposes flux change"},
        ],
        "Modern Physics": [
            {"zh": "E = hf；光子动量 p = h/λ", "en": "E = hf; photon momentum p = h/λ"},
            {"zh": "德布罗意 λ = h/p", "en": "de Broglie λ = h/p"},
            {"zh": "半衰期 N = N₀(½)^(t/t½)", "en": "Half-life decay N = N₀(½)^(t/t½)"},
        ],
        "4A · Motion, forces, work, energy, equilibrium": [
            {"zh": "斜面分解：重力平行/垂直分量", "en": "Incline decomposition: parallel/perpendicular gravity components"},
            {"zh": "功率 P = Fv（恒力同向时）", "en": "Power P = Fv when force aligns with velocity"},
            {"zh": "杠杆平衡：F₁d₁ = F₂d₂", "en": "Lever equilibrium: F₁d₁ = F₂d₂"},
        ],
        "4B · Fluids, circulation, gas exchange": [
            {"zh": "浮力 Fb = ρfluid Vdisplaced g", "en": "Buoyancy Fb = ρfluid Vdisplaced g"},
            {"zh": "血压 ≈ 流量 × 阻力（类比欧姆定律）", "en": "Blood pressure ≈ flow × resistance (Ohm-like analogy)"},
            {"zh": "表面张力与毛细现象：小管径液体上升", "en": "Surface tension and capillary rise in narrow tubes"},
        ],
        "4C · Electrochemistry and circuits": [
            {"zh": "E°cell = E°red − E°ox（约定方向）", "en": "E°cell = E°red − E°ox (watch sign convention)"},
            {"zh": "电容 C = Q/V；并联 C 相加", "en": "Capacitance C = Q/V; parallel capacitors add"},
            {"zh": "RC 时间常数 τ = RC", "en": "RC time constant τ = RC"},
        ],
        "4D · Light and sound with matter": [
            {"zh": "折射 n = c/v；斯涅尔定律 n₁sinθ₁ = n₂sinθ₂", "en": "Index n = c/v; Snell’s law n₁sinθ₁ = n₂sinθ₂"},
            {"zh": "多普勒：源/观察者运动改变频率", "en": "Doppler: source/observer motion shifts frequency"},
            {"zh": "共振：驱动频率匹配固有频率", "en": "Resonance when driving frequency matches natural frequency"},
        ],
        "4E · Atoms and electronic structure": [
            {"zh": "吸收光谱：电子跃迁到高能级", "en": "Absorption spectra: electrons jump to higher levels"},
            {"zh": "光电效应阈值频率与材料相关", "en": "Photoelectric threshold frequency is material-specific"},
        ],
    },
    "behavioral-social": {
        "Psychology": [
            {"zh": "经典条件反射：刺激泛化与分化", "en": "Classical conditioning: stimulus generalization and discrimination"},
            {"zh": "操作条件反射：强化计划塑造行为", "en": "Operant conditioning: reinforcement schedules shape behavior"},
            {"zh": "工作记忆容量有限（约 4±1 组块）", "en": "Working memory capacity is limited (~4±1 chunks)"},
        ],
        "Sociology and Anthropology": [
            {"zh": "社会建构：现实部分由集体定义", "en": "Social construction: reality partly defined collectively"},
            {"zh": "民族志：参与观察理解文化意义", "en": "Ethnography: participant observation to grasp cultural meaning"},
            {"zh": "功能主义 vs 冲突论：稳定 vs 权力斗争视角", "en": "Functionalism vs conflict theory: stability vs power-struggle lens"},
        ],
        "FC6 · Perceive, think, react": [
            {"zh": "韦伯定律：可觉差与刺激强度成比例", "en": "Weber’s law: detectable difference scales with stimulus intensity"},
            {"zh": "双加工：系统1快启发 vs 系统2慢分析", "en": "Dual process: fast heuristic System 1 vs slow analytic System 2"},
        ],
        "FC7 · Behavior and behavior change": [
            {"zh": "自我效能影响坚持与目标达成", "en": "Self-efficacy affects persistence and goal attainment"},
            {"zh": "计划行为理论：态度、主观规范、知觉控制", "en": "Theory of planned behavior: attitude, subjective norm, perceived control"},
        ],
        "FC8 · Self, others, interactions": [
            {"zh": "旁观者效应：他人在场降低救助概率", "en": "Bystander effect: others’ presence lowers helping likelihood"},
            {"zh": "自我服务偏差：成功归内因、失败归外因", "en": "Self-serving bias: credit success internally, blame failure externally"},
        ],
        "FC9 · Cultural and social differences": [
            {"zh": "文化智力：跨文化适应与沟通", "en": "Cultural intelligence: cross-cultural adaptation and communication"},
            {"zh": "少数群体地位与健康压力负荷相关", "en": "Minority status links to health via stress burden"},
        ],
        "FC10 · Stratification and resources": [
            {"zh": "健康社会梯度：SES 越低风险越高", "en": "Health social gradient: lower SES, higher risk"},
            {"zh": "结构性障碍限制医疗服务可及性", "en": "Structural barriers limit healthcare access"},
        ],
    },
    "biochemistry": {
        "Chemistry · Biochemistry（CEM）": [
            {"zh": "NMAT 生化块常与酶、氨基酸、代谢路径联动", "en": "NMAT biochem block often ties enzymes, amino acids, and pathways"},
            {"zh": "记住中心代谢物：葡萄糖、丙酮酸、乙酰 CoA", "en": "Hub metabolites: glucose, pyruvate, acetyl-CoA"},
        ],
        "1A · Proteins and amino acids": [
            {"zh": "等电点 pI：净电荷为零的 pH", "en": "Isoelectric point pI: pH where net charge is zero"},
            {"zh": "协同结合使氧合曲线 S 形", "en": "Cooperative binding yields sigmoid oxygenation curves"},
            {"zh": "不可逆抑制：共价修饰活性位点", "en": "Irreversible inhibition: covalent modification of active site"},
        ],
        "1B · Gene to protein": [
            {"zh": "5' 帽与 poly-A 尾稳定真核 mRNA", "en": "5' cap and poly-A tail stabilize eukaryotic mRNA"},
            {"zh": "内含子剪接：snRNP 催化", "en": "Intron splicing catalyzed by snRNPs"},
            {"zh": "摆动假说解释第三密码子简并", "en": "Wobble hypothesis explains third-base codon degeneracy"},
        ],
        "1C · Heritable information & diversity": [
            {"zh": "端粒酶在生殖/干细胞中补偿末端缩短", "en": "Telomerase compensates end shortening in germline/stem cells"},
            {"zh": "移码突变常比错义突变影响更大", "en": "Frameshift mutations often impact more than missense"},
        ],
        "1D · Bioenergetics and fuel metabolism": [
            {"zh": "糖酵解净产 2 ATP + 2 NADH（胞质）", "en": "Glycolysis nets 2 ATP + 2 NADH (cytoplasm)"},
            {"zh": "TCA 每乙酰 CoA 产 3 NADH、1 FADH₂、1 GTP", "en": "TCA per acetyl-CoA: 3 NADH, 1 FADH₂, 1 GTP"},
            {"zh": "脂肪酸 β 氧化在线粒体产生乙酰 CoA", "en": "Fatty-acid β-oxidation in mitochondria yields acetyl-CoA"},
        ],
    },
    "verbal": {
        "Analogies（词义类比）": [
            {"zh": "先排除关系类型不匹配的选项", "en": "Eliminate options whose relation type mismatches first"},
            {"zh": "动词对注意及物/不及物与因果方向", "en": "For verb pairs watch transitivity and causal direction"},
        ],
        "Reading Comprehension（阅读理解）": [
            {"zh": "段落功能题：定义、举例、反驳、过渡", "en": "Paragraph-function items: define, exemplify, refute, transition"},
            {"zh": "排除绝对化措辞除非原文支持", "en": "Reject absolute wording unless the passage supports it"},
        ],
    },
    "inductive-reasoning": {
        "Figure Series（图形序列）": [
            {"zh": "奇偶项可能遵循不同子规则", "en": "Odd/even terms may follow different sub-rules"},
            {"zh": "旋转角度常是固定步长（90°、45°）", "en": "Rotation often uses fixed steps (90°, 45°)"},
        ],
        "Figure Grouping（图形归类）": [
            {"zh": "对称性（轴对称/中心对称）是常见分组键", "en": "Symmetry (line/point) is a common grouping key"},
        ],
        "Number and Letter Series（数字与字母序列）": [
            {"zh": "二级差分：差值本身再成等差", "en": "Second-order difference: deltas form an arithmetic series"},
            {"zh": "质数/合数、平方/立方子序列", "en": "Prime/composite or square/cube subsequences"},
        ],
    },
    "quantitative": {
        "Fundamental Operations（基本运算）": [
            {"zh": "比例题：交叉相乘前检查单位一致", "en": "Proportions: cross-multiply only after unit alignment"},
            {"zh": "科学记数法便于大数乘除", "en": "Scientific notation simplifies large-number multiply/divide"},
        ],
        "Problem Solving（应用题）": [
            {"zh": "行程问题：画图标相遇/追及方向", "en": "Motion problems: sketch directions for meet/chase setups"},
            {"zh": "混合物：溶质守恒列方程", "en": "Mixtures: conserve solute when setting equations"},
        ],
        "Data Interpretation（资料判读）": [
            {"zh": "百分比变化 ≠ 百分点变化", "en": "Percent change ≠ percentage-point change"},
            {"zh": "平均数受极端值拉动；中位数更稳健", "en": "Mean pulled by extremes; median is more robust"},
        ],
    },
    "perceptual-acuity": {
        "Hidden Figure（隐藏图形）": [
            {"zh": "旋转试卷角度有时降低视觉噪声", "en": "Rotating the page can reduce visual clutter"},
        ],
        "Mirror Image（镜像）": [
            {"zh": "数字与字母镜像：b/d、p/q 易混", "en": "Mirrored digits/letters: b/d and p/q confuse easily"},
        ],
        "Identical Information（相同信息）": [
            {"zh": "标点与空格差异是常见陷阱", "en": "Punctuation and spacing gaps are common traps"},
        ],
    },
    "chem-phys": {
        "4A · Motion, forces, work, energy, equilibrium": [
            {"zh": "Chem/Phys 常把肌肉骨骼题化为力矩平衡", "en": "Chem/Phys often casts musculoskeletal items as torque balance"},
            {"zh": "能量守恒需明确是否非保守力做功", "en": "Energy conservation requires noting nonconservative work"},
        ],
        "4B · Fluids for circulation and gas exchange": [
            {"zh": "血流层流假设下 Poiseuille Q ∝ r⁴", "en": "Under laminar flow, Poiseuille Q ∝ r⁴"},
            {"zh": "肺泡气体交换依赖扩散与血流灌注匹配", "en": "Alveolar gas exchange depends on diffusion–perfusion matching"},
        ],
        "4C · Electrochemistry and electrical circuits": [
            {"zh": "标准氢电极 E° = 0 V 作参照", "en": "Standard hydrogen electrode E° = 0 V as reference"},
            {"zh": "电解质浓度影响电池电压（非标准态）", "en": "Electrolyte concentration shifts cell voltage (nonstandard conditions)"},
        ],
        "4D · Light and sound interacting with matter": [
            {"zh": "超声频率高 → 分辨率高、穿透浅", "en": "Higher ultrasound frequency → better resolution, less penetration"},
            {"zh": "全反射临界角 sinθc = n₂/n₁（n₁ > n₂）", "en": "TIR critical angle sinθc = n₂/n₁ when n₁ > n₂"},
        ],
        "4E · Atoms, nuclear decay, electronic structure": [
            {"zh": "医学成像同位素：半衰期适中、γ 发射", "en": "Medical isotopes: moderate half-life with gamma emission"},
        ],
        "5A · Unique nature of water and its solutions": [
            {"zh": "质子跳跃使酸在水中快速平衡", "en": "Proton hopping enables fast acid equilibration in water"},
            {"zh": "两亲分子在水中自组装成胶束/双层", "en": "Amphiphiles self-assemble into micelles/bilayers in water"},
        ],
        "5B · Molecules and intermolecular interactions": [
            {"zh": "氢键给体/受体配对决定特异性", "en": "H-bond donor/acceptor pairing drives specificity"},
        ],
        "5C · Separation and purification methods": [
            {"zh": "HPLC：高压提高分辨率与速度", "en": "HPLC: high pressure boosts resolution and speed"},
            {"zh": "电泳迁移率受电荷与分子大小影响", "en": "Electrophoretic mobility depends on charge and size"},
        ],
        "5D · Biologically relevant molecules": [
            {"zh": "酶活性位点常含催化性酸碱残基", "en": "Active sites often harbor catalytic acid/base residues"},
        ],
        "5E · Chemical thermodynamics and kinetics": [
            {"zh": "米氏动力学 v = Vmax[S]/(Km + [S])", "en": "Michaelis–Menten v = Vmax[S]/(Km + [S])"},
            {"zh": "过渡态理论：k 与 exp(−Ea/RT) 相关", "en": "Transition-state theory: k linked to exp(−Ea/RT)"},
        ],
    },
    "cars": {
        "Foundations of Comprehension": [
            {"zh": "区分作者声音与引述他人观点", "en": "Separate author voice from quoted viewpoints"},
            {"zh": "段落首句不一定是主旨；找综合句", "en": "First sentence may not be thesis; find synthesizing lines"},
        ],
        "Reasoning Within the Text": [
            {"zh": "加强题：找支持结论的前提或证据", "en": "Strengthen items: premises or evidence backing the conclusion"},
            {"zh": "削弱题：攻击假设或找反例", "en": "Weaken items: attack assumptions or supply counterexamples"},
        ],
        "Reasoning Beyond the Text": [
            {"zh": "应用题：新情境需映射核心原则而非表面相似", "en": "Application items map core principles, not surface similarity"},
            {"zh": "整合外部信息时不可 contradict 文本", "en": "Integrated outside info must not contradict the passage"},
        ],
    },
    "bio-biochem": {
        "1A · Proteins and amino acids": [
            {"zh": "锌指、亮氨酸拉链：DNA 结合基序", "en": "Zinc finger, leucine zipper: DNA-binding motifs"},
            {"zh": "变性剂：尿素、加热破坏非共价相互作用", "en": "Denaturants: urea, heat disrupt noncovalent interactions"},
        ],
        "1B · Gene to protein": [
            {"zh": "原核：转录与翻译可偶联", "en": "Prokaryotes: transcription and translation can couple"},
            {"zh": "RNAi：小 RNA 沉默基因表达", "en": "RNAi: small RNAs silence gene expression"},
        ],
        "1C · Heritable information & diversity": [
            {"zh": "CRISPR 导向 Cas 切割特定 DNA 序列", "en": "CRISPR guides Cas to cut specific DNA sequences"},
            {"zh": "非整倍体：染色体数目异常", "en": "Aneuploidy: abnormal chromosome number"},
        ],
        "1D · Bioenergetics and fuel metabolism": [
            {"zh": "磷酸肌酸快速缓冲 ATP 需求", "en": "Phosphocreatine buffers rapid ATP demand"},
            {"zh": "Cori 循环：肌肉乳酸→肝糖异生", "en": "Cori cycle: muscle lactate → liver gluconeogenesis"},
        ],
        "2A · Assemblies of molecules, cells, cell groups": [
            {"zh": "间隙连接允许小分子胞间通讯", "en": "Gap junctions permit small-molecule intercellular signaling"},
            {"zh": "基底膜：上皮与结缔组织界面", "en": "Basement membrane: epithelial–connective interface"},
        ],
        "2B · Prokaryotes and viruses": [
            {"zh": "抗生素耐药：酶降解、靶点改变、外排泵", "en": "Antibiotic resistance: enzymatic degradation, target change, efflux"},
            {"zh": "噬菌体：细菌病毒；溶菌 vs 溶原", "en": "Bacteriophages: bacterial viruses; lytic vs lysogenic"},
        ],
        "2C · Division, differentiation, specialization": [
            {"zh": "MPF：cyclin B + CDK1 驱动 M 期", "en": "MPF: cyclin B + CDK1 drives M phase"},
            {"zh": "诱导分化：外源信号启动特定基因程序", "en": "Induced differentiation: extrinsic signals launch gene programs"},
        ],
        "3A · Nervous and endocrine systems": [
            {"zh": "血脑屏障限制亲水性物质进入 CNS", "en": "Blood–brain barrier limits hydrophilic entry to CNS"},
            {"zh": "肾上腺素：战或逃交感反应", "en": "Epinephrine mediates fight-or-flight sympathetic response"},
        ],
        "3B · Main organ systems": [
            {"zh": "肾糖阈：超过阈值出现糖尿", "en": "Renal glucose threshold: glycosuria above limit"},
            {"zh": "抗体多样性：V(D)J 重组", "en": "Antibody diversity via V(D)J recombination"},
        ],
    },
    "psych-soc": {
        "6A · Sensing the environment": [
            {"zh": "感受器适应：持续刺激反应减弱", "en": "Sensory adaptation: response wanes under constant stimulus"},
            {"zh": "视觉：杆细胞暗视觉、锥细胞色觉", "en": "Vision: rods for dim light, cones for color"},
        ],
        "6B · Making sense of the environment": [
            {"zh": "知觉恒常性：距离变化仍识物体大小", "en": "Perceptual constancy: recognize size despite distance change"},
            {"zh": "错觉揭示知觉组织规则", "en": "Illusions reveal perceptual organization rules"},
        ],
        "6C · Responding to the world": [
            {"zh": "詹姆斯–兰格：生理唤醒先于情绪体验", "en": "James–Lange: physiological arousal precedes emotional experience"},
            {"zh": "一般适应综合征：警觉→抵抗→衰竭", "en": "General adaptation syndrome: alarm → resistance → exhaustion"},
        ],
        "7A · Individual influences on behavior": [
            {"zh": "五因素模型：OCEAN 人格维度", "en": "Five-factor model: OCEAN personality dimensions"},
            {"zh": "基因–环境交互：同一基因不同环境不同表型", "en": "Gene–environment interaction: same gene, different outcomes by context"},
        ],
        "7B · Social processes that influence behavior": [
            {"zh": "Milgram 服从：权威情境提高服从率", "en": "Milgram obedience: authority context raises compliance"},
            {"zh": "去个体化：群体降低自我觉察", "en": "Deindividuation: crowds reduce self-awareness"},
        ],
        "7C · Attitude and behavior change": [
            {"zh": "认知失调：态度与行为不一致引发不适", "en": "Cognitive dissonance: attitude–behavior mismatch causes discomfort"},
            {"zh": "外周路径：线索与情绪说服", "en": "Peripheral route: persuasion via cues and emotion"},
        ],
        "8A · Self-identity": [
            {"zh": "自我图式：组织关于自我的知识", "en": "Self-schemas organize self-related knowledge"},
            {"zh": "社会认同：群体成员身份影响自尊", "en": "Social identity: group membership shapes self-esteem"},
        ],
        "8B · Social thinking": [
            {"zh": "可得性启发：易想起事件高估频率", "en": "Availability heuristic: vivid recall inflates frequency estimates"},
            {"zh": "刻板印象威胁：担心验证偏见损害表现", "en": "Stereotype threat: fear of confirming bias hurts performance"},
        ],
        "8C · Social interactions": [
            {"zh": "互惠规范：回报他人给予", "en": "Reciprocity norm: return what others provide"},
            {"zh": "依恋风格影响亲密关系模式", "en": "Attachment styles shape close-relationship patterns"},
        ],
        "9A · Understanding social structure": [
            {"zh": "社会角色：期望行为集合", "en": "Social roles: sets of expected behaviors"},
            {"zh": "科层制：理性权威与规则导向", "en": "Bureaucracy: rational authority and rule orientation"},
        ],
        "9B · Demographic characteristics and processes": [
            {"zh": "人口转型：高出生死亡 → 低出生死亡", "en": "Demographic transition: high birth/death → low birth/death"},
            {"zh": "老龄化：依赖比与医疗需求上升", "en": "Aging populations raise dependency ratios and care demand"},
        ],
        "10A · Social inequality": [
            {"zh": "马太效应：优势累积放大不平等", "en": "Matthew effect: advantage accumulates, amplifying inequality"},
            {"zh": "医疗差距：保险、地理、语言均影响可及性", "en": "Healthcare gaps: insurance, geography, language affect access"},
        ],
    },
}


def merge_notes(base: dict) -> dict:
    """Merge EXTRA_NOTES into base without wiping existing; extend lists per chapter."""
    merged: dict[str, dict[str, list[dict[str, str]]]] = {}
    for slug, chapters in base.items():
        merged[slug] = {title: list(notes) for title, notes in chapters.items()}
    for slug, chapters in EXTRA_NOTES.items():
        if slug not in merged:
            merged[slug] = {}
        for title, notes in chapters.items():
            if title in merged[slug]:
                merged[slug][title] = list(merged[slug][title]) + list(notes)
            else:
                merged[slug][title] = list(notes)
    return merged
