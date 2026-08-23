"""Curriculum-aware study helpers for the Gabay tutor."""

from __future__ import annotations

from . import exams


def build_curriculum_context(
    *,
    exam: str = "",
    subject_slug: str = "",
    section_slug: str = "",
    chapter_title: str = "",
) -> str:
    """Return a compact curriculum brief the model must stay inside."""
    chunks: list[str] = []
    exam = (exam or "").upper().strip()
    subject_slug = (subject_slug or "").strip()
    section_slug = (section_slug or "").strip()
    chapter_title = (chapter_title or "").strip()

    shared = exams.get_shared(subject_slug) if subject_slug else None
    unique = exams.get_nmat_unique(subject_slug) if subject_slug else None
    section = exams.get_mcat_section(section_slug) if section_slug else None

    if shared:
        chunks.append(f"共用科目：{shared['name']}（{shared['name_zh']}）")
        chunks.append(f"定位：{shared['summary']}")
        for group in shared.get("chapters", []):
            chunks.append(f"[{group['heading']}]")
            for item in group["items"]:
                mark = " ← 当前章节" if chapter_title and chapter_title == item["title"] else ""
                points = "；".join(item.get("points") or [])
                chunks.append(f"- {item['title']}{mark}: {points}")

    if unique:
        chunks.append(f"NMAT Part 1 独有科：{unique['name']}（{unique['name_zh']}）")
        chunks.append(f"定位：{unique['focus']}")
        for group in unique.get("chapters", []):
            chunks.append(f"[{group['heading']}]")
            for item in group["items"]:
                mark = " ← 当前章节" if chapter_title and chapter_title == item["title"] else ""
                points = "；".join(item.get("points") or [])
                chunks.append(f"- {item['title']}{mark}: {points}")

    if section:
        chunks.append(f"MCAT 科目：{section['short']} — {section['name']}")
        chunks.append(f"定位：{section['focus']}")
        for group in section.get("chapters", []):
            chunks.append(f"[{group['heading']}]")
            for item in group["items"]:
                mark = " ← 当前章节" if chapter_title and chapter_title == item["title"] else ""
                points = "；".join(item.get("points") or [])
                chunks.append(f"- {item['title']}{mark}: {points}")

    if not chunks:
        chunks.append("通用 NMAT / MCAT 备考辅导。优先依据 Gabay 站点已列出的科目章节。")

    return "\n".join(chunks)


SYSTEM_PROMPT = """你是 Gabay 备考教练，服务用户同时准备菲律宾 NMAT（CEM）与北美 MCAT（AAMC）。
规则：
1. 紧扣用户当前科目/章节大纲作答；超出大纲时明确说“超纲”，并把它映射回最近的官方章节。
2. 区分考试：NMAT Part 2 是大学导论深度；MCAT 是篇章推理 + 基础科学；不要把临床指南级细节当成 NMAT 必考。
3. 讲解先给直觉，再给机制，最后给易错点；默认用中文，专有名词保留英文。
4. 出题时一次只出一题，等待用户作答；用户作答后再给解析。
5. 不要编造 CEM/AAMC 不存在的“官方百分比”或假考点；不确定就说不确定。
6. 回答简洁、可执行，适合刷题间隙阅读。"""


def tutor_messages(
    *,
    mode: str,
    user_text: str,
    curriculum: str,
    chapter_title: str = "",
) -> list[dict]:
    mode = (mode or "ask").lower()
    chapter_line = f"当前章节：{chapter_title}" if chapter_title else "当前章节：未指定（按整科辅导）"

    if mode == "explain":
        task = (
            "请讲解当前章节：先 3–5 条核心概念，再给一个迷你例子，最后给 2 个易错点。"
            "不要出题。"
        )
    elif mode == "quiz":
        task = (
            "请出一道贴合当前章节的单选题（A–D）。"
            "只输出：题干、四个选项、并在最后一行写“请选择 A/B/C/D”。"
            "不要在同一条消息里公布答案。"
        )
    elif mode == "grade":
        task = (
            "用户正在回答上一道练习题。请判断对错，给出正确选项与简短解析，"
            "并指出对应到大纲中的哪个知识点。"
        )
    else:
        task = "回答用户关于当前科目/章节的问题，必要时用类比。"

    user_payload = (
        f"{chapter_line}\n\n"
        f"【Gabay 大纲】\n{curriculum}\n\n"
        f"【任务】\n{task}\n\n"
        f"【用户输入】\n{user_text.strip() or '（无额外输入）'}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_payload},
    ]
