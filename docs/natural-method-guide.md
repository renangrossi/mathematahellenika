# Natural Method transformation guide (Ancient Greek)

Ported from the Latin sibling course's guide of the same name, where this
pattern was developed and proven across 51 lessons. This file records the
Greek-specific adaptation and current state.

Read `docs/natural-method-audit.csv` (regenerate with
`python3 scripts/audit_curriculum.py --csv docs/natural-method-audit.csv`)
before picking the next lesson — ordered by curriculum sequence, carrying
every lesson's A/B/C score.

## MANDATORY: exercises should be mostly Greek, not Greek-with-a-Latin-key

**Standing requirement for every Greek lesson, past and future.** The
concrete failure mode: an exercise's Greek answer choice (or a
fill-blank prompt's parenthetical) carries its own Latin/English
translation attached right next to it — e.g. a `fill-blank` prompt
reading `"Δίδωσί ___ τὸ βιβλίον. (ūsus normālis, "mihi")"`, where the
quoted `"mihi"` *is* the Latin translation of the correct answer. A
learner can solve exercises like this by pattern-matching the quoted
gloss to a superficially similar Greek option, never actually parsing
the Greek sentence — which defeats the entire Natural Method premise
that Greek competence should come from understanding Greek directly,
not from a permanently-attached translation crutch. This is distinct
from, and independent of, the audit script's A/B/C score: a lesson can
score A (comprehension-first structure, staged exercises) and still
fail this test if its exercises quietly hand the learner the answer key
in Latin.

**The test for every exercise, per item**: *could the learner solve
this by understanding the Greek itself, or does the Latin/English gloss
effectively hand them the answer?* If the latter, redesign it.

**What to do:**

1. **Answer choices (`options` in `multiple-choice`/`fill-blank`) should
   normally be Greek alone** — no `"τῷ φίλῳ — amico"` pattern, ever.
   (This course's `options` arrays were already almost entirely clean of
   this on inspection — the more common and worse version of the same
   problem was in the *prompt*, see next point.)
2. **Fill-blank/multiple-choice prompts must not carry a quoted
   translation of the missing form.** A grammatical *label* in Latin
   metalanguage (a case name, person marker, or the Greek headword being
   inflected — e.g. `"(τιμή, gen. sg.)"` or `"(1ª sg.)"`) is fine and
   stays — that is consolidation-stage terminology, not a translation
   crutch, and is explicitly sanctioned by the existing staging rule
   above (grammar-naming is the *later* stage, after meaning). What must
   go is any quoted natural-language phrase — `"“the man is in the
   house”"`, `"“mihi”"`, `"“vīgintī virī”"` — that translates the Greek
   sentence or the answer itself. Where the item was a bare noun-phrase
   with no verb (`"___ ἄνθρωπος (masc. sg.)"`), prefer turning it into an
   actual clause reusing the lesson's own established vocabulary/cast
   (`"___ ἄνθρωπος ἐν τῇ οἰκίᾳ ἐστίν."`) so meaning comes from the
   Greek sentence itself, not a gloss. Numerals as Arabic digits (`"(20)"`)
   are not a translation and are fine to keep — they're a symbol, not a
   language.
3. **True/false statements, recognition-stage prompts, and matching
   pairs should prefer Greek content directly** where the lesson's own
   vocabulary supports it — e.g. a `true-false` item stating a Greek
   sentence from the passage itself (`Ὁ Ἀγάθων εἰς τὴν ἀγορὰν ἔρχεται.` —
   Ἀληθές/Ψεῦδος) is stronger than a Latin sentence *describing* what the
   Greek says. This course's existing `recognize`-stage blocks (added by
   the staging-rule pass above) currently phrase their reasoning
   statements in Latin *about* a quoted Greek sentence — that's an
   acceptable middle ground (it still forces reasoning about the Greek,
   not a translation-match), but a pure-Greek statement is the stronger
   form when a lesson's vocabulary is rich enough to support one
   confidently; use judgement per lesson rather than converting
   mechanically.
