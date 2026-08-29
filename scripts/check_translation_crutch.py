#!/usr/bin/env python3
"""
Regression test: catch the "Greek answer choice silently carries its own
Latin/English translation" anti-pattern across every exercise item in the
curriculum -- the bug class reported and fixed on 2026-08-29 (a Greek
option like "discipulus sum (μαθητής)" or "χαῖρε (Salvē)" hands the
learner the answer key instead of requiring them to understand the Greek).

WHY THIS SCRIPT EXISTS, SPECIFICALLY: an earlier ad hoc audit for this
same bug filtered `if ex['type'] not in ('fill-blank', 'multiple-choice')`
and so never inspected `reading-comprehension` items -- even though those
render through the exact same choice-button UI in exercises.js. That is
where nearly all of the real violations were living. This script
deliberately checks EVERY exercise type's `options`/`pairs` fields with
no type-based exclusion, precisely so that mistake cannot recur silently.

This is a source-level (curriculum JSON) check, not a rendered-DOM check.
That is a deliberate choice, not a shortcut: the HTML is generated
deterministically from this JSON by build_lesson.py with no template-side
translation/gloss logic anywhere in the pipeline (verified by hand when
this script was written -- see the guide's "verified against rendered
DOM" note). Catching the bug here is equivalent to catching it in the
DOM for as long as that remains true. If build_lesson.py or exercises.js
is ever changed to inject any answer-choice text itself, re-verify that
invariant (grep build_lesson.py / assets/js/exercises.js for any string
formatting of `options`/`pairs`/`prompt`) and prefer re-running an actual
Playwright DOM check (render each touched page, read
`.exercise-block` option/choice text) as the authoritative check --
"the JSON has no violations" is necessary but was previously mistaken
for sufficient; it only actually is sufficient if this invariant holds.

USAGE:
    python3 scripts/check_translation_crutch.py                # scan everything, human report
    python3 scripts/check_translation_crutch.py --csv out.csv   # also write a CSV report
    python3 scripts/check_translation_crutch.py --strict        # exit 1 if any violation found (for CI/pre-commit use)

WHAT COUNTS AS A VIOLATION: an `options` (multiple-choice/fill-blank/
reading-comprehension) or `pairs[].left`/`pairs[].right` (matching)
string where Greek-script text appears outside a `(...)` parenthetical
and Latin/English text appears inside one attached to it, OR the
reverse (Latin/English outside, Greek quoted inside parens) -- i.e. the
same string carries both languages, one dressed as a gloss of the other.

WHAT DOES NOT COUNT (deliberately not flagged): exercises whose entire
declared purpose is translation practice -- this course's own
"Iunge Graecum cum Latino" / similarly-titled matching blocks -- are
exempted by title (see TRANSLATION_EXERCISE_TITLE_MARKERS below). If a
future lesson adds a genuine translation exercise under a different
title, add its marker there rather than editing around this script.
"""
import argparse
import csv
import glob
import json
import re
import sys

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
PAREN_RE = re.compile(r"\(([^)]*)\)")

# Exercise titles that are deliberately, honestly framed as translation
# exercises -- Greek<->Latin pairing is the whole point, so it is not a
# "crutch" there. Matched case-insensitively as a substring.
TRANSLATION_EXERCISE_TITLE_MARKERS = [
    "iunge graecum cum lat",  # "Iunge Graecum cum Latino"
]


def is_translation_exercise(ex):
    title = (ex.get("title") or "").lower()
    return any(marker in title for marker in TRANSLATION_EXERCISE_TITLE_MARKERS)


EXAMPLE_MARKER_RE = re.compile(r"\b(ut|vel|aut)\s", re.IGNORECASE)


