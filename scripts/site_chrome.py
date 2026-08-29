"""
Shared page chrome (head/header/nav/search-overlay/footer) for generated
pages -- adapted from the sibling Latin-course project's
scripts/site_chrome.py (itself adapted from the English course's) so a
generated page is structurally consistent site-wide. Only the
lesson-specific <main> content differs page to page; see build_lesson.py.

Deliberate differences from the Latin original:
  - Brand is "Mathemata Hellenika" / "Schola Graecitatis Classicae", not
    "Lectiones Latinae" / "Latinitatis Classicae Schola".
  - The AI-teacher toggle/panel/script is still called "Magister AI" (kept
    identical across all three sibling sites as a recognizable feature
    name) but its endpoint, system prompt and course catalog are this
    course's own -- see worker/README.md. The intro animation is a
    spinning Athenian owl tetradrachm instead of a waving SPQR vexillum.
  - "laurel-row" (a row of laurel sprigs, itself the Latin course's
    replacement for the English course's stars-row) -> "meander-row" (a
    row of Greek-key units), matching components.css's rename. See
    MEANDER_PATH below.
  - Fonts: Cormorant Garamond for display headings (in place of the Latin
    course's Cinzel) plus Cardo, loaded specifically for GREEK-SCRIPT
    text (breathings/accents/iota-subscript need a font built for
    classicists -- see docs/fonts-and-input.md).
  - Every UI string is still Latin -- this course's metalanguage is Latin
    too (see the project brief's "Pedagogical language policy"), so the
    vast majority of site_chrome's copy carries over unchanged from the
    Latin course; only brand name, nav copy tied to not-yet-built pages,
    and the AI-teacher panel's example prompts needed real edits.
  - LEVELS/LEVEL_EYEBROW/LEVEL_DESC describe Greek grammar topics, but the
    seven Gradus codes/names/slugs are IDENTICAL Latin words to the Latin
    course's own (Fundamenta..Auctores) -- this is deliberate (see
    docs/gradus-mapping.md), not a naming collision to fix.

REL is the relative path prefix from the generated file back to the repo
root, e.g. "../../" for gradus/{level}/{lesson}.html (two levels deep).
"""

LEVELS = [
    ("I", "Fundamenta", "fundamenta"),
    ("II", "Elementa", "elementa"),
    ("III", "Progressus", "progressus"),
    ("IV", "Media", "media"),
    ("V", "Provectus", "provectus"),
    ("VI", "Altior", "altior"),
    ("VII", "Auctores", "auctores"),
]

# Single source of truth for level-overview-page copy, shared by
# build_level_page.py and build_exercise_index.py (search index).
LEVEL_EYEBROW = {
    "I": "Prima Itinera", "II": "Grammatica Fundamentalis", "III": "Elementa Aucta",
    "IV": "Systema Verbi", "V": "Syntaxis Provectior", "VI": "Prosa Adaptata",
    "VII": "Auctores Authentici",
}
LEVEL_DESC = {
    "I": "Alphabetum, pronuntiatio Attica reconstructa, spiritus, accentus, et prima verba. Nulla scientia Graeca prior praesumitur.",
    "II": "Declinatio prima et secunda, articulus, tempus praesens verborum in -ω, adiectiva fundamentalia.",
    "III": "Declinatio tertia, verba contracta, tempus imperfectum, tempus futurum; vox media incipiens.",
    "IV": "Systema aoristi, systema perfecti, participia, infinitivi, verba deponentia.",
    "V": "Modus coniunctivus, modus optativus, clausulae finales et consecutivae, condiciones.",
    "VI": "Syntaxis provectior, oratio obliqua, adiectiva verbalia, prosa Graeca adaptata.",
    "VII": "Auctores authentici non adaptati: Xenophon, Plato, Lysias, excerpta Homerica, exempla e Novo Testamento.",
}