4. **Keep genuine translation exercises — as one type among several, not
   the default.** This course's `matching` blocks titled "Iunge Graecum
   cum Latīnō" (pairing a Greek phrase with its Latin sense) are a
   legitimate, deliberate exercise type and should stay; the difference
   from the anti-pattern above is that the *whole exercise* is honestly
   framed as translation practice, not a translation gloss silently
   riding along inside every option of an exercise that's nominally
   testing grammar/comprehension.
5. **Feedback/explanation text** (the `explanation` field shown after
   answering) is not fully addressed by this pass — it remains
   Latin-dominant commentary across the curriculum (consistent with this
   course's own foundational design: Latin as the historical metalanguage
   for teaching Greek, per the AI-teacher system prompt and this guide's
   own conventions). Making feedback itself "mostly Greek" per the ideal
   (`Ὀρθῶς! Ὁ Ἀγάθων δίδωσι τὸ δῶρον τῷ φίλῳ.` rather than a Latin
   grammatical note) is a much larger rewrite — every `explanation`
   string in all 67 lessons — that was judged out of scope for this pass
   given the volume; treat it as a longer-term aspiration, not something
   to silently skip when a lesson is next touched substantially.

**Audit performed this pass**: every `fill-blank`/`multiple-choice` item
across all 29 completed Gradus I-III lessons was checked programmatically
for a Greek-script prompt containing a quoted (`"…"`/`"…"`) translation.
61 violations were found across 14 files — including, notably, 10 that
this session's own earlier staging-rule pass had just introduced while
"upgrading" bare noun-phrase prompts into fuller context (`i-articulus-
et-numeri`, `ii-declinatio-prima`) — proof that this check needs to be
part of the standard review for every future edit, not just pre-existing
content. All 61 were fixed by removing the quoted translation while
keeping any grammatical label/Greek headword cue. Re-run the same
`options`/`prompt` quote-scan (see the Python snippet pattern: search
`fill-blank`/`multiple-choice` items for Greek-script text containing
`"` or `"`) on any lesson before considering it finished, in Gradus
IV-VII as much as when revisiting Gradus I-III.

**Apply from the start in Gradus IV-VII**: do not draft exercises with
Latin glosses attached to every option "for clarity" and plan to strip
them later — write prompts and options Greek-first from the first draft,
reaching for a fuller Greek clause (reusing established vocabulary)
instead of a translation whenever an item needs more context to be
solvable.

## Current state

As of this pass: **29/67 lessons score A, 38 B, 0 C** (up from 5 A / 62 B
after the `ii-declinatio-prima` pilot). No lesson in this course has ever
scored C under the audit heuristic — every lesson already carries some
meaningful Greek (real example sentences with glosses, and often
true-false/matching exercises), unlike the Latin course's initial state.
**Gradus I, II, and III are now all fully transformed (9/9, 10/10, 10/10
A)**. Every remaining B lesson (38 of them) is in Gradus IV, V, VI, or
VII — those four levels are entirely untouched and are the whole of the
remaining work.

The last 3 Gradus I lessons closed in this pass were two pure-phonology
lessons (`i-spiritus-et-accentus`, `i-syllabae-et-enclitica` — no
vocabulary exists yet at that point in the sequence) plus
`i-salutationes-et-verbum-sum` (the είμί lesson). Following the Latin
course's own precedent for its analogous phonology-only Gradus I
lessons, the two phonology lessons got a *light* treatment: a
reading-comprehension block built from real attested words/phrases
already in the lesson (ὁ ἄνθρωπος, ῥήτωρ, οὗτος, βιβλίον, ἄγγελος...)
with questions testing the phonological/orthographic fact itself
(which syllable divides where, why this word takes a rough breathing),
not an invented narrative — forcing a story onto pre-vocabulary content
would be artificial. `i-salutationes-et-verbum-sum` did get an
Agathōn/Melitē scene, since it already has real content (χαῖρε, εἰμί)
that i-lectio-prima's own founding dialogue and several later lessons'
passages already draw on — this lesson is arguably the *true* source of
the χαῖρε/τίς-εἶ material this guide's earlier batches kept reusing.

