"""Exam maps and chapter outlines for Gabay.

Sources (do not invent outside these):
- NMAT: CEM Bulletin of Information (subtests + Part 2 topic headings)
- MCAT: AAMC What’s on the MCAT Exam (Foundational Concepts + Content Categories)
"""

from __future__ import annotations

SHARED_SUBJECTS: dict[str, dict] = {
    "biology": {
        "slug": "biology",
        "name": "Biology",
        "name_zh": "生物学",
        "exams": ["NMAT", "MCAT"],
        "summary": "细胞、遗传、稳态、生态与生命过程；两边都会考，深度与题型不同。",
        "nmat_role": "NMAT Part 2 · Biology（30 题）",
        "mcat_role": "MCAT Bio/Biochem 主体，并少量出现在 Chem/Phys",
        "source_note": "NMAT 章节标题直接取自 CEM BOI Part 2 Biology；MCAT 侧列出与生物重叠的 AAMC Content Categories。",
        "exam_notes": {
            "NMAT": "对标大学导论级生物学；偏概念与综合认知（理解、应用、分析）。",
            "MCAT": "与生物化学交织；大量篇章题，强调实验设计与数据推理。",
        },
        "chapters": [
            {
                "heading": "NMAT · CEM BOI 章节",
                "items": [
                    {"title": "Unity and Diversity of Life", "points": ["生命的统一性与多样性", "分类与演化导论概念"]},
                    {"title": "Cells and Cellular Processes", "points": ["细胞结构与功能", "细胞过程（代谢、膜转运等导论级）"]},
                    {"title": "Genetics", "points": ["遗传信息传递", "变异与遗传规律导论"]},
                    {"title": "The World of Plants and Animals", "points": ["植物与动物世界导论", "比较结构/功能常见考点"]},
                    {"title": "Development", "points": ["发育过程基本概念"]},
                    {"title": "Life Processes: Regulation and Homeostasis", "points": ["调节与稳态", "内环境维持"]},
                    {"title": "Organisms and Their Environment", "points": ["生物与环境", "生态关系导论"]},
                ],
            },
            {
                "heading": "MCAT · 相关 Content Categories（AAMC）",
                "items": [
                    {"title": "1C · Heritable information & genetic diversity", "points": ["跨代遗传", "增加遗传多样性的过程"]},
                    {"title": "2A · Assemblies of molecules, cells, and cell groups", "points": ["单细胞与多细胞组装层次"]},
                    {"title": "2B · Prokaryotes and viruses", "points": ["结构、生长、生理与遗传"]},
                    {"title": "2C · Cell division, differentiation, specialization", "points": ["分裂、分化与特化"]},
                    {"title": "3A · Nervous & endocrine coordination", "points": ["神经/内分泌如何协调器官系统"]},
                    {"title": "3B · Main organ systems", "points": ["主要器官系统的结构与整合功能"]},
                ],
            },
        ],
    },
    "chemistry": {
        "slug": "chemistry",
        "name": "Chemistry",
        "name_zh": "化学",
        "exams": ["NMAT", "MCAT"],
        "summary": "普化、分析、有机与生化基础；NMAT 独立成科，MCAT 拆进 Chem/Phys 与 Bio/Biochem。",
        "nmat_role": "NMAT Part 2 · Chemistry（30 题）",
        "mcat_role": "MCAT Chem/Phys + Bio/Biochem 中的化学 / 生化内容",
        "source_note": "NMAT 四块标题取自 CEM BOI Chemistry；MCAT 侧对应 AAMC FC5 及生化交叉类别。",
        "exam_notes": {
            "NMAT": "导论课范围：普化、分析、有机、生化常见基本概念。",
            "MCAT": "Chem/Phys 侧重普化/有机/相互作用；Bio/Biochem 侧重生化分子与代谢。",
        },
        "chapters": [
            {
                "heading": "NMAT · CEM BOI 章节",
                "items": [
                    {"title": "General Chemistry", "points": ["原子结构与周期性", "化学键与计量", "酸碱、氧化还原、平衡导论"]},
                    {"title": "Analytical Chemistry", "points": ["定量分析基础", "常见分离/测定思路（导论级）"]},
                    {"title": "Organic Chemistry", "points": ["官能团与基本反应类型", "与生物分子相关的有机基础"]},
                    {"title": "Biochemistry", "points": ["生物大分子导论", "与代谢相关的基本概念（详见 Biochemistry 专题页）"]},
                ],
            },
            {
                "heading": "MCAT · 相关 Content Categories（AAMC）",
                "items": [
                    {"title": "5A · Water and its solutions", "points": ["水的独特性与溶液性质"]},
                    {"title": "5B · Molecules and intermolecular interactions", "points": ["分子本质与分子间作用"]},
                    {"title": "5C · Separation and purification methods", "points": ["分离纯化（含肽/蛋白相关方法）"]},
                    {"title": "5D · Biologically relevant molecules", "points": ["结构、功能与反应性"]},
                    {"title": "5E · Chemical thermodynamics and kinetics", "points": ["热力学与动力学原则"]},
                    {"title": "4E · Atoms, nuclear decay, electronic structure", "points": ["原子化学行为（Chem/Phys）"]},
                ],
            },
        ],
    },
    "physics": {
        "slug": "physics",
        "name": "Physics",
        "name_zh": "物理学",
        "exams": ["NMAT", "MCAT"],
        "summary": "力学到近代物理的导论框架；NMAT 独立成科，MCAT 主要落在 Chem/Phys。",
        "nmat_role": "NMAT Part 2 · Physics（30 题）",
        "mcat_role": "MCAT Chem/Phys 中的物理学（AAMC FC4）",
        "source_note": "NMAT 五块标题取自 CEM BOI Physics；MCAT 侧对应 AAMC Foundational Concept 4。",
        "exam_notes": {
            "NMAT": "大学导论物理常见主题，强调概念与推理。",
            "MCAT": "常嵌在生理/医疗情境篇章里，少纯算、多关系与估算。",
        },
        "chapters": [
            {
                "heading": "NMAT · CEM BOI 章节",
                "items": [
                    {"title": "Mechanics", "points": ["运动、力、功与能", "平衡与动量导论"]},
                    {"title": "Thermodynamics", "points": ["温度、热量与热力学定律导论"]},
                    {"title": "Vibrations, Waves, and Optics", "points": ["振动与波", "几何/波动光学基础"]},
                    {"title": "Electricity and Magnetism", "points": ["电场、电路基础", "磁学导论"]},
                    {"title": "Modern Physics", "points": ["近代物理导论概念（如量子/核现象入门）"]},
                ],
            },
            {
                "heading": "MCAT · Foundational Concept 4（AAMC）",
                "items": [
                    {"title": "4A · Motion, forces, work, energy, equilibrium", "points": ["生命系统中的平动、力、功、能与平衡"]},
                    {"title": "4B · Fluids, circulation, gas exchange", "points": ["血液循环与气体交换中的流体"]},
                    {"title": "4C · Electrochemistry and circuits", "points": ["电化学与电路元件"]},
                    {"title": "4D · Light and sound with matter", "points": ["光、声与物质的相互作用"]},
                    {"title": "4E · Atoms and electronic structure", "points": ["原子、核衰变与电子结构"]},
                ],
            },
        ],
    },
    "behavioral-social": {
        "slug": "behavioral-social",
        "name": "Behavioral & Social Sciences",
        "name_zh": "行为与社会科学",
        "exams": ["NMAT", "MCAT"],
        "summary": "心理、社会、人类学交叉；NMAT 叫 Social Science，MCAT 对应 Psych/Soc。",
        "nmat_role": "NMAT Part 2 · Social Science（Psychology / Sociology and Anthropology）",
        "mcat_role": "MCAT Psychological, Social, and Biological Foundations of Behavior",
        "source_note": "NMAT 按 CEM BOI：Psychology + Sociology and Anthropology。MCAT 按 AAMC FC6–10。",
        "exam_notes": {
            "NMAT": "Social Science = psychology + sociology + anthropology，导论深度。",
            "MCAT": "以心理、社会为主，并带少量生物基础；人类学不是独立主轴。",
        },
        "chapters": [
            {
                "heading": "NMAT · CEM BOI 章节",
                "items": [
                    {"title": "Psychology", "points": ["导论心理学概念", "行为与心理过程基础"]},
                    {"title": "Sociology and Anthropology", "points": ["社会结构与文化导论", "人类学基本视角（NMAT 明确包含）"]},
                ],
            },
            {
                "heading": "MCAT · Foundational Concepts 6–10（AAMC）",
                "items": [
                    {"title": "FC6 · Perceive, think, react", "points": ["6A Sensing the environment", "6B Making sense of the environment", "6C Responding to the world"]},
                    {"title": "FC7 · Behavior and behavior change", "points": ["7A Individual influences on behavior", "7B Social processes that influence human behavior", "7C Attitude and behavior change"]},
                    {"title": "FC8 · Self, others, interactions", "points": ["8A Self-identity", "8B Social thinking", "8C Social interactions"]},
                    {"title": "FC9 · Cultural and social differences", "points": ["9A Understanding social structure", "9B Demographic characteristics and processes"]},
                    {"title": "FC10 · Stratification and resources", "points": ["10A Social inequality"]},
                ],
            },
        ],
    },
    "biochemistry": {
        "slug": "biochemistry",
        "name": "Biochemistry",
        "name_zh": "生物化学",
        "exams": ["MCAT", "NMAT via Chemistry"],
        "summary": "MCAT 高权重专题；NMAT 不单开此科，CEM 将其放在 Chemistry 的 Biochemistry。",
        "nmat_role": "非独立分测验；归入 Part 2 Chemistry · Biochemistry",
        "mcat_role": "主要落在 Bio/Biochem FC1，并与 Chem/Phys 生化交叉",
        "source_note": "章节按 AAMC Bio/Biochem Foundational Concept 1 的 Content Categories；NMAT 仅作 Chemistry 子块对照。",
        "exam_notes": {
            "NMAT": "不要当成第九科；跟 Chemistry · Biochemistry 一起复习。",
            "MCAT": "AAMC 估计 Bio/Biochem 中 FC1 约占该科 55%（约到 5%）。",
        },
        "chapters": [
            {
                "heading": "NMAT 对照",
                "items": [
                    {"title": "Chemistry · Biochemistry（CEM）", "points": ["生物大分子导论", "与导论化学衔接的代谢基本概念"]},
                ],
            },
            {
                "heading": "MCAT · Foundational Concept 1（AAMC）",
                "items": [
                    {"title": "1A · Proteins and amino acids", "points": ["氨基酸与蛋白质结构/功能"]},
                    {"title": "1B · Gene to protein", "points": ["遗传信息从基因到蛋白质"]},
                    {"title": "1C · Heritable information & diversity", "points": ["跨代遗传与遗传多样性过程"]},
                    {"title": "1D · Bioenergetics and fuel metabolism", "points": ["生物能学与燃料分子代谢"]},
                ],
            },
        ],
    },
}