MEANDER_PATH = (
    '<path d="M2 3h4v4H2V3Zm4 4h4V3H6v4Zm0 0v4h4V7H6Zm4 4h4V7h-4v4Zm4-4V3h-4v4h4Z"/>'
)
MEANDER = f'<svg class="meander-row__unit" viewBox="0 0 16 12" fill="currentColor" aria-hidden="true">{MEANDER_PATH}</svg>'
MEANDER_ROW = f'<div class="meander-row meander-row--onlight" aria-hidden="true">{MEANDER * 15}</div>'
MEANDER_ROW_GOLD = f'<div class="meander-row meander-row--gold" aria-hidden="true">{MEANDER * 15}</div>'


def nav_levels_html(rel, active_level_code):
    items = []
    for code, name, slug in LEVELS:
        current = ' aria-current="page"' if code.upper() == (active_level_code or "").upper() else ""
        items.append(
            f'<li><a href="{rel}gradus/{slug}.html"{current}><span>{name}</span>'
            f'<span class="level-code">{code}</span></a></li>'
        )
    return "".join(items)


def head(rel, title, description):
    return f"""<!DOCTYPE html>
<html lang="la">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Mathemata Hellenika">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<link rel="icon" href="{rel}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cardo:ital,wght@0,400;0,700;1,400&family=Cormorant+Garamond:wght@500;600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/css/tokens.css">
<link rel="stylesheet" href="{rel}assets/css/base.css">
<link rel="stylesheet" href="{rel}assets/css/components.css">
<link rel="stylesheet" href="{rel}assets/css/layout.css">
<link rel="stylesheet" href="{rel}assets/css/dark-mode.css">
<link rel="stylesheet" href="{rel}assets/css/ai-teacher.css">
<link rel="stylesheet" href="{rel}assets/css/search.css">
<link rel="stylesheet" href="{rel}assets/css/exercises.css"><link rel="stylesheet" href="{rel}assets/css/lessons.css">
<script>
(function(){{try{{var t=localStorage.getItem('theme');if(!t){{t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}}document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
</head>"""


def header(rel, active_level_code, breadcrumb_html):
    return f"""<body class="" data-level-code="{active_level_code}">
    <a class="skip-link" href="#main-content">Ad contentum transi</a>
    <header class="site-header">
        <div class="site-header__bar">
            <a class="brand" href="{rel}index.html">
                <img class="brand__mark" src="{rel}assets/img/favicon.svg" alt="" width="38" height="38" loading="lazy">
                <span class="brand__text">
                    <span class="brand__name">Mathemata Hellenika</span>
                    <span class="brand__tagline">Schola Graecitatis Classicae</span>
                </span>
            </a>
            <nav class="primary-nav" id="primary-nav" role="navigation" aria-label="Navigatio Praecipua">
                <ul class="primary-nav__list">
                <li><a href="{rel}index.html">Domus</a></li>
                <li><a href="{rel}index.html#grammatica">Grammatica</a></li>
                <li class="nav-drop">
                    <button type="button" class="nav-drop__toggle" aria-haspopup="true" aria-expanded="false">
                        Gradus <span class="nav-drop__caret" aria-hidden="true"></span>
                    </button>
                    <ul class="nav-drop__menu" role="menu">
                    {nav_levels_html(rel, active_level_code)}
                    </ul>
                </li>
                <li><a href="{rel}exercitationes.html">Exercitationes</a></li>
                <li><a href="{rel}varia.html">Varia</a></li>
                <li><a href="{rel}lexicon.html">Lexicon</a></li>
                <li class="nav-sibling"><a href="https://renangrossi.github.io/lectioneslatinae/" lang="la">Lectiones Latinae</a></li>
                </ul>
            </nav>
            <div class="nav-utility">
                <button type="button" class="theme-toggle" data-search-toggle aria-label="Quaere in situ" aria-haspopup="dialog">
                    <svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
                </button>
                <button type="button" class="theme-toggle" data-theme-toggle aria-label="Ad modum obscurum verte">
                    <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
                    <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z"/></svg>
                </button>
                <button type="button" class="nav-toggle" data-nav-toggle aria-label="Aperi indicem" aria-expanded="false" aria-controls="primary-nav">
                    <span class="nav-toggle__icon"></span>
                </button>
            </div>
        </div>
    </header>
    <div class="search-overlay" data-search-overlay hidden>
        <div class="search-modal" role="dialog" aria-modal="true" aria-label="Inquisitio Situs" data-index-src="{rel}assets/data/search-index.json">
            <div class="search-modal__bar">
                <svg class="search-modal__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
                <input type="search" class="search-modal__input" data-search-input placeholder="Quaere lectiones, grammaticam, vocabularium, exercitationes&hellip;" aria-label="Quaerere">
                <button type="button" class="search-modal__close" data-search-close aria-label="Occlude inquisitionem"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="M6 6l12 12"/></svg></button>
            </div>
            <div class="search-modal__results" data-search-results>
                <p class="search-modal__hint">Scribe saltem duas litteras ut per omnes gradus, lectiones, argumenta grammatica, et exercitationes quaeras.</p>
            </div>
        </div>
    </div>
    <nav class="breadcrumbs" aria-label="Vestigia">
        <ol>
        {breadcrumb_html}
        </ol>
    </nav>
    <main id="main-content" class="site-main">"""


