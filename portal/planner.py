"""Deterministic study-plan generator.

Same inputs → byte-identical plan. Syllabus order follows each subject's
curated outline (pedagogical), filtered to the exam's blueprint blocks.
"""

from __future__ import annotations

import datetime as dt

from .content import chapters_store, exam_blueprint, get_subject


def syllabus(exam_id: str) -> list[dict]:
    """Ordered chapters for the exam: blueprint blocks → bank docs → subject
    outline order, deduped keeping first occurrence."""
    bp = exam_blueprint(exam_id)
    if not bp:
        return []
    ordered: list[str] = []
    seen: set[str] = set()
    chs = chapters_store()
    for block in bp.get("blocks") or []:
        for section_id in block.get("bank") or []:
            from .content import exam_bank_section
            bank_doc = exam_bank_section(exam_id, section_id) or {}
            subject_slug = bank_doc.get("subject") or section_id
            subject = get_subject(subject_slug)
            if not subject:
                continue
            for group in subject.get("chapters") or []:
                for cid in group.get("chapters") or []:
                    ch = chs.get(cid) or {}
                    exams = ch.get("exams") or []
                    if exams and exam_id.upper() not in exams:
                        continue
                    if cid not in seen:
                        seen.add(cid)
                        ordered.append(cid)
    return [{"chapter_id": cid, "discipline": (chs.get(cid) or {}).get("discipline", ""),
             "title": (chs.get(cid) or {}).get("title", cid),
             "notes": len((chs.get(cid) or {}).get("notes") or []),
             "practice": len((chs.get(cid) or {}).get("practice") or [])}
            for cid in ordered]


def task_minutes(entry: dict) -> int:
    read = min(45, 20 + 2 * entry.get("notes", 0))
    drill = 5 + 2 * entry.get("practice", 0)
    return read + drill


def build_plan(*, exam_id: str, exam_date: dt.date, weekly_hours: int,
               done: set[str], weak: set[str] | None = None,
               today: dt.date | None = None) -> list[dict]:
    weak = weak or set()
    today = today or dt.date.today()
    days = (exam_date - today).days
    if days <= 0:
        return []
    daily_minutes = max(30, int(weekly_hours * 60 / 7))
    tasks = syllabus(exam_id)
    plan: list[dict] = []
    # weak chapters (recently missed) get priority: front-load and double-tap
    if weak:
        weak_first = [t for t in tasks if t["chapter_id"] in weak and t["chapter_id"] not in done]
        rest = [t for t in tasks if t["chapter_id"] not in done and t["chapter_id"] not in weak]
        queue = weak_first + rest
    else:
        queue = [t for t in tasks if t["chapter_id"] not in done]
    qi = 0
    for offset in range(days):
        date = today + dt.timedelta(days=offset)
        day = {"date": date.isoformat(), "minutes": 0, "tasks": []}
        remaining_days = days - offset
        # mock cadence: every 14th day, then every 3rd day in the last 10 —
        # never on the eve of the exam (that day is rest)
        is_mock_day = ((offset > 0 and offset % 14 == 0 and remaining_days > 1)
                       or (1 < remaining_days <= 10 and remaining_days % 3 == 0))
        if remaining_days == 1:
            day["tasks"].append({"kind": "rest", "label": "Light review + early night",
                                 "url": "/review/", "minutes": 60, "chapter_id": ""})
            day["minutes"] += 60
            plan.append(day)
            continue
        if is_mock_day:
            day["tasks"].append({"kind": "mock", "label": f"Full-length {exam_id.upper()} mock exam",
                                 "url": f"/exams/{exam_id}/", "minutes": 240,
                                 "chapter_id": ""})
            day["minutes"] += 240
        budget = daily_minutes - day["minutes"]
        while budget >= 20 and qi < len(queue):
            entry = queue[qi]
            mins = task_minutes(entry)
            read_mins = min(45, 20 + 2 * entry["notes"])
            day["tasks"].append({"kind": "read", "label": f"Read: {entry['title']}",
                                 "url": f"/tutorials/{entry['discipline']}/{entry['chapter_id']}/",
                                 "minutes": read_mins, "chapter_id": entry["chapter_id"]})
            day["minutes"] += read_mins
            budget -= read_mins
            if entry["practice"] and budget >= 10:
                drill = 5 + 2 * entry["practice"]
                day["tasks"].append({"kind": "drill", "label": f"Drill: {entry['title']} practice",
                                     "url": f"/practice/{subject_slug_for(exam_id, entry['chapter_id'])}/",
                                     "minutes": drill, "chapter_id": entry["chapter_id"]})
                day["minutes"] += drill
                budget -= drill
            qi += 1
        if qi >= len(queue):
            # syllabus exhausted — mocks and the final rest day still get
            # scheduled even when everything is read, but re-reading the
            # whole queue from scratch made a finished plan never terminate
            queue = []
            qi = 0
        plan.append(day)
    return plan


def subject_slug_for(exam_id: str, chapter_id: str) -> str:
    chs = chapters_store()
    return (chs.get(chapter_id) or {}).get("discipline", "")
