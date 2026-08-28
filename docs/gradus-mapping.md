# Gradus mapping: this course's seven levels vs. typical modern references

This course does not follow the CEFR (the Common European Framework
used for living languages) or any single existing Ancient Greek
textbook's chapter order — Ancient Greek pedagogy has no single
standard sequence the way, say, modern-language CEFR exams do. The
table below gives an **approximate** correspondence so a student
already familiar with CEFR levels, or with one of the well-known
beginner Greek textbooks, has a sense of where each Gradus sits. Treat
every row as a rough band, not an equivalence — a Gradus boundary here
is drawn where it makes the clearest *pedagogical* break for a
Latin-medium classical course, not to line up chapter-for-chapter with
any other syllabus.

| Gradus | Name | Core grammar introduced | Rough CEFR band | Comparable point in well-known textbooks |
|---|---|---|---|---|
| I | Fundamenta | Alphabet, Attic reconstructed pronunciation, breathings, accents, basic greetings, εἰμί | Pre-A1 | Athenaze ch. 1; Hansen & Quinn ch. 1-2; JACT *Reading Greek* "Alphabet and pronunciation" section |
| II | Elementa | 1st/2nd declension, the article, present system of ω-verbs, basic adjectives | A1 | Athenaze ch. 2-4; Hansen & Quinn ch. 3-6; Mastronarde ch. 1-6 |
| III | Progressus | 3rd declension, contract verbs, imperfect, future, middle voice begins | A2 | Athenaze ch. 5-8; Hansen & Quinn ch. 7-12; Mastronarde ch. 7-14 |
| IV | Media | Aorist system, perfect system, participles, infinitives, deponents | B1 | Athenaze ch. 9-12; Hansen & Quinn ch. 13-19; Mastronarde ch. 15-25 |
| V | Provectus | Subjunctive, optative, purpose/result clauses, conditionals | B1/B2 | Athenaze ch. 13-16; Hansen & Quinn ch. 20-27; Mastronarde ch. 26-35 |
| VI | Altior | Complex syntax, full indirect statement, verbal adjectives, adapted prose | B2/C1 | Athenaze ch. 17-23; Hansen & Quinn ch. 28-34; JACT *Reading Greek*, later sections |
| VII | Auctores | Unadapted texts: Xenophon, Plato, Lysias, Homeric excerpts, NT Koine samples | C1/C2 | "Reading the real thing" stage in any of the above — post-primer intermediate readers |

## Why these seven, and why these boundaries

- **Gradus I is entirely pre-grammatical.** Unlike the sibling Latin
  course (whose Gradus I already includes `sum` and personal
  pronouns fully declined), this course's Gradus I is deliberately
  slower on declension: Greek's polytonic orthography (breathings,
  three accent types, iota subscript) is a genuine second layer of
  "alphabet" that Latin doesn't have, and rushing past it produces
  students who can conjugate but can't read their own textbook
  correctly. See `gradus/fundamenta/spiritus-et-accentus.html` for the
  detail this earns.
- **The declension/conjugation split across II-III mirrors Latin's own
  course**, not because Greek and Latin declensions correspond
  1-for-1 (they don't), but because "nouns and the present system
  first, everything else after" is the same sound pedagogical choice
  in both languages, and it keeps the two sibling courses' Gradus
  numbers meaning roughly the same thing to a student doing both.
- **The aorist (Gradus IV) is Greek's biggest single hurdle for a
  Latin-trained ear**, since Latin's perfect system does the job of
  both the Greek aorist AND the Greek perfect, and the two are not
  interchangeable in Greek. Isolating it in its own Gradus, alongside
  participles (which lean heavily on the aorist stem), matches how
  most of the textbooks above treat it as well.
- **Subjunctive AND optative together in Gradus V** (rather than
  splitting them, as some textbooks do) reflects that in Attic prose
  they are two faces of the same subordinate-clause system
  (purpose/result/fear clauses, indirect questions) — teaching one
  without the other leaves half of "what mood do I use here?"
  unanswered.
- **Gradus VI is the "adapted classical prose" bridge, Gradus VII is
  unadapted** — same two-step landing used by the Latin course
  (Caesar/Cicero adapted in its Gradus VI, unadapted in its Gradus
  VII), and by nearly every serious Greek program: adapted prose
  lets a student practice reading fluency without a dictionary open
  in one hand, before removing that scaffold entirely.
- **Homeric and Koine notes are folded in, not given their own
  Gradus.** A dedicated "Homeric Greek" or "Koine Greek" Gradus would
  imply they are later/harder than Attic, which isn't really true —
  they're *different*, not more advanced. Instead, dialect notes
  appear wherever they're pedagogically relevant (see any lesson's
  `content.rules` for the pattern), and Gradus VII's authors list
  includes both a genuine Homeric excerpt and a Koine (New Testament)
  excerpt precisely so a student's first unadapted reading isn't
  Attic-only.

## Current build status

As of this scaffold, **only Gradus I has published lessons** (3 of 9
planned — see `curriculum/index.json`'s `status` field for the
honest, lesson-by-lesson accounting). Gradus II-VII exist only as a
planned unit outline in `curriculum/index.json`, rendered as a short
"not yet built" placeholder page by `scripts/build_level_page.py`
rather than a broken link. This document describes the intended shape
of all seven; `curriculum/index.json` is the single source of truth
for exactly what is written vs. planned at any given moment.