def string_mixes_languages(s):
    """True if `s` has Greek outside parens + non-Greek inside (a gloss
    attached to a Greek answer), or non-Greek outside + Greek inside
    parens (the same bug, direction-swapped).

    Deliberately NOT flagged (kept low-noise for legitimate consolidation-
    stage grammar prose, which cites Greek forms as *examples* of a
    category rather than *translating* a single word/phrase):
      - a parenthetical listing multiple comma-separated Greek forms
        (a citation of several exemplars, e.g. "forma enclitica (mou,
        moi, me)" -- not a translation of "forma enclitica")
      - a parenthetical introduced by "ut"/"vel"/"aut" right before it in
        the outside text (an explicit "such as" example marker)
    The bug signature this script exists to catch is a SINGLE Greek
    word/short phrase paired 1:1 with its own Latin/English translation,
    e.g. "chaire (Salve)" or "discipulus sum (mathetes)".
    """
    if not isinstance(s, str) or not s:
        return False
    parens = PAREN_RE.findall(s)
    if not parens:
        return False
    # Multiple exemplar forms in one parenthetical -> citation, not a gloss.
    if any("," in p for p in parens):
        return False
    outside = PAREN_RE.sub("", s)
    if EXAMPLE_MARKER_RE.search(outside):
        return False
    has_paren_greek = any(GREEK_RE.search(p) for p in parens)
    has_paren_other = any(not GREEK_RE.search(p) for p in parens)
    outside_has_greek = bool(GREEK_RE.search(outside))
    outside_has_other = bool(re.search(r"[A-Za-z]", outside))
    return (outside_has_greek and has_paren_other) or (
        outside_has_other and not outside_has_greek and has_paren_greek
    )


def scan_file(path):
    violations = []
    d = json.load(open(path, encoding="utf-8"))
    for ex in d.get("exercises", []):
        ex_id = ex.get("id", "?")
        ex_type = ex.get("type", "?")
        translation_ok = is_translation_exercise(ex)
        for it in ex.get("items", []):
            item_id = it.get("id", "?")
            for opt in it.get("options") or []:
                if string_mixes_languages(opt):
                    violations.append(
                        {
                            "file": path,
                            "lesson_id": d.get("id"),
                            "exercise_id": ex_id,
                            "exercise_type": ex_type,
                            "item_id": item_id,
                            "field": "options",
                            "text": opt,
                            "translation_exercise": translation_ok,
                        }
                    )
            for pair in it.get("pairs") or []:
                for side in ("left", "right"):
                    val = pair.get(side, "")
                    if string_mixes_languages(val):
                        violations.append(
                            {
                                "file": path,
                                "lesson_id": d.get("id"),
                                "exercise_id": ex_id,
                                "exercise_type": ex_type,
                                "item_id": item_id,
                                "field": f"pairs.{side}",
                                "text": val,
                                "translation_exercise": translation_ok,
                            }
                        )
    return violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="write full report to this CSV path")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 if any non-translation-exercise violation is found",
    )
    args = ap.parse_args()

    all_violations = []
    for path in sorted(glob.glob("curriculum/*/*.json")):
        all_violations.extend(scan_file(path))

    real = [v for v in all_violations if not v["translation_exercise"]]
    exempted = [v for v in all_violations if v["translation_exercise"]]

    print(f"Scanned curriculum/*/*.json")
    print(f"Violations (translation crutch, should be fixed): {len(real)}")
    print(f"Exempted (deliberate translation exercises, OK):  {len(exempted)}")
    print()
    if real:
        print("--- VIOLATIONS ---")
        for v in real:
            print(
                f"{v['file']} | {v['exercise_id']} ({v['exercise_type']}) | "
                f"{v['item_id']} | {v['field']} = {v['text']!r}"
            )

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "file",
                    "lesson_id",
                    "exercise_id",
                    "exercise_type",
                    "item_id",
                    "field",
                    "text",
                    "translation_exercise",
                ],
            )
            w.writeheader()
            for v in all_violations:
                w.writerow(v)
        print(f"\nFull report -> {args.csv}")

    if args.strict and real:
        sys.exit(1)


if __name__ == "__main__":
    main()
