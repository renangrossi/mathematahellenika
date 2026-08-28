# Polytonic Greek: fonts, Unicode normalization, and student input

This course needs **polytonic** Ancient Greek — smooth/rough
breathings, three accent types, and iota subscript, on top of the
Modern-Greek "monotonic" letters most fonts/keyboards assume — to be
typed, stored, rendered, and graded correctly. This document covers
all four.

## Fonts

`scripts/site_chrome.py`'s `head()` loads two Google Fonts families
already, and `tokens.css` wires them into two separate stacks:

```css
--font-display: "Cormorant Garamond", "Times New Roman", serif;  /* Latin-script UI headings */
--font-body:    "Source Sans 3", "Segoe UI", Helvetica, Arial, sans-serif;  /* Latin-script body text */
--font-greek:   "Cardo", "Gentium Plus", "Noto Serif", "Source Sans 3", serif;  /* Greek-script text */
```

**Cardo** is the primary Greek face, and it's a deliberate choice, not
a default: it was drawn by David J. Perry specifically for classicists
and covers full polytonic Greek (every real combination of breathing +
accent + iota subscript, correctly kerned) as well as Latin and Hebrew
transliteration glyphs — a single font that renders a Greek example, a
Latin gloss, and a transliterated headword consistently. **Gentium
Plus** and **Noto Serif** are the fallback chain, both with broad
polytonic coverage, in case Cardo fails to load.

Any element holding Greek-script text should carry the `.greek`
utility class (defined in `assets/css/base.css`) to pick up this stack
— `lang="grc"` alone does **not** change the rendered font in most
browsers, so the class is what actually does the work.
`scripts/build_lesson.py`'s `escg()` helper (and its equivalent in
`build_level_page.py`) auto-wraps any Greek-script run inside a
plain-text field (titles, objectives, examples, summary, common
mistakes) in `<span class="greek">`; content written as raw HTML by a
lesson author (`content.explanation`, `rules[].body`) should add the
span by hand — see any Gradus I lesson JSON for the convention.

## Unicode normalization

Two different, unrelated normalization concerns apply:

1. **NFC vs. NFD in curriculum content.** Write Greek text in
   curriculum JSON in **NFC** (precomposed) form — e.g. the single
   codepoint `ά` (U+03AC), not `α` + a combining acute accent
   (U+0301) — since that's what any Greek keyboard layout or IME
   normally produces, and it keeps a git diff of a curriculum file
   showing genuine character-for-character changes rather than
   invisible re-composition noise. The build scripts and grading
   engine tolerate NFD input too (see next point), so this is a
   consistency convention for authors, not a hard technical
   requirement.
2. **Diacritic-insensitive grading.** `assets/js/exercises.js`'s
   `norm()` function — used to compare a student's typed answer
   against an `answers`/`answer` key — calls
   `.normalize("NFD")` before stripping every combining mark in the
   `U+0300`–`U+036F` range (which, after NFD decomposition, covers
   every polytonic diacritic: acute, grave, circumflex, smooth/rough
   breathing, and iota subscript) and folding final sigma (ς) to
   medial sigma (σ). This runs on **both** the answer key and the
   student's input, so:
   - A lesson author writes answer keys WITH full, correct
     accentuation (per `curriculum/SCHEMA.md`'s convention) without
     worrying that it makes grading stricter.
   - A student who types plain, unaccented Greek (`λογος`) is graded
     identically to one who types it fully accented (`λόγος`) —
     accuracy of accentuation is *taught* throughout the lessons, but
     never silently *penalized* in a fill-in-the-blank grading pass
     that isn't specifically about accent placement.
   - This same NFD-based stripping is reused, independently, in
     `worker/worker.js`'s course-catalog keyword matcher, so a
     student's question about "spiritus" or "σπιριτος" both still
     find the breathings lesson.

## Student input methods

A student typing Greek from scratch (rather than copy-pasting an
example) needs a way to produce polytonic characters. None of these
require installing anything beyond what's already free:

- **Windows**: Settings → Time & Language → Language & region → add
  "Greek" → its keyboard options include a **Polytonic Greek**
  layout (search "Greek Polytonic" in the layout picker). Built in,
  no download.
- **macOS**: System Settings → Keyboard → Input Sources → add
  language → **Greek — Polytonic** (a separate entry from plain
  "Greek"). Built in.
- **Linux (X11/Wayland via xkb)**: `setxkbmap gr polytonic` from a
  terminal, or add a "Greek (polytonic)" layout through the desktop
  environment's keyboard settings (GNOME Settings, KDE System
  Settings, etc.) — the `gr(polytonic)` XKB variant ships with the
  standard `xkeyboard-config` package on essentially every
  distribution.
- **No install / shared or locked-down computer**: a web-based
  polytonic Greek keyboard (search "polytonic Greek keyboard online";
  several free, keyless tools exist, e.g. under lexilogos.com) lets a
  student click or type-and-convert their way to correct Unicode
  without any OS-level configuration, then copy the result into an
  exercise field.
- **Fallback for exercises specifically**: because grading is
  diacritic-insensitive (see above), a student without a working
  polytonic input method set up yet can still complete every
  fill-in-the-blank/typing exercise by typing plain, unaccented Greek
  letters — nothing in the exercise engine blocks progress on this,
  though learning a real input method is worth doing early, since
  correct accentuation is itself one of Gradus I's own objectives
  (see `gradus/fundamenta/spiritus-et-accentus.html`).

## Rendering sanity-check

If polytonic characters ever show up as tofu boxes (☐) or with visibly
wrong/missing diacritics in a browser: confirm the page actually loaded
Cardo (dev tools → Network → filter "Cardo"; Google Fonts occasionally
fails silently behind some ad-blockers/privacy extensions, in which
case the `.greek` class falls through to Gentium Plus, then Noto Serif,
then the plain body sans-serif — the last of which does render Greek
correctly on most modern operating systems, just without Cardo's
classicist-tuned kerning).
