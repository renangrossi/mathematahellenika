# Natural Method transformation guide (Ancient Greek)

Ported from the Latin sibling course's guide of the same name, where this
pattern was developed and proven across 51 lessons. This file records the
Greek-specific adaptation and current state.

Read `docs/natural-method-audit.csv` (regenerate with
`python3 scripts/audit_curriculum.py --csv docs/natural-method-audit.csv`)
before picking the next lesson — ordered by curriculum sequence, carrying
every lesson's A/B/C score.

## Current state

As of the pilot (`ii-declinatio-prima`): 5/67 lessons score A, 62 B, 0 C.
No lesson in this course has ever scored C under the audit heuristic —
every lesson already carries some meaningful Greek (real example
sentences with glosses, and often true-false/matching exercises), unlike
the Latin course's initial state. The gap here is narrower but real: past
Gradus I, comprehension-first material (a passage read *before* the
paradigm, with comprehension questions) is the exception, not the rule.

## The pattern, adapted for Greek

Same shape as the Latin guide: rewrite `content.intro` and
`content.explanation` so the learner meets the target forms in a short
comprehensible passage before the paradigm table (which stays in
`content.rules`, following immediately after — no reordering needed,
`build_lesson.py` already renders Explicatio before Regulae), and add one
`reading-comprehension` exercise block (this course's first, added in the
pilot) ahead of the kept multiple-choice/fill-blank/true-false blocks.

Two Greek-specific things to know:

1. **`content.intro` supports inline Greek safely.** Unlike the Latin
   course (where `intro` is always plain text, HTML-escaped), this
   course's `build_lesson.py` uses a `rich()` helper: if `intro` contains
   `<`, it's treated as pre-formed HTML and passed through unescaped
   (write `<span class="greek">...</span>` around Greek runs yourself,
   exactly as `content.explanation`/`rules[].body` already do elsewhere
   in every lesson); if it contains no `<`, any bare Greek-script run is
   auto-wrapped for you via `escg()`. Either way works — the pilot used
   explicit spans since it embeds a full passage. This is *more*
   permissive than the Latin course, not a trap to route around.
2. **Compose new Greek conservatively.** Accentuation (recessive accent,
   enclitics, the α-pure/impure and other paradigm-specific rules) is
   genuinely hard to get right freely. The pilot built its passage almost
   entirely by recombining vocabulary/forms already attested correct
   *within that same lesson's own rules/examples*, plus the εἰμί paradigm
   and the Ἀγάθων/Μελίτη cast established in Gradus I's dialogue lesson —
   minimizing freely-invented morphology. Keep doing this: pull nouns,
   adjectives, and paradigm forms straight from the lesson's own `rules`/
   `examples` fields rather than inventing new declined forms, and lean
   on verbs already conjugated somewhere in the curriculum (εἰμί, φιλέω,
   ἔχω, and whatever else Gradus I's dialogue lessons already conjugate).
3. **Comprehension questions use Latin prompts/options**, not free Greek
   questions — this course's own established convention (see Gradus I's
   `i-lectio-prima` reading-comprehension block, and the AI-teacher system
   prompt: explanations and UI are primarily in Latin, the historical
   metalanguage for teaching Greek). Keep following it.

## The recurring cast

**Ἀγάθων** (Agathon) and **Μελίτη** (Melite), established in Gradus I's
own dialogue lesson (`i-lectio-prima`) — already the two named students
of a `διδάσκαλος`. `scripts/audit_curriculum.py`'s `CAST_RE` also tracks
Σωκράτης/Ξανθίππη/Περικλῆς/Δημοσθένης as historical figures the later
authentic-text lessons draw on; extend that list if you add a new
recurring name.

## Priority for the next pass

Worst-scoring lessons (all B, score 0-1): `iii-declinatio-tertia-
consonantica` (score 0, the single lowest), then a cluster of Gradus I/II
foundational lessons at score 1 — `i-articulus-et-numeri`,
`i-pronomina-personalia`, `ii-declinatio-secunda-masculina-et-neutra`,
`ii-articulus-plenus`, `ii-adiectiva-classis-primae`,
`ii-coniugatio-praesentis-activi`, `ii-coniugatio-praesentis-medii-
passivi`, `ii-praepositiones-fundamentales`, `ii-adverbia-et-negatio`,
`ii-interrogativa-fundamentalia`, `ii-numeri-cardinales-1-100`,
`iii-declinatio-tertia-vocalica`, `iii-adiectiva-tertiae-declinationis`.
Gradus II (the first full grammar unit after Gradus I's dialogues) is the
highest-leverage target, exactly as it was for Latin.
