"""Disease enrichment notes.

These are NOT official NMAT/MCAT blueprints. NMAT Part 2 Biology is
introductory college biology (CEM BOI), not clinical medicine. Use these
pages as biology/immunology/pathophys bridges and later med-school context.
"""

from __future__ import annotations

DISEASES: dict[str, dict] = {
    "tuberculosis": {
        "slug": "tuberculosis",
        "name": "Tuberculosis",
        "name_zh": "结核病",
        "short": "Mycobacterium tuberculosis 引起的慢性肉芽肿感染；菲律宾高负担病；作生物学/免疫学延伸阅读，非 NMAT 独立考科。",
        "systems": ["Respiratory", "Infectious"],
        "exams": ["Enrichment"],
        "exam_fit": "MCAT：免疫/感染基础可迁移；NMAT：仅当落到细胞/免疫导论概念时有间接帮助，临床诊疗细节不在 CEM 考纲。",
        "pathogen": "Mycobacterium tuberculosis（抗酸杆菌，胞内寄生）",
        "transmission": "飞沫核（airborne droplet nuclei）；密闭空间、长时间接触风险最高。",
        "pathophysiology": [
            "吸入后被肺泡巨噬细胞吞噬，但细菌可在细胞内存活。",
            "细胞介导免疫（Th1 / IFN-γ）驱动肉芽肿形成，限制扩散。",
            "原发感染多为潜伏性（LTBI）；免疫抑制时可再激活为活动性 TB。",
        ],
        "clinical": [
            "慢性咳嗽、咯血、盗汗、体重下降、午后低热。",
            "肺尖后段常见空洞性病变（再激活型）。",
            "肺外：淋巴结、骨、泌尿生殖道、脑膜（粟粒性 TB）。",
        ],
        "diagnosis": [
            "痰涂片抗酸染色、GeneXpert / NAAT、培养（金标准但慢）。",
            "胸部 X 线：上叶浸润/空洞。",
            "LTBI：TST 或 IGRA（不能区分活动与潜伏）。",
        ],
        "treatment": [
            "活动性肺 TB 标准：RIPE（Rifampin, Isoniazid, Pyrazinamide, Ethambutol）强化期后巩固。",
            "注意肝毒性、视神经炎（乙胺丁醇）、橘红色尿（利福平）。",
            "LTBI：异烟肼或利福平短程方案（依指南）。",
        ],
        "high_yield": [
            "肉芽肿 = 巨噬细胞 + 淋巴细胞；干酪样坏死是经典病理。",
            "BCG 可影响 TST，IGRA 相对不受 BCG 干扰。",
            "HIV 是再激活最强危险因素之一；CD4 低时表现可不典型。",
            "菲律宾情境：公共卫生负担高，接触史与拥挤居住很关键。",
        ],
        "mcat_bridge": "连接细胞免疫、肉芽肿炎症与公共卫生流行病学（传染病传播模型）。",
        "nmat_bridge": "生物/健康科学：病原、免疫逃逸、抗酸染色与一线药物副作用对应。",
    },
    "dengue": {
        "slug": "dengue",
        "name": "Dengue Fever",
        "name_zh": "登革热",
        "short": "登革病毒经埃及伊蚊传播；菲律宾常见虫媒病，考点在血浆渗漏与抗体依赖性增强。",
        "systems": ["Infectious", "Hematologic"],
        "exams": ["Enrichment"],
        "exam_fit": "延伸阅读：服务生物学/病理生理直觉；NMAT 考纲是导论课不是临床诊疗；MCAT 可迁移机制，不考指南级用药方案。",
        "pathogen": "Dengue virus（黄病毒科，+ssRNA）；血清型 DENV-1–4",
        "transmission": "Aedes aegypti（白天叮咬）；人—蚊—人周期。",
        "pathophysiology": [
            "感染内皮与免疫细胞，引发细胞因子风暴样反应。",
            "二次感染异型血清型时，ADE（抗体依赖性增强）可加重。",
            "血管通透性↑ → 血浆渗漏 → 休克（DSS）与出血风险。",
        ],
        "clinical": [
            "突发性高热、剧烈头痛、眶后痛、肌骨痛（breakbone fever）。",
            "皮疹、血小板↓、白细胞↓。",
            "危险期常在退热后：腹痛、持续呕吐、黏膜出血、血细胞比容↑。",
        ],
        "diagnosis": [
            "NS1 抗原（早期）、IgM/IgG、PCR。",
            "监测：血小板、Hct、生命体征与出入量。",
        ],
        "treatment": [
            "支持治疗为主：谨慎补液，避免 NSAIDs（出血风险）。",
            "识别血浆渗漏窗口，按严重登革热液体管理。",
            "无特异抗病毒一线药物作为常规考点。",
        ],
        "high_yield": [
            "退热后反而要警惕重症——这是经典陷阱题。",
            "ADE：非中和抗体促进病毒进入 Fc 受体细胞。",
            "与基孔肯雅/寨卡鉴别：血小板显著↓更支持登革。",
            "媒介控制 = 清除积水容器（菲律宾社区考点）。",
        ],
        "mcat_bridge": "病毒结构、媒介传播、体液免疫与 ADE 机制。",
        "nmat_bridge": "热带医学与公共卫生；实验室指标与危险征象识别。",
    },
    "type-2-diabetes": {
        "slug": "type-2-diabetes",
        "name": "Type 2 Diabetes Mellitus",
        "name_zh": "2型糖尿病",
        "short": "胰岛素抵抗 + 相对胰岛素分泌不足；代谢综合征核心疾病，NMAT/MCAT 双高频。",
        "systems": ["Endocrine", "Metabolic"],
        "exams": ["Enrichment"],
        "exam_fit": "延伸阅读：服务生物学/病理生理直觉；NMAT 考纲是导论课不是临床诊疗；MCAT 可迁移机制，不考指南级用药方案。",
        "pathogen": "非传染性；遗传易感 + 环境（肥胖、久坐、饮食）",
        "transmission": "不适用（非传染）。家族聚集与生活方式相关。",
        "pathophysiology": [
            "脂肪/肌肉对胰岛素不敏感 → 代偿性高胰岛素血症。",
            "β 细胞逐渐失代偿 → 高血糖。",
            "慢性高糖：AGE、氧化应激、微血管与大血管损伤。",
        ],
        "clinical": [
            "多饮、多尿、多食、疲乏；常隐匿起病。",
            "并发症：视网膜病、肾病、神经病变、ASCVD、足溃疡。",
            "急性：HHS（高渗高糖状态）多于 DKA（DKA 更偏 1 型）。",
        ],
        "diagnosis": [
            "空腹血糖 ≥126 mg/dL，或 HbA1c ≥6.5%，或 OGTT 2h ≥200（标准阈值需记牢）。",
            "症状 + 随机血糖 ≥200 亦可诊断。",
        ],
        "treatment": [
            "生活方式是基石；一线口服常考二甲双胍（减少肝糖输出）。",
            "其他：SGLT2i、GLP-1 RA、胰岛素（进展期）。",
            "控压控脂、筛查眼底与尿白蛋白。",
        ],
        "high_yield": [
            "胰岛素抵抗 vs 1 型绝对缺乏——机制题常考。",
            "二甲双胍：GI 副作用；乳酸酸中毒罕见但经典关联。",
            "HbA1c 反映约 2–3 个月平均血糖。",
            "MCAT：信号转导（胰岛素受体酪氨酸激酶）常串联。",
        ],
        "mcat_bridge": "激素信号、代谢通路、反馈调节与慢性病流行病学。",
        "nmat_bridge": "内分泌生理、诊断阈值与一线药物机制。",
    },
    "hypertension": {
        "slug": "hypertension",
        "name": "Essential Hypertension",
        "name_zh": "原发性高血压",
        "short": "多数高血压无单一病因；心脑血管事件的核心可改变危险因素。",
        "systems": ["Cardiovascular", "Renal"],
        "exams": ["Enrichment"],
        "exam_fit": "延伸阅读：服务生物学/病理生理直觉；NMAT 考纲是导论课不是临床诊疗；MCAT 可迁移机制，不考指南级用药方案。",
        "pathogen": "多因素：遗传、盐敏感、交感张力、RAAS、血管硬化",
        "transmission": "不适用。",
        "pathophysiology": [
            "心输出量与外周阻力失衡；长期导致血管重构。",
            "RAAS：肾素 → 血管紧张素 II → 醛固酮 → 保钠与血管收缩。",
            "靶器官：心（LVH）、脑、肾、视网膜、血管。",
        ],
        "clinical": [
            "多数无症状（silent）；头痛并非可靠标志。",
            "急症：极高血压伴急性靶器官损害（脑病、ACS、肺水肿等）。",
            "长期：卒中、心衰、CKD、PAD。",
        ],
        "diagnosis": [
            "重复、规范测量；诊室与动态血压相互印证。",
            "继发性线索：年轻起病、低钾、腹部杂音、阵发三联征等。",
        ],
        "treatment": [
            "限盐、减重、运动、限酒。",
            "一线药类：ACEI/ARB、CCB、噻嗪类利尿剂（个体化）。",
            "合并糖尿病/CKD 常优先 ACEI/ARB（考点）。",
        ],
        "high_yield": [
            "BP = CO × TPR——公式级理解题。",
            "ACEI：干咳、高钾、血管性水肿；妊娠禁忌。",
            "原发性占绝大多数；先想常见，再筛继发。",
            "MCAT：稳态、负反馈与内分泌轴。",
        ],
        "mcat_bridge": "循环生理、激素调节与稳态。",
        "nmat_bridge": "心血管药理与靶器官损害路径。",
    },
    "pneumonia": {
        "slug": "pneumonia",
        "name": "Community-Acquired Pneumonia",
        "name_zh": "社区获得性肺炎",
        "short": "肺泡感染导致渗出与气体交换障碍；病原谱与经验性治疗是高频考点。",
        "systems": ["Respiratory", "Infectious"],
        "exams": ["Enrichment"],
        "exam_fit": "延伸阅读：服务生物学/病理生理直觉；NMAT 考纲是导论课不是临床诊疗；MCAT 可迁移机制，不考指南级用药方案。",
        "pathogen": "常见：Streptococcus pneumoniae；非典型：Mycoplasma、Chlamydia、Legionella",
        "transmission": "吸入口咽定植菌或飞沫；宿主防御下降时发病。",
        "pathophysiology": [
            "病原到达远端气道 → 炎症渗出填充肺泡。",
            "V/Q 失调与分流 → 低氧血症。",
            "大叶性 vs 支气管肺炎病理模式常考。",
        ],
        "clinical": [
            "发热、咳痰、呼吸困难、胸痛；听诊湿啰音/实变征。",
            "肺炎链球菌：突发寒战、铁锈色痰（经典描述）。",
            "老年可表现不典型（意识改变、低热）。",
        ],
        "diagnosis": [
            "临床 + 胸片浸润影。",
            "必要时痰培养、血培养、尿抗原（肺炎链球菌/军团菌）。",
            "CURB-65 等用于严重度分层（记忆框架即可）。",
        ],
        "treatment": [
            "经验性覆盖典型 ± 非典型（地区指南导向）。",
            "氧疗、补液、退热支持。",
            "疫苗：肺炎链球菌、流感疫苗降低风险。",
        ],
        "high_yield": [
            "肺炎链球菌 = 最常见细菌性 CAP。",
            "Mycoplasma：年轻、干咳、肺外表现；无细胞壁→β-内酰胺无效。",
            "Legionella：水系统暴露、低钠、消化道症状。",
            "实变 = 支气管音、触觉语颤增强。",
        ],
        "mcat_bridge": "气体交换、炎症与免疫系统应答。",
        "nmat_bridge": "呼吸病理与经验性抗微生物思路。",
    },
    "asthma": {
        "slug": "asthma",
        "name": "Asthma",
        "name_zh": "哮喘",
        "short": "可逆性气道阻塞 + 高反应性 + 慢性炎症；I 型超敏与 Th2 通路是机制核心。",
        "systems": ["Respiratory", "Immunologic"],
        "exams": ["Enrichment"],
        "exam_fit": "延伸阅读：服务生物学/病理生理直觉；NMAT 考纲是导论课不是临床诊疗；MCAT 可迁移机制，不考指南级用药方案。",
        "pathogen": "非传染；过敏原、感染、运动、冷空气等触发",
        "transmission": "不适用。",
        "pathophysiology": [
            "Th2：IL-4/IL-5/IL-13 → IgE、嗜酸粒细胞、黏液高分泌。",
            "早期：支气管痉挛；晚期：炎症细胞浸润。",
            "长期：气道重构（基底膜增厚、平滑肌增生）。",
        ],
        "clinical": [
            "发作性喘息、气短、胸闷、干咳；夜间/清晨加重。",
            "呼气性哮鸣音；使用辅助呼吸肌。",
            "危重时可出现沉默肺（近乎无哮鸣）——危险信号。",
        ],
        "diagnosis": [
            "肺功能：可逆性 FEV1 改善（支气管舒张试验）。",
            "峰值流速变异；过敏评估按需。",
        ],
        "treatment": [
            "缓解：短效 β2 激动剂（SABA）。",
            "控制：吸入糖皮质激素（ICS）是抗炎基石；可加 LABA。",
            "重度：全身激素、镁剂、升级治疗（生物制剂了解即可）。",
        ],
        "high_yield": [
            "I 型超敏 = IgE + 肥大细胞脱颗粒。",
            "ICS 依从性差是失控常见原因。",
            "阿司匹林敏感型哮喘 ↔ 鼻息肉（Samter）三联征了解。",
            "与 COPD：可逆性与发病年龄/吸烟史是鉴别主轴。",
        ],
        "mcat_bridge": "超敏反应分型、呼吸系统力学（阻力↑）。",
        "nmat_bridge": "免疫病理与吸入治疗阶梯。",
    },
    "myocardial-infarction": {
        "slug": "myocardial-infarction",
        "name": "Myocardial Infarction",
        "name_zh": "心肌梗死",
        "short": "冠脉急性闭塞导致心肌坏死；缺血时间与再灌注是生死线。",
        "systems": ["Cardiovascular"],
        "exams": ["Enrichment"],
        "exam_fit": "延伸阅读：服务生物学/病理生理直觉；NMAT 考纲是导论课不是临床诊疗；MCAT 可迁移机制，不考指南级用药方案。",
        "pathogen": "多数为动脉粥样硬化斑块破裂 + 血栓",
        "transmission": "不适用。危险因素：吸烟、高血压、糖尿病、血脂异常、家族史。",
        "pathophysiology": [
            "氧供需失衡 → 缺血 → 损伤 → 坏死（时间依赖）。",
            "STEMI：透壁性损伤，ST 抬高；NSTEMI：心内膜下为主。",
            "坏死标志物：Troponin（高敏）最关键。",
        ],
        "clinical": [
            "压榨性胸痛，可放射至左臂/下颌；冷汗、恶心。",
            "女性、糖尿病、老年：症状可不典型。",
            "并发症：心律失常、心衰、室壁瘤、机械并发症（时间窗记忆）。",
        ],
        "diagnosis": [
            "ECG + 肌钙蛋白 + 临床表现。",
            "STEMI：紧急再灌注指征识别。",
        ],
        "treatment": [
            "MONA-BASH 等记忆框架了解；核心是抗血小板、抗凝、再灌注。",
            "STEMI：PCI 优先；无条件时溶栓。",
            "二级预防：他汀、双抗、β阻滞剂、ACEI、生活方式。",
        ],
        "high_yield": [
            "时间就是心肌：door-to-balloon 概念。",
            "Troponin 比 CK-MB 更特异/敏感（现代考点）。",
            "左前降支闭塞常累及前壁。",
            "MCAT：有氧代谢中断 → 乳酸、ATP 衰竭、膜泵失效。",
        ],
        "mcat_bridge": "细胞呼吸、膜电位与循环解剖。",
        "nmat_bridge": "急性冠脉综合征分型与急救优先级。",
    },
    "acute-kidney-injury": {
        "slug": "acute-kidney-injury",
        "name": "Acute Kidney Injury",
        "name_zh": "急性肾损伤",
        "short": "数小时至数日内肾功能骤降；先分清肾前/肾性/肾后，再谈机制题。",
        "systems": ["Renal"],
        "exams": ["Enrichment"],
        "exam_fit": "延伸阅读：服务生物学/病理生理直觉；NMAT 考纲是导论课不是临床诊疗；MCAT 可迁移机制，不考指南级用药方案。",
        "pathogen": "病因分类：灌注不足、实质损伤、梗阻",
        "transmission": "不适用。",
        "pathophysiology": [
            "肾前性：有效血容量↓ → GFR↓（肾结构初期可逆）。",
            "急性肾小管坏死（ATN）：缺血/毒物；管型尿常见。",
            "肾后性：尿路梗阻 → 压力传导损伤肾单位。",
        ],
        "clinical": [
            "少尿或非少尿；乏力、恶心、水肿、高血压。",
            "高钾、代谢性酸中毒、容量过负荷、尿毒症症状。",
            "药物史（NSAID、氨基糖苷、造影剂）很关键。",
        ],
        "diagnosis": [
            "肌酐急性上升、尿量变化。",
            "FeNa/FeUrea、尿检、超声排除梗阻。",
            "肾前 vs ATN：尿钠、浓缩能力差异是经典比较题。",
        ],
        "treatment": [
            "纠正病因与灌注；停肾毒性药。",
            "处理并发症：高钾、酸中毒、肺水肿。",
            "透析指征：AEIOU 记忆（酸中毒、电解质、中毒、过负荷、尿毒症）。",
        ],
        "high_yield": [
            "先定位：pre-renal / intrinsic / post-renal。",
            "泥沙色颗粒管型 ↔ ATN。",
            "ACEI + NSAID + 利尿剂可促成血流动力学性 AKI。",
            "MCAT：滤过、重吸收与稳态（钾/酸碱）。",
        ],
        "mcat_bridge": "肾脏生理与体液电解质平衡。",
        "nmat_bridge": "临床分类思维与急症处理优先级。",
    },
}


def all_diseases() -> list[dict]:
    try:
        from knowledge.models import DiseaseArticle

        rows = [d.as_dict() for d in DiseaseArticle.objects.all()]
        if rows:
            return sorted(rows, key=lambda d: (d.get("name") or "").lower())
    except Exception:
        pass
    return sorted(DISEASES.values(), key=lambda d: d["name"].lower())


def get_disease(slug: str) -> dict | None:
    try:
        from knowledge.models import DiseaseArticle

        row = DiseaseArticle.objects.filter(slug=slug).first()
        if row:
            return row.as_dict()
    except Exception:
        pass
    return DISEASES.get(slug)