NMAT: dict = {
    "slug": "nmat",
    "name": "NMAT",
    "full_name": "National Medical Admission Test",
    "name_zh": "菲律宾医学院入学考试",
    "admin": "CEM (Center for Educational Measurement)",
    "format": "两部分共 240 道选择题；每科 30 题。Part 1 心智能力 2h15m，Part 2 学业能力 1h30m，中间约 10 分钟休息。",
    "parts": [
        {
            "id": "part1",
            "name": "Part 1 · Mental Ability",
            "name_zh": "心智能力",
            "time": "2 hours 15 minutes",
            "items": 120,
            "subjects": [
                {
                    "slug": "verbal",
                    "name": "Verbal",
                    "name_zh": "语文",
                    "shared": None,
                    "items": 30,
                    "pacing": "约 30 minutes（BOI 建议）",
                    "item_types": ["Analogies", "Reading Comprehension"],
                    "focus": "词汇关系与阅读理解。",
                    "source_note": "章节按 CEM BOI Verbal 题型划分。",
                    "chapters": [
                        {
                            "heading": "大知识点 / 章节",
                            "items": [
                                {
                                    "title": "Analogies（词义类比）",
                                    "points": [
                                        "识别词对关系（同义、反义、部分-整体、因果、程度等）",
                                        "把关系迁移到选项，排除貌合神离干扰项",
                                    ],
                                },
                                {
                                    "title": "Reading Comprehension（阅读理解）",
                                    "points": [
                                        "抓主旨与段落功能",
                                        "细节定位与推断（不超出文本）",
                                        "语气/态度与论证结构",
                                    ],
                                },
                            ],
                        }
                    ],
                },
                {
                    "slug": "inductive-reasoning",
                    "name": "Inductive Reasoning",
                    "name_zh": "归纳推理",
                    "shared": None,
                    "items": 30,
                    "pacing": "约 35 minutes（BOI 建议）",
                    "item_types": [
                        "Figure Series",
                        "Figure Grouping",
                        "Number and Letter Series",
                    ],
                    "focus": "从有限信息归纳规则或关系。",
                    "source_note": "章节按 CEM BOI Inductive Reasoning 题型划分。",
                    "chapters": [
                        {
                            "heading": "大知识点 / 章节",
                            "items": [
                                {
                                    "title": "Figure Series（图形序列）",
                                    "points": ["旋转/翻转/增减元素", "位置、阴影、叠加规则归纳"],
                                },
                                {
                                    "title": "Figure Grouping（图形归类）",
                                    "points": ["共同属性归组", "排除唯一例外"],
                                },
                                {
                                    "title": "Number and Letter Series（数字与字母序列）",
                                    "points": ["等差/倍比/交替规则", "字母位置与双序列穿插"],
                                },
                            ],
                        }
                    ],
                },
                {
                    "slug": "quantitative",
                    "name": "Quantitative",
                    "name_zh": "数量推理",
                    "shared": None,
                    "items": 30,
                    "pacing": "约 40 minutes（BOI 建议）",
                    "item_types": [
                        "Fundamental Operations",
                        "Problem Solving",
                        "Data Interpretation",
                    ],
                    "focus": "组织并应用基础数学与推理求解。",
                    "source_note": "章节按 CEM BOI Quantitative 题型划分。",
                    "chapters": [
                        {
                            "heading": "大知识点 / 章节",
                            "items": [
                                {
                                    "title": "Fundamental Operations（基本运算）",
                                    "points": ["四则与优先级", "分数/百分数/比与比例速算"],
                                },
                                {
                                    "title": "Problem Solving（应用题）",
                                    "points": ["把文字转成数量关系", "单位换算与合理性检查"],
                                },
                                {
                                    "title": "Data Interpretation（资料判读）",
                                    "points": ["表/图读取", "比较、趋势与简单统计推理"],
                                },
                            ],
                        }
                    ],
                },
                {
                    "slug": "perceptual-acuity",
                    "name": "Perceptual Acuity",
                    "name_zh": "知觉敏锐",
                    "shared": None,
                    "items": 30,
                    "pacing": "约 30 minutes（BOI 建议）",
                    "item_types": [
                        "Hidden Figure",
                        "Mirror Image",
                        "Identical Information",
                    ],
                    "focus": "干扰条件下的视觉识别、细节与空间关系。",
                    "source_note": "章节按 CEM BOI Perceptual Acuity 题型划分。",
                    "chapters": [
                        {
                            "heading": "大知识点 / 章节",
                            "items": [
                                {
                                    "title": "Hidden Figure（隐藏图形）",
                                    "points": ["在复杂图中定位目标轮廓", "抗干扰与局部匹配"],
                                },
                                {
                                    "title": "Mirror Image（镜像）",
                                    "points": ["左右镜像判断", "翻转 vs 旋转区分"],
                                },
                                {
                                    "title": "Identical Information（相同信息）",
                                    "points": ["快速比对相同/差异", "细节精度与速度权衡"],
                                },
                            ],
                        }
                    ],
                },
            ],
        },
        {
            "id": "part2",
            "name": "Part 2 · Academic Proficiency",
            "name_zh": "学业能力",
            "time": "1 hour 30 minutes",
            "items": 120,
            "subjects": [
                {
                    "slug": "biology",
                    "name": "Biology",
                    "name_zh": "生物学",
                    "shared": "biology",
                    "items": 30,
                    "item_types": [],
                    "focus": "大学导论生物学。章节见共用科目页。",
                },
                {
                    "slug": "physics",
                    "name": "Physics",
                    "name_zh": "物理学",
                    "shared": "physics",
                    "items": 30,
                    "item_types": [],
                    "focus": "大学导论物理学。章节见共用科目页。",
                },
                {
                    "slug": "social-science",
                    "name": "Social Science",
                    "name_zh": "社会科学",
                    "shared": "behavioral-social",
                    "items": 30,
                    "item_types": ["Psychology", "Sociology and Anthropology"],
                    "focus": "心理 / 社会与人类学导论。章节见共用科目页。",
                },
                {
                    "slug": "chemistry",
                    "name": "Chemistry",
                    "name_zh": "化学",
                    "shared": "chemistry",
                    "items": 30,
                    "item_types": [],
                    "focus": "普化、分析、有机与生化导论。章节见共用科目页。",
                },
            ],
        },
    ],
}


