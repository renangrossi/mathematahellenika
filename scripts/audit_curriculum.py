#!/usr/bin/env python3
"""
Audit every curriculum/{level}/*.json lesson for how "Natural Method"
(comprehensible-input-first) vs. "grammar-first" it is, and how much it
draws on the course's recurring cast of characters.

Ported from the sibling Latin course's scripts/audit_curriculum.py --
identical heuristic/scoring logic, only the recurring-cast name list is
Greek-specific (see CAST_RE below). See that script's own header
comment for the full methodology explanation; it applies unchanged here.

Usage:
    python3 scripts/audit_curriculum.py            # summary to stdout
    python3 scripts/audit_curriculum.py --csv out.csv   # + full per-lesson CSV
"""
import argparse
import csv
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

GRAMMAR_TERMS = [
    "indicativus", "coniunctivus", "optativus", "imperativus", "nominativus",
    "genetivus", "genitivus", "dativus", "accusativus", "vocativus",
    "aoristus", "perfectum", "imperfectum", "praesens", "futurum",
    "activus", "medius", "passivus", "singularis", "pluralis", "dualis",
    "masculinum", "femininum", "neutrum", "declinatio", "coniugatio",
    "participium", "infinitivus", "modus", "tempus", "casus",
]

# This course's recurring cast (see gradus/fundamenta/lectio-prima.html and
# its sibling dialogue lessons), plus Socrates as the recurring historical
# figure later authentic-text lessons draw on. Macron-insensitive is not
# meaningful for polytonic Greek names, so these are matched literally.
CAST_RE = re.compile(r"(Ἀγάθων|Μελίτη|Σωκράτης|Ξανθίππη|Περικλῆς|Δημοσθένης)")

IDENTIFY_PATTERNS = [
    re.compile(r"\best[:：]", re.I),
    re.compile(r"identific[a-z]*", re.I),
    re.compile(r"quod (tempus|modus|casus|genus)", re.I),
    re.compile(r"quis modus", re.I),
    re.compile(r"decline|dēclīnā", re.I),
    re.compile(r"coniuga|coniūgā", re.I),
    re.compile(r"est cl[aā]usula", re.I),
]


def classify(d):
    content = d.get("content", {})
    intro = content.get("intro", "") or ""
    explanation = content.get("explanation", "") or ""
    rules = content.get("rules", []) or []
    exercises = d.get("exercises", []) or []

    ex_types = [e.get("type") for e in exercises]
    has_rc = "reading-comprehension" in ex_types
    has_match = "matching" in ex_types
    has_tf = "true-false" in ex_types
    has_typing_selfcheck = any(
        e.get("type") == "typing" and any(not it.get("answer") for it in e.get("items", []))
        for e in exercises
    )
    meaning_block_count = sum(1 for t in ex_types if t in ("reading-comprehension", "matching", "true-false"))

    total_items = 0
    identify_items = 0
    for e in exercises:
        items = e.get("items", []) or []
        total_items += len(items)
        for it in items:
            text = " ".join(str(it.get(k, "")) for k in ("prompt", "statement")) + " " + " ".join(it.get("options", []) or [])
            if any(pat.search(text) for pat in IDENTIFY_PATTERNS):
                identify_items += 1
            else:
                opts = [o.lower() for o in (it.get("options") or [])]
                if opts and sum(1 for o in opts if any(gt in o for gt in GRAMMAR_TERMS)) >= max(1, len(opts) - 1):
                    identify_items += 1

    identify_ratio = identify_items / total_items if total_items else 0

    combined_text = intro + " " + explanation + " " + " ".join(r.get("body", "") for r in rules)
    passage_text = "".join(e.get("passage", "") or "" for e in exercises)
    has_character = bool(CAST_RE.search(combined_text) or CAST_RE.search(passage_text))
    narrative_paras = explanation.count("<p>")

    score = 0
    score += 2 if has_rc else 0
    score += 1 if has_match else 0
    score += 1 if has_tf else 0
    score += 1 if has_typing_selfcheck else 0
    score += 1 if has_character else 0
    score += 1 if narrative_paras >= 2 else 0
    score -= 2 if identify_ratio >= 0.6 else (1 if identify_ratio >= 0.35 else 0)
    score -= 1 if len(rules) >= 4 and not has_character else 0
    score -= 1 if meaning_block_count == 0 else 0

    classification = "A" if score >= 3 else ("B" if score >= 0 else "C")

    return {
        "id": d.get("id"), "level": d.get("level"), "title": d.get("title"),
        "skill": d.get("skill"), "n_exercises": len(exercises), "n_items": total_items,
        "identify_items": identify_items, "identify_ratio": round(identify_ratio, 2),
        "has_reading_comprehension": has_rc, "has_matching": has_match,
        "has_true_false": has_tf, "has_typing_selfcheck": has_typing_selfcheck,
        "has_character": has_character, "n_rules": len(rules),
        "narrative_paras": narrative_paras, "score": score,
        "classification": classification,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="write full per-lesson results to this CSV path")
    args = ap.parse_args()

    idx = json.loads((REPO_ROOT / "curriculum" / "index.json").read_text())
    order_map = {}
    for level, info in idx["levels"].items():
        pos = 0
        for u in info["units"]:
            for l in u["lessons"]:
                order_map[l["id"]] = pos
                pos += 1

    rows = []
    for path in sorted(glob.glob(str(REPO_ROOT / "curriculum" / "*" / "*.json"))):
        p = Path(path)
        if p.name == "index.json":
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        row = classify(d)
        row["path"] = str(p.relative_to(REPO_ROOT))
        rows.append(row)
    rows.sort(key=lambda r: (r["level"], order_map.get(r["id"], 999)))

    by_class = Counter(r["classification"] for r in rows)
    by_level_class = Counter((r["level"], r["classification"]) for r in rows)

    print(f"TOTAL LESSONS: {len(rows)}")
    print(f"Overall: A={by_class['A']}  B={by_class['B']}  C={by_class['C']}")
    print(f"{'Level':<6}{'A':>4}{'B':>4}{'C':>4}")
    for level in ["I", "II", "III", "IV", "V", "VI", "VII"]:
        print(f"{level:<6}{by_level_class.get((level,'A'),0):>4}{by_level_class.get((level,'B'),0):>4}{by_level_class.get((level,'C'),0):>4}")

    no_char = sum(1 for r in rows if not r["has_character"])
    print(f"\nLessons with zero recurring-cast mentions: {no_char}/{len(rows)}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\nFull per-lesson CSV -> {args.csv}")


if __name__ == "__main__":
    main()