def footer(rel):
    return f"""<button type="button" class="dict-widget-toggle" data-dict-widget-toggle aria-label="Aperi lexicon breve" aria-expanded="false" aria-haspopup="dialog">
        <svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/></svg>
    </button>
    <div class="dict-widget-panel" data-dict-widget-panel hidden>
        <div class="dict-widget__bar">
            <input type="text" data-dict-widget-input placeholder="Verbum quaere&hellip;" aria-label="Verbum quaere">
            <button type="button" class="dict-widget__close" data-dict-widget-close aria-label="Occlude lexicon"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="M6 6l12 12"/></svg></button>
        </div>
        <div class="dict-widget__result" data-dict-widget-result>
            <p class="dict-widget__hint">Verbum scribe ut definitionem sine hac pagina relinquenda videas.</p>
        </div>
        <div class="dict-widget__links" data-dict-widget-links></div>
    </div>
    </main>
    <footer class="site-footer">
        <div class="site-footer__inner">
            <div>
                <a class="brand" href="{rel}index.html">
                    <img class="brand__mark" src="{rel}assets/img/favicon.svg" alt="" width="38" height="38" loading="lazy">
                    <span class="brand__text">
                        <span class="brand__name">Mathemata Hellenika</span>
                        <span class="brand__tagline">Schola Graecitatis Classicae</span>
                    </span>
                </a>
                <p class="site-footer__blurb">Cursus Graecitatis Classicae (Attica potissimum, cum notis de dialecto Homerica et Koine ubi utile), Latine explicatus, lectione per lectionem diligenter compositus &mdash; ab ipso alphabeto usque ad auctores authenticos.</p>
            </div>
            <div class="footer-col">
                <h4>Gradus</h4>
                <ul>
                    <li><a href="{rel}gradus/fundamenta.html">Gradus I &mdash; Fundamenta</a></li>
                    <li><a href="{rel}gradus/elementa.html">Gradus II &mdash; Elementa</a></li>
                    <li><a href="{rel}gradus/progressus.html">Gradus III &mdash; Progressus</a></li>
                    <li><a href="{rel}gradus/media.html">Gradus IV &mdash; Media</a></li>
                    <li><a href="{rel}gradus/provectus.html">Gradus V &mdash; Provectus</a></li>
                    <li><a href="{rel}gradus/altior.html">Gradus VI &mdash; Altior</a></li>
                    <li><a href="{rel}gradus/auctores.html">Gradus VII &mdash; Auctores</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Exercitium</h4>
                <ul>
                    <li><a href="{rel}index.html#grammatica">Compendia Grammatica</a></li>
                    <li><a href="{rel}exercitationes.html">Exercitationes</a></li>
                    <li><a href="{rel}lexicon.html">Lexicon &amp; Fontes</a></li>
                    <li><a href="{rel}varia.html">Varia</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>De Lingua Graeca</h4>
                <ul>
                    <li><a href="{rel}index.html#de-lingua">Quid est Graecitas Classica?</a></li>
                    <li><a href="{rel}index.html#pronuntiatio">Cur Pronuntiatio Attica?</a></li>
                    <li><a href="{rel}index.html#consilium">Consilium Nostrum</a></li>
                </ul>
            </div>
        </div>
        <div class="site-footer__bottom">
            <p>&copy; Mathemata Hellenika MMXXVI. Omnia iura reservantur.</p>
        </div>
    </footer>
    <button type="button" class="back-to-top back-to-top--with-dict" data-back-to-top aria-label="Ad summum redi">
        <svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5"/><path d="m5 12 7-7 7 7"/></svg>
    </button>
    <button type="button" class="ai-teacher-toggle" data-ai-teacher-toggle aria-label="Interroga Magistrum AI" aria-expanded="false" aria-haspopup="dialog">
        <svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 10-10-5L2 10l10 5 10-5Z"/><path d="M6 12v5c0 1.5 2.5 3 6 3s6-1.5 6-3v-5"/><path d="M22 10v6"/></svg>
        <span class="ai-teacher-toggle__label">Magister AI</span>
    </button>
    <div class="ai-teacher-panel" data-ai-teacher-panel hidden role="dialog" aria-label="Colloquium cum Magistro AI" aria-modal="false">
        <div class="ai-teacher-panel__bar">
            <div class="ai-teacher-panel__brand">
                <svg class="ai-teacher-panel__brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 10-10-5L2 10l10 5 10-5Z"/><path d="M6 12v5c0 1.5 2.5 3 6 3s6-1.5 6-3v-5"/><path d="M22 10v6"/></svg>
                <div>
                    <strong>Magister AI</strong>
                    <span>Interroga de grammatica, vocabulario, vel exercitationibus</span>
                </div>
            </div>
            <button type="button" class="ai-teacher-panel__close" data-ai-teacher-close aria-label="Occlude Magistrum AI"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="M6 6l12 12"/></svg></button>
        </div>
        <div class="ai-teacher-panel__messages" data-ai-teacher-messages role="log" aria-live="polite">
            <div class="ai-teacher-msg ai-teacher-msg--bot">
                <p>Salvē! Tē adiuvāre possum dē linguā Graecā antīquā. Interrogā dē grammaticā, verbīs, vel exercitātiōnibus &mdash; Latīnē, Anglicē, vel Graecē.<br>Exemplum: <em>&ldquo;Explica verbum εἰμί&rdquo;</em> vel <em>&ldquo;Dā mihi exercitātiōnem dē spīritibus.&rdquo;</em></p>
            </div>
        </div>
        <form class="ai-teacher-panel__form" data-ai-teacher-form>
            <label for="ai-teacher-input" class="visually-hidden">Quaestio tua</label>
            <textarea id="ai-teacher-input" data-ai-teacher-input rows="1" maxlength="600" placeholder="Scribe quaestionem tuam&hellip;" required></textarea>
            <button type="submit" class="ai-teacher-panel__send" data-ai-teacher-send aria-label="Mitte quaestionem"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg></button>
        </form>
        <p class="ai-teacher-panel__hint" data-ai-teacher-hint>Respōnsa ab exemplārī AI veniunt et interdum falsa esse possunt &mdash; semper cum māteriā lēctiōnis tuae cōnfer. Nihil quod scrībis post hanc fenestram clausam servātur.</p>
    </div>
    <script src="{rel}assets/js/main.js"></script>
    <script src="{rel}assets/js/search.js"></script>
    <script src="{rel}assets/js/ai-teacher.js" data-ai-endpoint="https://ai-teacher-el.englishclasses.workers.dev"></script>
    <script src="{rel}assets/js/dict-widget.js"></script>
    <script src="{rel}assets/js/progress.js"></script><script src="{rel}assets/js/exercises.js"></script><script src="{rel}assets/js/mastery.js"></script>
</body>
</html>
"""
