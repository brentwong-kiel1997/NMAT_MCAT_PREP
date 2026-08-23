"""Exam maps for Gabay.

NMAT: CEM Bulletin of Information (8 subtests, Part 1 + Part 2).
MCAT: AAMC four sections (official names preserved).

Overlapping academic areas are merged into shared subject pages.
Exam-unique aptitude / CARS stay on exam-specific pages.
"""

from __future__ import annotations

# Shared content hubs (NMAT Part 2 academic ∩ MCAT science/social)
SHARED_SUBJECTS: dict[str, dict] = {
    "biology": {
        "slug": "biology",
        "name": "Biology",
        "name_zh": "生物学",
        "exams": ["NMAT", "MCAT"],
        "summary": "细胞、遗传、稳态、生态与生命过程；两边都会考，深度与题型不同。",
        "nmat_role": "NMAT Part 2 · Biology（30 题）",
        "mcat_role": "MCAT Bio/Biochem 的主体，并少量出现在 Chem/Phys",
        "scope": [
            "Unity and diversity of life",
            "Cells and cellular processes",
            "Genetics",
            "Plants and animals / organismal biology",
            "Development",
            "Regulation and homeostasis",
            "Organisms and environment",
        ],
        "exam_notes": {
            "NMAT": "对标大学导论级生物学；偏概念与综合认知（理解、应用、分析）。",
            "MCAT": "与生物化学交织；大量篇章题，强调实验设计与数据推理。",
        },
    },
    "chemistry": {
        "slug": "chemistry",
        "name": "Chemistry",
        "name_zh": "化学",
        "exams": ["NMAT", "MCAT"],
        "summary": "普化、分析、有机与生化基础；NMAT 独立成科，MCAT 拆进 Chem/Phys 与 Bio/Biochem。",
        "nmat_role": "NMAT Part 2 · Chemistry（30 题）",
        "mcat_role": "MCAT Chem/Phys + Bio/Biochem 中的化学 / 生化内容",
        "scope": [
            "General chemistry",
            "Analytical chemistry fundamentals",
            "Organic chemistry",
            "Biochemistry basics",
        ],
        "exam_notes": {
            "NMAT": "导论课范围：普化、分析、有机、生化常见基本概念。",
            "MCAT": "Chem/Phys 侧重普化/有机/物化交叉；Bio/Biochem 侧重生化通路与分子。",
        },
    },
    "physics": {
        "slug": "physics",
        "name": "Physics",
        "name_zh": "物理学",
        "exams": ["NMAT", "MCAT"],
        "summary": "力学到近代物理的导论框架；NMAT 独立成科，MCAT 主要落在 Chem/Phys。",
        "nmat_role": "NMAT Part 2 · Physics（30 题）",
        "mcat_role": "MCAT Chem/Phys 中的物理学（约四分之一权重量级）",
        "scope": [
            "Mechanics",
            "Thermodynamics",
            "Vibrations, waves, and optics",
            "Electricity and magnetism",
            "Modern physics",
        ],
        "exam_notes": {
            "NMAT": "大学导论物理常见主题，强调概念与推理。",
            "MCAT": "常嵌在生理/医疗情境篇章里，少纯算、多关系与估算。",
        },
    },
    "behavioral-social": {
        "slug": "behavioral-social",
        "name": "Behavioral & Social Sciences",
        "name_zh": "行为与社会科学",
        "exams": ["NMAT", "MCAT"],
        "summary": "心理、社会、人类学交叉；NMAT 叫 Social Science，MCAT 对应 Psych/Soc。",
        "nmat_role": "NMAT Part 2 · Social Science（心理学 / 社会学 / 人类学）",
        "mcat_role": "MCAT Psychological, Social, and Biological Foundations of Behavior",
        "scope": [
            "Introductory psychology",
            "Introductory sociology",
            "Anthropology (NMAT Social Science 明确包含)",
            "Behavior in biological / social context (MCAT 强调)",
        ],
        "exam_notes": {
            "NMAT": "Social Science = psychology + sociology + anthropology，导论深度。",
            "MCAT": "以心理、社会为主，并带少量生物基础；篇章题 + 独立题。",
        },
    },
    "biochemistry": {
        "slug": "biochemistry",
        "name": "Biochemistry",
        "name_zh": "生物化学",
        "exams": ["MCAT", "NMAT via Chemistry"],
        "summary": "MCAT 高权重专题；NMAT 不单开此科，CEM 将其放在 Chemistry 的 biochemistry 范围内。",
        "nmat_role": "非独立分测验；归入 Part 2 Chemistry 的导论生化",
        "mcat_role": "Bio/Biochem 与 Chem/Phys 的核心交叉内容（公开备考资料常给 ~25% 量级）",
        "scope": [
            "Amino acids, proteins, enzymes",
            "Carbohydrates and lipids",
            "Nucleic acids",
            "Metabolism overview",
            "Bioenergetics basics",
        ],
        "exam_notes": {
            "NMAT": "不要当成第八科以外的第九科；跟 Chemistry 一起复习即可。",
            "MCAT": "建议单开专题深挖；百分比来自常见备考分解，非 AAMC 官方权重量表。",
        },
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
                    "item_types": ["Word analogies", "Reading comprehension"],
                    "focus": "词汇关系与阅读理解。",
                },
                {
                    "slug": "inductive-reasoning",
                    "name": "Inductive Reasoning",
                    "name_zh": "归纳推理",
                    "shared": None,
                    "items": 30,
                    "item_types": [
                        "Number series",
                        "Letter series",
                        "Figural series",
                        "Figure grouping",
                    ],
                    "focus": "从有限信息归纳规则或关系。",
                },
                {
                    "slug": "quantitative",
                    "name": "Quantitative",
                    "name_zh": "数量推理",
                    "shared": None,
                    "items": 30,
                    "item_types": [
                        "Fundamental operations",
                        "Problem solving",
                        "Data interpretation",
                    ],
                    "focus": "组织并应用基础数学与推理求解。",
                },
                {
                    "slug": "perceptual-acuity",
                    "name": "Perceptual Acuity",
                    "name_zh": "知觉敏锐",
                    "shared": None,
                    "items": 30,
                    "item_types": [
                        "Hidden figure",
                        "Mirror image",
                        "Identical information",
                    ],
                    "focus": "干扰条件下的视觉识别、细节与空间关系。",
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
                    "focus": "大学导论生物学。内容见共用科目页。",
                },
                {
                    "slug": "physics",
                    "name": "Physics",
                    "name_zh": "物理学",
                    "shared": "physics",
                    "items": 30,
                    "item_types": [],
                    "focus": "大学导论物理学。内容见共用科目页。",
                },
                {
                    "slug": "social-science",
                    "name": "Social Science",
                    "name_zh": "社会科学",
                    "shared": "behavioral-social",
                    "items": 30,
                    "item_types": ["Psychology", "Sociology", "Anthropology"],
                    "focus": "心理 / 社会 / 人类学导论。内容见共用科目页。",
                },
                {
                    "slug": "chemistry",
                    "name": "Chemistry",
                    "name_zh": "化学",
                    "shared": "chemistry",
                    "items": 30,
                    "item_types": [],
                    "focus": "普化、分析、有机与生化导论。内容见共用科目页。",
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
    "discipline_mix_note": "下列学科百分比来自常见公开备考分解（如 Kaplan 等），用于复习配比，不是 AAMC 官方权重量表。题量/时长以 AAMC 为准。",
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
            ],
            "focus": "把普化、有机、物理、生化放进生命系统情境里考。",
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
            ],
            "focus": "生命系统中的生物与生化，强调过程、实验与数据。",
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
            ],
            "focus": "行为的心理、社会与生物基础。",
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