MCAT: dict = {
    "slug": "mcat",
    "name": "MCAT",
    "full_name": "Medical College Admission Test",
    "name_zh": "北美医学院入学考试",
    "admin": "AAMC",
    "format": "四个官方科目；科学三科各 59 题 / 95 分钟，CARS 53 题 / 90 分钟。考试日顺序固定。",
    "discipline_mix_note": "学科百分比为常见备考分解；Foundational Concept 占比取自 AAMC What’s on the MCAT（约到 5%，不同卷会浮动）。",
    "sections": [
        {
            "slug": "chem-phys",
            "name": "Chemical and Physical Foundations of Biological Systems",
            "short": "Chem/Phys",
            "name_zh": "化学与物理基础",
            "unique": False,
            "questions": 59,
            "time": "95 minutes",
            "shared_links": ["chemistry", "physics", "biochemistry"],
            "discipline_mix": [
                "General chemistry ~30%（备考分解）",
                "First-semester biochemistry ~25%（备考分解）",
                "Introductory physics ~25%（备考分解）",
                "Organic chemistry ~15%（备考分解）",
                "Introductory biology ~5%（备考分解）",
                "AAMC FC4 ~40% / FC5 ~60%（该科内）",
            ],
            "focus": "把普化、有机、物理、生化放进生命系统情境里考。",
            "source_note": "章节 = AAMC Foundational Concepts 4–5 及全部 Content Categories。",
            "chapters": [
                {
                    "heading": "Foundational Concept 4（约 40%）",
                    "items": [
                        {"title": "4A · Motion, forces, work, energy, equilibrium", "points": ["生命系统中的平动、力、功、能与平衡"]},
                        {"title": "4B · Fluids for circulation and gas exchange", "points": ["血液循环、气体运动与交换中的流体"]},
                        {"title": "4C · Electrochemistry and electrical circuits", "points": ["电化学与电路元件"]},
                        {"title": "4D · Light and sound interacting with matter", "points": ["光、声与物质相互作用"]},
                        {"title": "4E · Atoms, nuclear decay, electronic structure", "points": ["原子、核衰变、电子结构与原子化学行为"]},
                    ],
                },
                {
                    "heading": "Foundational Concept 5（约 60%）",
                    "items": [
                        {"title": "5A · Unique nature of water and its solutions", "points": ["水及其溶液"]},
                        {"title": "5B · Molecules and intermolecular interactions", "points": ["分子与分子间作用"]},
                        {"title": "5C · Separation and purification methods", "points": ["分离与纯化"]},
                        {"title": "5D · Biologically relevant molecules", "points": ["生物相关分子的结构、功能与反应性"]},
                        {"title": "5E · Chemical thermodynamics and kinetics", "points": ["化学热力学与动力学"]},
                    ],
                },
            ],
        },
        {
            "slug": "cars",
            "name": "Critical Analysis and Reasoning Skills",
            "short": "CARS",
            "name_zh": "批判分析与推理",
            "unique": True,
            "questions": 53,
            "time": "90 minutes",
            "shared_links": [],
            "discipline_mix": [
                "Humanities ~50%（备考分解）",
                "Social sciences ~50%（备考分解）",
            ],
            "focus": "全篇章题；不要求特定学科内容知识，考理解与推理。",
            "skills": [
                "Foundations of Comprehension",
                "Reasoning Within the Text",
                "Reasoning Beyond the Text",
            ],
            "source_note": "章节按 AAMC CARS 三大技能轴展开（无学科内容大纲）。",
            "chapters": [
                {
                    "heading": "CARS 技能章节（AAMC）",
                    "items": [
                        {
                            "title": "Foundations of Comprehension",
                            "points": [
                                "理解主旨与主要观点",
                                "识别信息的作用（例证、定义、转折）",
                                "把握作者态度与论证基调",
                            ],
                        },
                        {
                            "title": "Reasoning Within the Text",
                            "points": [
                                "推断文内隐含但可支持的结论",
                                "评估论证强度与相关性",
                                "识别假设与逻辑关系",
                            ],
                        },
                        {
                            "title": "Reasoning Beyond the Text",
                            "points": [
                                "把原则应用到新情境",
                                "整合文外信息时仍忠于文本约束",
                                "判断类推是否成立",
                            ],
                        },
                    ],
                }
            ],
        },
        {
            "slug": "bio-biochem",
            "name": "Biological and Biochemical Foundations of Living Systems",
            "short": "Bio/Biochem",
            "name_zh": "生物与生化基础",
            "unique": False,
            "questions": 59,
            "time": "95 minutes",
            "shared_links": ["biology", "biochemistry", "chemistry"],
            "discipline_mix": [
                "Introductory biology ~65%（备考分解）",
                "First-semester biochemistry ~25%（备考分解）",
                "General chemistry ~5%（备考分解）",
                "Organic chemistry ~5%（备考分解）",
                "AAMC FC1 ~55% / FC2 ~20% / FC3 ~25%（该科内）",
            ],
            "focus": "生命系统中的生物与生化，强调过程、实验与数据。",
            "source_note": "章节 = AAMC Foundational Concepts 1–3 及全部 Content Categories。",
            "chapters": [
                {
                    "heading": "Foundational Concept 1（约 55%）",
                    "items": [
                        {"title": "1A · Proteins and amino acids", "points": ["蛋白质及其组成氨基酸的结构与功能"]},
                        {"title": "1B · Gene to protein", "points": ["遗传信息从基因到蛋白质的传递"]},
                        {"title": "1C · Heritable information & diversity", "points": ["跨代遗传与增加遗传多样性的过程"]},
                        {"title": "1D · Bioenergetics and fuel metabolism", "points": ["生物能学与燃料分子代谢"]},
                    ],
                },
                {
                    "heading": "Foundational Concept 2（约 20%）",
                    "items": [
                        {"title": "2A · Assemblies of molecules, cells, cell groups", "points": ["分子、细胞与细胞群的组装"]},
                        {"title": "2B · Prokaryotes and viruses", "points": ["原核生物与病毒的结构、生长、生理与遗传"]},
                        {"title": "2C · Division, differentiation, specialization", "points": ["细胞分裂、分化与特化"]},
                    ],
                },
                {
                    "heading": "Foundational Concept 3（约 25%）",
                    "items": [
                        {"title": "3A · Nervous and endocrine systems", "points": ["神经与内分泌系统如何协调器官系统"]},
                        {"title": "3B · Main organ systems", "points": ["主要器官系统的结构与整合功能"]},
                    ],
                },
            ],
        },
        {
            "slug": "psych-soc",
            "name": "Psychological, Social, and Biological Foundations of Behavior",
            "short": "Psych/Soc",
            "name_zh": "心理、社会与行为基础",
            "unique": False,
            "questions": 59,
            "time": "95 minutes",
            "shared_links": ["behavioral-social", "biology"],
            "discipline_mix": [
                "Introductory psychology ~65%（备考分解）",
                "Introductory sociology ~30%（备考分解）",
                "Introductory biology ~5%（备考分解）",
                "AAMC FC6 ~25% / FC7 ~35% / FC8 ~20% / FC9 ~15% / FC10 ~5%",
            ],
            "focus": "行为的心理、社会与生物基础。",
            "source_note": "章节 = AAMC Foundational Concepts 6–10 及全部 Content Categories。",
            "chapters": [
                {
                    "heading": "Foundational Concept 6（约 25%）",
                    "items": [
                        {"title": "6A · Sensing the environment", "points": ["感觉环境"]},
                        {"title": "6B · Making sense of the environment", "points": ["理解/组织环境信息"]},
                        {"title": "6C · Responding to the world", "points": ["对世界作出反应"]},
                    ],
                },
                {
                    "heading": "Foundational Concept 7（约 35%）",
                    "items": [
                        {"title": "7A · Individual influences on behavior", "points": ["影响行为的个体因素"]},
                        {"title": "7B · Social processes that influence behavior", "points": ["影响行为的社会过程"]},
                        {"title": "7C · Attitude and behavior change", "points": ["态度与行为改变"]},
                    ],
                },
                {
                    "heading": "Foundational Concept 8（约 20%）",
                    "items": [
                        {"title": "8A · Self-identity", "points": ["自我认同"]},
                        {"title": "8B · Social thinking", "points": ["社会思维"]},
                        {"title": "8C · Social interactions", "points": ["社会互动"]},
                    ],
                },
                {
                    "heading": "Foundational Concept 9（约 15%）",
                    "items": [
                        {"title": "9A · Understanding social structure", "points": ["理解社会结构"]},
                        {"title": "9B · Demographic characteristics and processes", "points": ["人口特征与过程"]},
                    ],
                },
                {
                    "heading": "Foundational Concept 10（约 5%）",
                    "items": [
                        {"title": "10A · Social inequality", "points": ["社会不平等与资源可及性"]},
                    ],
                },
            ],
        },
    ],
}


def shared_list() -> list[dict]:
    return list(SHARED_SUBJECTS.values())


def get_shared(slug: str) -> dict | None:
    return SHARED_SUBJECTS.get(slug)


def nmat_unique_subjects() -> list[dict]:
    return list(NMAT["parts"][0]["subjects"])


def get_nmat_unique(slug: str) -> dict | None:
    for s in nmat_unique_subjects():
        if s["slug"] == slug:
            return s
    return None


def get_mcat_section(slug: str) -> dict | None:
    for s in MCAT["sections"]:
        if s["slug"] == slug:
            return s
    return None