A third batch (7 lessons) finished Gradus III: `iii-verba-contracta-in-
eo`, `iii-verba-contracta-in-ao-et-oo`, `iii-tempus-imperfectum`,
`iii-tempus-futurum-activum-et-medium`, `iii-pronomen-relativum`,
`iii-pronomina-demonstrativa`, `iii-comparatio-adiectivorum` (the
level's own capstone). Same pattern, same conservative-composition
discipline; several of these scenes chain directly into each other
(the imperfectum lesson's teacher-and-students scene continues the
declinatio-tertia-vocalica/adiectiva-tertiae-declinationis king-and-city
arc's classroom framing; the capstone lesson has Agathōn and Melitē
discuss Socrates and the city one last time before Gradus III closes).
All 7 landed at A (score 5).

This pass (two batches) transformed 14 lessons: the worst-scoring lesson
(`iii-declinatio-tertia-consonantica`, score 0), the two Gradus I
lessons `i-articulus-et-numeri`/`i-pronomina-personalia`, all 8 remaining
Gradus II lessons (`ii-declinatio-secunda-masculina-et-neutra`,
`ii-articulus-plenus`, `ii-adiectiva-classis-primae`,
`ii-coniugatio-praesentis-activi`, `ii-coniugatio-praesentis-medii-
passivi`, `ii-praepositiones-fundamentales`, `ii-adverbia-et-negatio`,
`ii-interrogativa-fundamentalia`, `ii-numeri-cardinales-1-100`), and 2
more Gradus III lessons (`iii-declinatio-tertia-vocalica`,
`iii-adiectiva-tertiae-declinationis`). All 14 landed comfortably at A
(score 5). Each new passage reused, near-verbatim, sentences already
attested in that lesson's own `examples`/`rules` (see "Compose new Greek
conservatively" below) — e.g. `iii-declinatio-tertia-consonantica`'s
story is built almost entirely out of its own pre-existing "ὁ φύλαξ τῆς
πόλεως", "ὁ ῥήτωρ καλῶς λέγει", and "τοῖς φύλαξι πιστεύομεν" — recombined
into a short connected scene with Ἀγάθων and Μελίτη rather than presented
as isolated glossed sentences. Several lessons' scenes deliberately chain
into each other (`iii-declinatio-tertia-vocalica`'s king-and-city scene
continues directly into `iii-adiectiva-tertiae-declinationis`'s passage
about the same king and city), and `ii-interrogativa-fundamentalia`'s
passage explicitly echoes `i-lectio-prima`'s own founding dialogue
("Τίς εἶ;" ... "Ἀγάθων εἰμί") rather than inventing a new frame.

A recurring composition risk worth naming for future batches: Greek
demonstrative pronouns (οὗτος, τοῦτο...) and many common verbs outside
εἰμί/φιλέω/ἔχω/λέγω/βούλομαι have no attested inflected form anywhere in
this course yet, so several draft passages that reached for them (ἐρωτᾷ,
γίγνεται, μανθάνω, τοῦτο, ταύτῃ...) were cut or replaced during drafting
in favor of sticking to each lesson's own attested vocabulary plus this
small set of safe, already-well-established verbs. When a scene needs
something beyond that set, prefer rephrasing over inventing a new
inflected form.

**A staging pass followed the classification pass**: `i-articulus-et-
numeri`, `i-pronomina-personalia`, and `i-salutationes-et-verbum-sum`
were all already A but their first grammar-facing exercise still asked
the learner to name or produce a form (e.g. "Quae est fōrma nōminātīva
singulāris fēminīna articulī?") right after a single short story. Per
the "MANDATORY: stage every morphology exercise set" section below,
each got a new `recognize` exercise block (meaning-first, minimal-
contrast reasoning) inserted between the story and the first
grammar-naming exercise, `i-salutationes-et-verbum-sum`'s passage was
extended so all 6 persons of εἰμί are attested in context before being
tested, and `i-articulus-et-numeri`'s bare noun-phrase fill-blank
prompts were rewritten as full clauses. See that section for the rule
to apply to every lesson touched going forward, including re-touching
already-A Gradus II/III lessons.

**A pre-existing accuracy bug was also fixed in this pass**:
`ii-declinatio-secunda-masculina-et-neutra.json`'s `examples` list
contained `"ὦ λόγε... — Ō verbum..."`, i.e. the vocative case applied to
an abstract noun (λόγος, "word/speech/reason") as if it were a person
being addressed — linguistically wrong; the vocative is for persons (and
occasionally personified things), not ordinary nouns treated as
addressees. Replaced with `"χαῖρε, ὦ φίλε. — Salvē, amīce."`, a genuine
address to a person, using vocabulary already established in
`i-salutationes-et-verbum-sum` and `i-lectio-prima`. A curriculum-wide
grep (`grep -rn "ὦ " curriculum/`) turned up no other instance of this
pattern — every other vocative in the course (πολῖτα, βασιλεῦ, δοῦλε,
φίλοι, ἄνδρες, μαθηταί, Σώκρατες, Ἀθηναῖοι...) already addresses a real
person. Worth re-checking with the same grep after any future batch that
touches vocative-case material.

## MANDATORY: stage every morphology exercise set — meaning before naming

**This applies to every lesson touched from now on, including lessons
already scored A.** The audit script's A/B/C classification is blind to
this — it can score a lesson A while its first grammar exercise still
asks the learner to produce or name a form in a vacuum. Passing the
audit is necessary but not sufficient.

The rule: **never make the learner produce or name a grammatical form
before giving them enough meaningful Greek to recognize what that form
does.** Concretely, for any lesson introducing a new case, ending,
tense, or agreement pattern, the exercise sequence must be:

1. **Meaning** — the reading-comprehension passage (already the norm).
2. **Recognition** — a NEW stage, inserted directly after the story and
   before any exercise that names or asks to reproduce a form. Built
   from the *same* sentences already in the passage (or trivial
   variants), it asks who-does-what/which-sentence-fits questions —
   never "what case is this?" Use `true-false` (statements about who
   did what to whom) or `multiple-choice` with full-sentence prompts
   and meaning-based options, e.g. "Cui magister librum dat, secundum
   Agathōne?" rather than "Quae fōrma est datīvus?". Include at least
   one item that asks *why* a form was chosen over a superficially
   similar alternative (a minimal-contrast question) when the lesson
   has one to offer (fortis/enclitic pairs, ἐν/εἰς, ὁ/ἡ/τό...).
3. **Selection in context** — the existing `fill-blank` stage stays,
   but every prompt must be a full meaningful clause (reusing the
   passage's own vocabulary), never a bare noun phrase like "___
   ἄνθρωπος (masc. sg.)" with no verb or situation attached. Rewrite
   any such bare-NP prompt into a clause the learner has to actually
   understand to answer, e.g. "___ ἄνθρωπος ἐν τῇ οἰκίᾳ ἐστίν."
4. **Explicit grammar** — the pre-existing `multiple-choice` block that
   names cases/forms directly is fine to KEEP, but retitle it toward
   consolidation (e.g. "Nunc Nōmina Rēgulam" / "now name the rule") and
   make sure it comes AFTER the recognition and selection stages, not
   immediately after the story.
5. The closing `true-false`/`matching` blocks (rule-level facts,
   vocabulary matching) stay last, unchanged, as final consolidation.

**Also lengthen the passage itself** wherever the exercises need to
test a form the passage doesn't actually show in context yet — don't
test what the learner hasn't met. Example: `i-salutationes-et-verbum-
sum`'s original passage only showed 3 of εἰμί's 6 persons (εἰμι, εἶ,
ἐσμέν) but its fill-blank tested all 6; the passage was extended with
two more lines (a διδάσκαλος speaking in 3rd person singular/plural,
addressing the pair in 2nd plural) so every tested form is now attested
in a meaningful sentence first. Keep recycling known vocabulary when
extending — the goal is more *sentences* using what's already known,
not more new words.

This was applied retroactively to `i-articulus-et-numeri`,
`i-pronomina-personalia`, and `i-salutationes-et-verbum-sum` first, then
— since the same violation turned out to be systemic — to **every one**
of the other 19 Gradus II/III lessons (all 10 of Gradus II including
the original `ii-declinatio-prima` pilot, and all 10 of Gradus III).
Each got a new `true-false` "recognize" block titled "Quid Vērē
Dīcitur? (Ex Sēnsū)" inserted directly after the story block and before
whichever grammar-naming block (`multiple-choice` or `fill-blank`) came
first — 4 items per block, built entirely from the story's own
sentences, phrased as comprehension/reasoning statements ("Cīvēs,
secundum Melitēn, volunt lēgem solvere, nōn servāre" — true/false) never
as "what case/form is this". `ii-declinatio-prima` (the pilot) and the
three Gradus I lessons additionally got their `fill-blank` prompts
rewritten from bare noun-phrases/paradigm-labels into full clauses, and
their `multiple-choice` grammar-naming block moved to *after* the
fill-blank stage and retitled toward consolidation ("Nunc Nōmina
Rēgulam"); the other 18 lessons' fill-blank/multiple-choice ordering
and prompts were left as they were (a smaller remaining gap — see
below) since the primary violation (nothing but a single story between
"meaning" and "name the grammar") is what the recognize-block insertion
directly fixes, and doing so for all 20 lessons was judged higher
priority than perfecting the remaining stages on the 3 flagship lessons
alone. **Gradus I, II, and III are now believed fully compliant with
this rule; Gradus IV-VII have not been checked against it at all** —
budget the same treatment (recognize block first, applied everywhere
the pattern repeats) into that work rather than treating it as a
separate pass at the end.

**Remaining lower-priority gap on the 18 non-flagship lessons**: their
`fill-blank` blocks still have some bare paradigm-label prompts (e.g.
"τιμή, genetīvus singulāris: ___" with no clause), and their
`multiple-choice` grammar-naming block still comes immediately after
the new recognize block rather than after a contextual fill-blank
stage. This is a real but smaller gap than the one just closed — worth
tightening opportunistically when a lesson is next touched for other
reasons, following the fuller treatment `ii-declinatio-prima` got as
the model.

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

Gradus I, II, and III are all fully cleared. All remaining work is now:

1. **Gradus IV-VII, 38 lessons, still entirely B — every lesson in
   these 4 levels** — the next major body of work, and by far the
   largest remaining chunk. Skim a few from each level first to see
   whether they follow the same "already has narrative + glosses, just
   not comprehension-first" shape as Gradus I-III, or need a different
   approach — the way Latin's Gradus VI/VII authentic-text lessons ended
   up needing a `magister` classroom frame rather than a family-story
   frame. Given this course teaches Greek through Latin, and Gradus
   VI/VII likely include unadapted-author lessons (Plato, Lysias — see
   `vi-lectio-adaptata-platon.json`, `vii-lysias-orationes-selectae.json`,
   `vii-platon-apologia.json` referenced during the vocative grep), the
   Latin course's `magister`-frame pattern for authentic texts is the
   most likely fit there too, adapted with the Ἀγάθων/Μελίτη cast (now
   presumably older students) or a Greek-appropriate teacher framing.
   By Gradus IV-V, verb morphology (aorist, subjunctive, participles)
   will be considerably richer than Gradus I-III's εἰμί/φιλέω/λύω/
   contract-verb core used so far — re-derive the "safe verb list" for
   composing new passages from what each *specific* lesson and its
   already-transformed prerequisites actually attest, rather than
   assuming the Gradus I-III list still covers it.
