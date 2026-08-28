# Mathemata Hellenika — Schola Graecitatis Classicae

A free, static Ancient Greek course (Classical Attic core, with notes
on Homeric and Koine Greek where useful), taught **through Latin** as
the metalanguage — the historical European tradition of teaching Greek
through Latin. Sibling project to `course-latin` (Lectiones Latinae)
and `curso-ingles` (englishclasses), sharing their architecture,
visual language, exercise engine, and AI-teacher pattern.

## Status

Only **Gradus I** (of seven planned) has published lessons so far — 3
of its 9 planned lessons are written; the rest of Gradus I, and all of
Gradus II–VII, are documented as a planned outline in
`curriculum/index.json` but not yet built. See `docs/gradus-mapping.md`
for the full seven-Gradus plan and how it maps onto more familiar
references (CEFR, common textbooks).

## Layout

- `curriculum/` — single source of truth for lesson content (see
  `curriculum/SCHEMA.md`). One JSON file per lesson; `index.json`
  sequences every Gradus's units.
- `gradus/` — generated HTML (never hand-edit; rebuild from
  `curriculum/` instead — see Build below).
- `assets/` — shared CSS/JS/fonts/data, the exercise engine, and the
  gamification/mastery/search/dictionary-widget/AI-teacher frontend.
- `scripts/` — the Python build pipeline that turns `curriculum/*.json`
  into `gradus/**/*.html`, plus the hand-designed top-level pages
  (`build_static_pages.py`).
- `worker/` — a separate Cloudflare Worker (Magister AI's backend);
  see `worker/README.md` for deployment.
- `docs/` — `gradus-mapping.md` (the seven Gradus vs. modern
  references) and `fonts-and-input.md` (polytonic Greek fonts, Unicode
  normalization, and student input methods).

## Build

```bash
# After adding/editing a lesson JSON:
python3 scripts/build_lesson.py curriculum/i/some-lesson.json
python3 scripts/build_nav_map.py        # regenerate Prior/Next + Te Ipsum Proba links
python3 scripts/build_level_page.py --all   # regenerate every Gradus overview + Te Ipsum Proba page
python3 scripts/build_static_pages.py   # regenerate index.html, lexicon.html, exercitationes.html, varia.html
python3 scripts/build_exercise_index.py # regenerate search index + exercise-items index (run last)
```

No build tool, bundler, or `npm install` is required — every page is
static HTML/CSS/vanilla JS, deployable as-is to GitHub Pages.

## What's deliberately not built yet

Nav and footer only link to pages that exist: `index.html`,
`lexicon.html`, `exercitationes.html` (stub), `varia.html` (stub), and
the seven `gradus/*.html` overview pages (six of which are honest
"not yet built" placeholders — see `scripts/build_level_page.py`). The
Latin course's `examina.html`, `probatio.html` (placement test),
`iter.html` (progress dashboard page), `hodie.html` (spaced-repetition
review hub), and `verba-irregularia.html` equivalents are future work,
deliberately omitted rather than half-built or linked as dead ends.
