#!/usr/bin/env python3
"""Audit tutorial chapters against the quantitative template benchmarks.

Usage: python3 scripts/audit_tutorials.py [discipline]  (default: all)
Exits 1 if any chapter FAILs.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
import yaml
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BENCH = {"secs": 4, "figs": 2, "mnem": 2, "maps": 2, "pq": 3, "rq": 4, "fr": 2, "kp": 6}

def audit(disc):
    tut_dir = REPO / "content" / "tutorials" / disc
    if not tut_dir.is_dir():
        return []
    results = []
    for f in sorted(tut_dir.glob("*.yml")):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        secs = len(d.get("sections") or [])
        figs = sum(len(s.get("figures") or []) for s in d.get("sections") or [])
        checks = sum(len(s.get("check") or []) for s in d.get("sections") or [])
        tables = sum(1 for s in d.get("sections") or [] if s.get("table"))
        mnem = len(d.get("mnemonics") or [])
        maps = len(d.get("maps") or [])
        pq = len((d.get("passage") or {}).get("questions") or [])
        rq = len(d.get("review_questions") or [])
        fr = len(d.get("further_reading") or [])
        ex = len(d.get("examples") or [])
        dx = sum(1 for e in d.get("examples") or [] if e.get("distractors"))
        kp = len(d.get("key_points") or [])
        fails = []
        if secs < BENCH["secs"]: fails.append(f"secs{secs}<{BENCH['secs']}")
        figs_on_disk = sum(1 for s in d.get("sections") or [] for fig in s.get("figures") or [] if (REPO / "content" / "images" / fig.get("src", "")).exists())
        if figs < BENCH["figs"] or figs_on_disk < BENCH["figs"]: fails.append(f"figs{figs_on_disk}disk/{figs}ref<{BENCH['figs']}")
        if checks < secs: fails.append(f"checks{checks}<{secs}")
        if mnem < BENCH["mnem"]: fails.append(f"mnem{mnem}<{BENCH['mnem']}")
        if maps < BENCH["maps"]: fails.append(f"maps{maps}<{BENCH['maps']}")
        if pq < BENCH["pq"]: fails.append(f"pq{pq}<{BENCH['pq']}")
        if rq < BENCH["rq"]: fails.append(f"rq{rq}<{BENCH['rq']}")
        if fr < BENCH["fr"]: fails.append(f"fr{fr}<{BENCH['fr']}")
        if ex < 1 or dx < ex: fails.append(f"ex{ex}/{dx}")
        if kp < BENCH["kp"]: fails.append(f"kp{kp}<{BENCH['kp']}")
        status = "PASS" if not fails else "FAIL:" + ",".join(fails)
        results.append((status, f.name, f"s={secs} f={figs} c={checks} t={tables} m={mnem} mp={maps} pq={pq} rq={rq} fr={fr} kp={kp}"))
    return results

if __name__ == "__main__":
    disc = sys.argv[1] if len(sys.argv) > 1 else None
    all_results = []
    base = REPO / "content" / "tutorials"
    discs = [disc] if disc else sorted(d.name for d in base.iterdir() if d.is_dir())
    failed = False
    for d in discs:
        for status, name, detail in audit(d):
            print(f"{status:6s} {d}/{name}  {detail}")
            if status != "PASS": failed = True
    sys.exit(1 if failed else 0)
