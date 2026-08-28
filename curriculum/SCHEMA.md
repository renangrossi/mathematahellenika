# Curriculum data schema (v1)

Single source of truth for lesson content. Each lesson is one JSON file
at `curriculum/{level-code-lowercase}/{lesson-id}.json` (e.g.
`curriculum/iv/aoristus-activus.json` for a Gradus IV lesson — the
directory uses the level's short code lowercased, `i`..`vii`, matching
the `{code}-` prefix every lesson id already carries; it is NOT the
Gradus slug used for URLs, e.g. `media`, which only appears under
`gradus/`). `curriculum/index.json` lists every Gradus's units and the
lesson ids that belong to each, in order, with prerequisites — this is
what lets a level page, the search index, and the exercise-items index
all be generated instead of hand-maintained.

Adapted from the sibling Latin-course project's `curriculum/SCHEMA.md`
(same shape, same build pipeline, itself adapted from the English
course's) — `level` values are this course's seven Latin-named Gradus
short codes (`I`..`VII`, see `scripts/site_chrome.py`'s `LEVELS` — the
same seven names as the Latin course's own, see
`docs/gradus-mapping.md` for why), and `exercises` items use the exact
schema `assets/js/exercises.js` reads (same engine, extended — see that
file's own header comment — with Greek-specific answer grading).

## Object language vs. metalanguage (read this before writing a lesson)

This course teaches **Ancient Greek** (Classical Attic as the core, with
notes on Homeric/Koine forms where pedagogically useful) **through
Latin** as the metalanguage, per the project's pedagogical-language
policy. Concretely, inside every field below:

- `title`, `subtitle`, `intro`, `explanation`, `rules[].heading`,
  `rules[].body`, `commonMistakes[].why`, `summary`, and every exercise
  `instructions`/`explanation` are written in clear Latin (with Greek
  technical terms left in Greek script where that is the normal
  scholarly convention, e.g. "τὸ ῥῆμα" alongside "verbum"). English is
  used only as a short parenthetical gloss where Latin alone would
  leave a genuine beginner guessing — see any Gradus I lesson.
- `examples`, exercise prompts' Greek material, and any `answer`/
  `answers` keys that are Greek words are written in **polytonic Greek**
  (breathings, accents, iota subscript) — Unicode NFC, not transliterated
  — since correct accentuation is itself part of what Gradus I teaches.
  See `docs/fonts-and-input.md` for the type stack and input-method notes
  this depends on.

## Lesson JSON shape

```jsonc
{
  "id": "i-spiritus-et-accentus",         // matches the generated filename
  "level": "I",                           // I | II | III | IV | V | VI | VII
  "unit": "1",              // curriculum/index.json unit number this belongs to
  "order": 4,                // position within the unit
  "skill": "grammatica",     // grammatica | vocabularium | pronuntiatio | lectio
                              // | auditio | scriptio | locutio | functionale
  "strand": "spiritus",       // free-text grouping used for prerequisite/related lookups
  "title": "Spiritus et Accentus",
  "subtitle": "Spiritus lenis et asper, tres accentus (acutus, gravis, circumflexus), et regulae fundamentales positionis eorum.",
  "prerequisites": ["i-alphabetum-et-phonologia"],   // lesson ids; [] if none
  "objectives": [
    "Distinguere spiritum lenem (᾿) a spiritu aspero (῾) et eos recte pronuntiare",
    "..."
  ],
  "content": {
    "intro": "One short paragraph, Latin (English gloss only where truly needed at Gradus I).",
    "explanation": "<p>...</p>",     // may contain inline HTML (strong/em), no block tags
    "rules": [ { "heading": "a) Spiritus", "body": "<p>...</p>" }, ... ],
    "examples": ["ὁ ἄνθρωπος — homo.", "..."],
    "commonMistakes": [
      { "wrong": "...", "right": "...", "why": "..." }
    ]
  },
  "exercises": [ /* verbatim assets/js/exercises.js exercise-data objects */ ],
  "summary": ["One-line takeaway", "..."],
  "related": [ { "lessonId": "i-alphabetum-et-phonologia", "label": "Alphabetum et Phonologia" } ]
}
```

### Correct-answer keys: Latin words vs. Greek words

Correct-answer keys inside `exercises` (`answer`/`answers`/pair `right`
values, `words` for ordering, `answerIndex`'s corresponding `options`
entry) follow **two different conventions depending on which language
the answer is in**, both implemented in `assets/js/exercises.js`'s
`norm()`:

- A **Latin** metalanguage word in an answer key is written WITHOUT
  macrons, even when the prompt/explanation uses them for pedagogy —
  macrons are a typing burden the grading should never impose. (Same
  convention as the Latin sibling course; norm() never strips macrons
  because Latin answer keys simply never contain them.)
- A **Greek** word in an answer key SHOULD be written WITH full,
  correct polytonic accentuation (breathings, accents, iota subscript)
  — do not pre-strip it "to make grading easier". `norm()` strips Greek
  diacritics from BOTH the key and the student's typed answer before
  comparing (and folds final ς to medial σ), so a student who types
  unaccented Greek is graded fairly without the lesson author ever
  having to maintain an unaccented duplicate of every answer.

## `curriculum/index.json` shape

```jsonc
{
  "levels": {
    "I": {
      "units": [
        {
          "id": "1",
          "title": "Fundamenta: Alphabetum, Phonologia, et Prima Verba",
          "lessons": [
            { "id": "i-alphabetum-et-phonologia", "status": "published" },
            { "id": "i-vocales-diphthongi-et-longitudo", "status": "planned" }
          ]
        }
      ]
    }
  }
}
```

`status` on a lesson entry is `"published"` (generated HTML exists and
is linked from its Gradus page), `"drafted"` (JSON exists, not yet
built), or `"planned"` (identified in the course plan, no JSON yet —
used so a Gradus's full intended shape is documented honestly even
before most of it is written; see `scripts/build_level_page.py`'s
placeholder-page behavior for a Gradus with zero published lessons).

## Build

`python3 scripts/build_lesson.py curriculum/{level}/{lesson-id}.json`
renders one lesson to `gradus/{level}/{lesson-id}.html`, reusing the
shared header/footer markup (via `scripts/site_chrome.py`).

`python3 scripts/build_nav_map.py` regenerates
`scripts/lesson_nav_map.json` (Previous/Next + Test-Yourself-anchor
data) from `curriculum/index.json` — run it after adding/reordering
lessons, before rebuilding pages.

`python3 scripts/build_level_page.py {LEVEL|--all}` regenerates a
Gradus's overview + Te Ipsum Proba pages (or an honest placeholder page
if nothing is published yet for that Gradus — see its own docstring).

`python3 scripts/build_exercise_index.py` regenerates
`assets/data/exercise-items-index.json` (for a future spaced-repetition
review page) and `assets/data/search-index.json` (used by the site
search) from every built page — run it last, after all pages for a
batch are built.
