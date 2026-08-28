#!/usr/bin/env python3
"""
Render one curriculum/{level}/{lesson-id}.json into gradus/{level}/{lesson-id}.html,
following the section structure (Proposita -> Explicatio -> Regulae ->
Exempla -> Errores Communes -> Exercitium -> Summarium -> Perge), using
the shared chrome from site_chrome.py.

Adapted verbatim from the sibling Latin-course project's
scripts/build_lesson.py -- identical structure/pipeline; only the
brand name in <title>/breadcrumb-adjacent copy differs (see
site_chrome.py). Section labels stay Latin, matching this course's
metalanguage.

Usage:
    python3 scripts/build_lesson.py curriculum/i/alphabetum-et-phonologia.json
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_chrome  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
REL = "../../"  # gradus/{level}/{lesson}.html -> repo root
NAV_MAP_PATH = Path(__file__).resolve().parent / "lesson_nav_map.json"

CHECK_SVG = '<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg>'
ARROW_SVG = '<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'

LEVEL_NAMES = {code: name for code, name, _slug in site_chrome.LEVELS}
LEVEL_SLUGS = {code: slug for code, name, slug in site_chrome.LEVELS}


def esc(s: str) -> str:
    return html.escape(s, quote=False)


# Greek-script runs (Greek and Coptic U+0370-03FF, Greek Extended
# U+1F00-1FFF -- the polytonic precomposed block) get wrapped in the
# .greek utility class (see base.css) so they render in the Cardo-first
# --font-greek stack instead of the Latin-oriented body face, wherever
# they appear inside a plain-text field (objectives/examples/summary/
# mistakes/titles) that this build script HTML-escapes itself. Content
# fields written as raw HTML by the lesson author (content.explanation,
# rules[].body) are expected to add their own `<span class="greek">`
# by hand instead -- see curriculum/SCHEMA.md and any Gradus I lesson
# JSON for the convention. Applied AFTER esc() -- Greek letters contain
# no HTML metacharacters, so escaping first and wrapping second is safe
# and order-independent for correctness.
GREEK_RUN = re.compile("([\u0370-\u03ff\u1f00-\u1fff]+)")


def escg(s: str) -> str:
    return GREEK_RUN.sub(r'<span class="greek">\1</span>', esc(s))


# Same raw-HTML-vs-plain-text convention as content.explanation (see
# explanation_section() below): if the author included a literal "<",
# the field is pre-formed HTML they're responsible for escaping/
# wrapping Greek in themselves (as content.explanation/rules[].body
# already do) and is passed through unescaped; otherwise it's plain
# text, HTML-escaped with any bare Greek-script run auto-wrapped via
# escg(). Used for content.intro, which -- unlike explanation -- is
# always already inside a <p> in its template, so (unlike explanation's
# own plain-text branch) this never adds its own <p> wrapper.
def rich(s: str) -> str:
    return s if "<" in s else escg(s)


def page_header(lesson):
    return f"""<div class="page-header">
        {site_chrome.MEANDER_ROW}
        <div class="page-header__inner">
            <div class="page-header__text">
                <p class="eyebrow hero__eyebrow">Gradus {lesson['level']} &middot; {esc(LEVEL_NAMES.get(lesson['level'], ''))}</p>
                <h1>{escg(lesson['title'])}</h1>
                <p class="page-header__lede">{escg(lesson['subtitle'])}</p>
            </div>
        </div>
    </div>"""


def toc(present_ids):
    labels = {
        "objectives": "Proposita", "explanation": "Explicatio", "rules": "Regulae",
        "examples": "Exempla", "mistakes": "Errores Communes", "practice": "Exercitium",
        "summary": "Summarium", "lesson-test-yourself": "Te Ipsum Proba",
    }
    links = "".join(f'<a href="#{a}">{labels[a]}</a>' for a in labels if a in present_ids)
    return f'<div class="level-toc"><div class="level-toc__inner">{links}</div></div>'


def objectives_section(lesson):
    items = "".join(f"<li>{CHECK_SVG}<span>{escg(o)}</span></li>" for o in lesson["objectives"])
    return f"""<section id="objectives" class="section section--tight" aria-labelledby="obj-heading">
        <div class="section__inner split">
            <div>
                <p class="eyebrow">Prooemium</p>
                <p style="font-size:var(--step-0);color:var(--color-text-muted);max-width:56ch;">{rich(lesson['content']['intro'])}</p>
            </div>
            <div class="card card--feature">
                <h2 id="obj-heading" style="font-size:var(--step-0);">Post hanc lectionem poteris&hellip;</h2>
                <ul class="objectives-list">{items}</ul>
            </div>
        </div>
    </section>"""


def explanation_section(lesson):
    c = lesson["content"]
    explanation = c.get("explanation")
    register = f'<div class="notice mt-lg"><strong>Nota</strong><p>{esc(c["registerNote"])}</p></div>' if c.get("registerNote") else ""
    if not explanation and not register:
        return ""
    if explanation:
        inner = explanation if "<" in explanation else f"<p>{esc(explanation)}</p>"
        body = f'<div class="prose">{inner}</div>'
    else:
        body = ""
    return f"""<section id="explanation" class="section section--surface" aria-labelledby="exp-heading">
        <div class="section__inner section__inner--narrow">
            <p class="eyebrow">Explicatio</p>
            <h2 id="exp-heading" class="visually-hidden">Explicatio</h2>
            {body}
            {register}
        </div>
    </section>"""


def rules_section(lesson):
    rules = lesson["content"].get("rules") or []
    if not rules:
        return ""
    blocks = "".join(f'<div class="card" style="margin-bottom:var(--space-md);"><h3>{escg(r["heading"])}</h3>{r["body"]}</div>' for r in rules)
    return f"""<section id="rules" class="section section--tight" aria-labelledby="rules-heading">
        <div class="section__inner">
            <p class="eyebrow">Regulae Grammaticae</p>
            <h2 id="rules-heading">Regulae</h2>
            {blocks}
        </div>
    </section>"""


def examples_section(lesson):
    items = "".join(
        f'<li><svg class="examples-list__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg><span>{escg(e)}</span></li>'
        for e in lesson["content"]["examples"]
    )
    return f"""<section id="examples" class="section section--surface" aria-labelledby="ex-heading">
        <div class="section__inner">
            <p class="eyebrow">Exempla</p>
            <h2 id="ex-heading">Exempla in Usu</h2>
            <ul class="examples-list">{items}</ul>
        </div>
    </section>"""


def mistakes_section(lesson):
    if not lesson["content"].get("commonMistakes"):
        return ""
    cards = "".join(
        f"""<div class="mistake-card">
            <p class="mistake-card__wrong"><span class="badge badge--pdf" style="margin-right:.5em;">Vitium</span>{escg(m['wrong'])}</p>
            <p class="mistake-card__right"><span class="badge badge--doc" style="margin-right:.5em;">Rectius</span>{escg(m['right'])}</p>
            <p class="mistake-card__why">{escg(m['why'])}</p>
        </div>"""
        for m in lesson["content"]["commonMistakes"]
    )
    return f"""<section id="mistakes" class="section section--tight" aria-labelledby="mist-heading">
        <div class="section__inner">
            <p class="eyebrow">Errores Communes</p>
            <h2 id="mist-heading">Cave</h2>
            <div class="mistakes-grid">{cards}</div>
        </div>
    </section>"""


def practice_section(lesson):
    blocks = "".join(
        f'<div class="exercise-block"><script type="application/json" class="exercise-data">{json.dumps(ex, ensure_ascii=False)}</script></div>'
        for ex in lesson["exercises"]
    )
    return f"""<section id="practice" class="section section--surface" aria-labelledby="practice-heading">
        <div class="section__inner">
            <p class="eyebrow">Exercitationes Interactivae</p>
            <h2 id="practice-heading">Exercitium</h2>
            <p style="color:var(--color-text-muted);margin-bottom:var(--space-md);max-width:60ch;">Confice quamque exercitationem, deinde <strong>Proba</strong> preme ut summam et explicationem cuiusque responsi videas.</p>
            {blocks}
        </div>
    </section>"""


def summary_section(lesson):
    items = "".join(f"<li>{escg(s)}</li>" for s in lesson["summary"])
    return f"""<section id="summary" class="section section--tight" aria-labelledby="sum-heading">
        <div class="section__inner section__inner--narrow">
            <p class="eyebrow">Summarium</p>
            <h2 id="sum-heading">Recognitio</h2>
            <ul class="summary-list">{items}</ul>
        </div>
    </section>"""


def test_yourself_section(lesson, level_slug, ty_anchor):
    if not ty_anchor:
        return ""
    return f"""<section id="lesson-test-yourself" class="section section--tight" aria-labelledby="lesson-ty-heading">
        <div class="section__inner section__inner--narrow" style="text-align:center;">
            <p class="eyebrow">Te Ipsum Proba</p>
            <h2 id="lesson-ty-heading">Visne scientiam tuam probare?</h2>
            <p style="color:var(--color-text-muted);max-width:56ch;margin:0 auto var(--space-md);">Confice totam recognitionem &ldquo;Te Ipsum Proba&rdquo; Gradus {lesson['level']} de hoc argumento &mdash; plures quaestiones, mixtae, cum responso statim.</p>
            <a class="btn btn--accent" href="test-yourself.html#{ty_anchor}">Te Ipsum Proba: {escg(lesson['title'])} {ARROW_SVG}</a>
        </div>
    </section>"""


def related_section(lesson, level_slug, prev_lesson, next_lesson):
    prev_link = (
        f'<a class="btn btn--ghost" href="{prev_lesson["slug"]}.html">{ARROW_SVG} Prior: {escg(prev_lesson["title"])}</a>'
        if prev_lesson else ""
    )
    next_link = (
        f'<a class="btn btn--accent" href="{next_lesson["slug"]}.html">Proximum: {escg(next_lesson["title"])} {ARROW_SVG}</a>'
        if next_lesson else ""
    )
    return f"""<section id="related" class="section section--surface" aria-labelledby="rel-heading">
        <div class="section__inner">
            <p class="eyebrow">Proximum</p>
            <h2 id="rel-heading">Perge</h2>
            <div class="lesson-nav">
                {prev_link}
                <a class="btn btn--ghost" href="../{level_slug}.html">Redi ad Gradum {lesson['level']}</a>
                {next_link}
            </div>
        </div>
    </section>"""


def build(lesson_path: Path):
    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    level_slug = LEVEL_SLUGS[lesson["level"]]
    id_prefix = lesson["level"].lower() + "-"  # lesson ids use the level CODE prefix (i-, ii-...), not the slug
    lesson_slug = lesson["id"][len(id_prefix):] if lesson["id"].startswith(id_prefix) else lesson["id"]

    title = f"{lesson['title']} — Gradus {lesson['level']} — Mathemata Hellenika"
    description = f"{lesson['title']}: {lesson['subtitle']}"[:300]
    breadcrumb = (
        f'<li><a href="{REL}index.html">Domus</a></li>'
        f'<li aria-current="page">Gradus</li>'
        f'<li><a href="../{level_slug}.html">Gradus {lesson["level"]}</a></li>'
        f'<li aria-current="page">{escg(lesson["title"])}</li>'
    )

    sections = {
        "objectives": objectives_section(lesson),
        "explanation": explanation_section(lesson),
        "rules": rules_section(lesson),
        "examples": examples_section(lesson),
        "mistakes": mistakes_section(lesson),
        "practice": practice_section(lesson),
        "summary": summary_section(lesson),
    }
    present_ids = [k for k, v in sections.items() if v]

    nav_map = json.loads(NAV_MAP_PATH.read_text(encoding="utf-8")) if NAV_MAP_PATH.exists() else {}
    nav_list = nav_map.get(level_slug, [])
    pos = next((i for i, l in enumerate(nav_list) if l["slug"] == lesson_slug), None)
    prev_lesson = nav_list[pos - 1] if pos is not None and pos > 0 else None
    next_lesson = nav_list[pos + 1] if pos is not None and pos < len(nav_list) - 1 else None
    ty_anchor = nav_list[pos]["ty"] if pos is not None else None
    toc_ids = present_ids + (["lesson-test-yourself"] if ty_anchor else [])

    out = []
    out.append(site_chrome.head(REL, title, description))
    out.append(site_chrome.header(REL, lesson["level"], breadcrumb))
    out.append(page_header(lesson))
    out.append(toc(toc_ids))
    for k in present_ids:
        out.append(sections[k])
    out.append(test_yourself_section(lesson, level_slug, ty_anchor))
    out.append(related_section(lesson, level_slug, prev_lesson, next_lesson))
    out.append(site_chrome.footer(REL))

    out_dir = REPO_ROOT / "gradus" / level_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{lesson_slug}.html"
    out_path.write_text("\n".join(out), encoding="utf-8")
    print(f"Built {out_path.relative_to(REPO_ROOT)}")
    return out_path


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        build(Path(arg))
