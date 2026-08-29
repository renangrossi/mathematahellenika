#!/usr/bin/env python3
"""
Build the hand-designed top-level pages that don't come from a
curriculum/*.json lesson: index.html, lexicon.html, exercitationes.html,
and varia.html. Each still goes through site_chrome.head/header/footer
(unlike the sibling Latin course, where index.html and lexicon.html are
hand-authored files that happen to duplicate that markup by hand) so the
header/search-overlay/footer markup has exactly one source of truth even
for these one-off pages -- only the <main> content below is unique to
each page.

exercitationes.html indexes all seven Gradus overview pages now that
the curriculum is complete (see build_exercitationes() below). varia.html
remains a short, honest "not yet written" stub -- it covers bonus
material (mythology, history, proverbs, dialect notes) that's separate
from the graded curriculum and was never in scope for the curriculum
build; see gradus/auctores.html for the dialect notes that did get
written as part of Gradus VII proper. Both still render through the
same chrome so nav never 404s.

Usage:
    python3 scripts/build_static_pages.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_chrome  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

ARROW_SVG = '<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
SEARCH_SVG = '<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'


def write(name, main_html, title, description):
    out = []
    out.append(site_chrome.head("", title, description))
    breadcrumb = f'<li aria-current="page">{name.replace(".html", "").capitalize()}</li>' if name != "index.html" else '<li aria-current="page">Domus</li>'
    out.append(site_chrome.header("", "", breadcrumb))
    out.append(main_html)
    out.append(site_chrome.footer(""))
    path = REPO_ROOT / name
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"Built {name}")


# ---------------------------------------------------------------------
# index.html
# ---------------------------------------------------------------------

GRAMMAR_CARDS = [
    ("I", "fundamenta", "Alphabētum, Spīritūs, Εἰμί", "Alphabētum Graecum, prōnūntiātiō Attica reconstrūcta, spīritūs et accentūs, salūtātiōnēs, verbum εἰμί."),
    ("II", "elementa", "Dēclīnātiō I–II et Articulus", "Nōmina prīmae/secundae dēclīnātiōnis, articulus plēnus, adiectīva, tempus praesēns verbōrum in -ω."),
    ("III", "progressus", "Dēclīnātiō III et Verba Contracta", "Nōmina tertiae dēclīnātiōnis, verba contracta, tempora imperfectum/futūrum, vōx media incipiēns."),
    ("IV", "media", "Systema Aoristī et Participia", "Aoristus, perfectum, participia, īnfīnītīvī, verba dēpōnentia."),
    ("V", "provectus", "Coniūnctīvus et Optātīvus", "Modus coniūnctīvus et optātīvus, clausulae fīnālēs/cōnsecūtīvae, condiciōnēs."),
    ("VI", "altior", "Syntaxis Prōvectior", "Ōrātiō oblīqua plēna, adiectīva verbālia, ōrdō verbōrum, prōsa Graeca adaptāta."),
    ("VII", "auctores", "Auctōrēs Authenticī", "Xenophōn, Platō, Lȳsiās, excerpta Homērica, excerpta ē Novō Testāmentō."),
]

LADDER = [
    ("I", "Fundamenta", "Alphabētum, prōnūntiātiō, spīritūs, accentūs, salūtātiōnēs, εἰμί. Nūlla scientia Graeca prior praesūmitur.", "fundamenta"),
    ("II", "Elementa", "Dēclīnātiō prīma/secunda, articulus, tempus praesēns, adiectīva fundāmentālia.", "elementa"),
    ("III", "Prōgressus", "Dēclīnātiō tertia, verba contracta, imperfectum/futūrum, vōx media incipiēns.", "progressus"),
    ("IV", "Media", "Systema aoristī et perfectī, participia, īnfīnītīvī, verba dēpōnentia.", "media"),
    ("V", "Prōvectus", "Coniūnctīvus plēnus, optātīvus, clausulae subōrdinātae, condiciōnēs.", "provectus"),
    ("VI", "Altior", "Syntaxis prōvectior; prōsa Graeca classica adaptāta legitur.", "altior"),
    ("VII", "Auctōrēs", "Textūs authenticī nōn adaptātī: Xenophōn, Platō, Lȳsiās, Homērus, Novum Tēstāmentum.", "auctores"),
]


def build_index():
    grammar_cards_html = "".join(
        f"""<article class="lesson-card">
                    <span class="lesson-card__index" aria-hidden="true">{code}</span>
                    <h3><a class="lesson-card__title-link" href="gradus/{slug}.html">{title}</a></h3>
                    <p>{desc}</p>
                    </article>"""
        for code, slug, title, desc in GRAMMAR_CARDS
    )
    ladder_html = "".join(
        f"""<li class="ladder__rung">
                <span class="ladder__code" aria-hidden="true">{code}</span>
                <div class="ladder__body">
                    <h3>{name}</h3>
                    <p>{desc} <a class="ladder__link" href="gradus/{slug}.html">Intrā gradum {ARROW_SVG}</a></p>
                </div>
            </li>"""
        for code, name, desc, slug in LADDER
    )

    # No leading <main> here: site_chrome.header() (called from write())
    # already emits the opening <main id="main-content" class="site-main">
    # tag as its last line -- see the same fix/comment in
    # build_progress_stub() below for the full explanation.
    main = f"""<section class="hero" id="mission">
        <div class="hero__inner">
            {site_chrome.MEANDER_ROW}
            <div class="hero__split">
                <div>
                    <p class="eyebrow hero__eyebrow">Fundāta Annō MMXXVI</p>
                    <h1>Salvē apud Māthēmata Hellēnika</h1>
                    <p class="hero__lede">Cursus līber Graecitātis Classicae (Atticae potissimum, cum notīs dē dialectō Homēricā et Koinē ubi ūtile), Latīnē explicātus, ā prīmō alphabētō usque ad auctōrēs authenticōs nōn adaptātōs.<br>Perge, gradū post gradum.</p>
                    <div class="hero__actions">
                        <a class="btn btn--accent" href="gradus/fundamenta.html">Incipe cum Gradū I {ARROW_SVG}</a>
                        <a class="btn btn--ghost-inverse" href="#gradus-ladder">Vidē Septem Gradūs</a>
                    </div>
                </div>
            </div>
        </div>
    </section>
    <hr class="rule">
<section id="de-lingua" class="section" aria-labelledby="de-lingua-heading">
        <div class="section__inner section__inner--narrow">
            <p class="eyebrow">De Lingua</p>
            <h2 id="de-lingua-heading">Quid est Graecitās Classica?</h2>
            <p>Graecitās Classica hīc dēsignat prīmāriē <strong>dialectum Atticam</strong> saeculōrum V/IV ante Chrīstum nātum — sermōnem Athēniēnsium, quō Platō, Xenophōn, et Lȳsiās ūsī sunt — cum notīs occāsiōnālibus dē dialectō <strong>Homēricā</strong> (epica, antīquior, in Iliade/Odysseā reperta) et <strong>Koinē</strong> (commūnis, posterior, linguā Novī Tēstāmentī et scrīptōrum Hellēnisticōrum). Nōn est Graecum Neogaecum hodiernum: vocābula, fōrmae grammaticae, et prōnūntiātiō omnēs aetātī Classicae Atticae fīdēliter attribuuntur, dialectīs aliīs tantum ubi pedagogicē ūtile notātīs.</p>
        </div>
    </section>
<section id="pronuntiatio" class="section section--surface" aria-labelledby="pronuntiatio-heading">
        <div class="section__inner section__inner--narrow">
            <p class="eyebrow">Prōnūntiātiō</p>
            <h2 id="pronuntiatio-heading">Cūr Prōnūntiātiō Attica Reconstrūcta?</h2>
            <p>Sīcut cursus Latīnus huius scholae docet prōnūntiātiōnem <strong>reconstructam</strong> (nōn Ecclēsiasticam), hic cursus docet prōnūntiātiōnem Atticam reconstrūctam ex philologiā comparātā — differt notābiliter ā prōnūntiātiōne Neograecā hodiernā (ubi θ φ χ sunt fricātīvae, nōn occlūsīvae aspīrātae; ubi η ι υ ει οι omnēs ferē sonant \"i\"; ubi accentus est sōlum tonicus, nōn ille antīquus mixtus tonō/quantitāte). Ambae sunt authenticae in tempore suō; hic cursus semper distinguit inter <strong>orthographiam</strong> (immūtātam per omnia saecula) et <strong>prōnūntiātiōnem</strong> (variantem). Vidē <a href="gradus/fundamenta.html">Gradum I</a> prō tractātiōne plēnā.</p>
        </div>
    </section>
<section id="grammatica" class="section section--surface" aria-labelledby="grammar-heading">
        <div class="section__inner">
            <div class="section__head">
                <p class="eyebrow">Grammatica</p>
                <h2 id="grammar-heading">Septem gradūs, ūnus per cardinem grammaticum</h2>
                <p>Cōnspectus tōtīus grammaticae Graecae plānificātae in hōc cursū, ā prīmō alphabētō ad ōrātiōnem oblīquam plēnam — ūtile ad recognitiōnem rapidam iūxtā lēctiōnēs gradū post gradum īnfrā. Sōlum Gradus I hodiē lēctiōnēs scrīptās habet; cēterī monstrant cōnsilium nostrum (vidē etiam <code>docs/gradus-mapping.md</code>).</p>
            </div>
            <div class="grid">{grammar_cards_html}</div>
        </div>
    </section>
<section id="gradus-ladder" class="section section--surface" aria-labelledby="ladder-heading">
        <div class="section__inner">
            <div class="section__head section__head--center">
                <p class="eyebrow">Iter Tuum, Gradū Post Gradum</p>
                <h2 id="ladder-heading">Septem Gradūs</h2>
                <p>Ā prīmō alphabētō ad auctōrēs authenticōs — quisque gradus super priōrem aedificat. Approximātē: Gradūs I&ndash;II respondent nivellīs \"Prae-A1/A1\" cursuum modernōrum, III \"A2\", IV \"B1\", V \"B2\", VI \"C1\", VII \"C2\" &mdash; vidē <code>docs/gradus-mapping.md</code> prō tabulā plēnā et explicātā. Hic cursus tamen ōrdinem proprium pedagogicum sequitur, aptum Graecitātī, nōn sȳstēma externum rigidē secūtum.</p>
            </div>
            <ol class="ladder">{ladder_html}</ol>
        </div>
    </section>
<section id="praecepta" class="section" aria-labelledby="skills-heading">
        <div class="section__inner">
            <div class="section__head section__head--center">
                <p class="eyebrow">Cōnsilium Plēnum</p>
                <h2 id="skills-heading">Omnis ars, comprehēnsa</h2>
                <p>Quisque gradus (ubi scrīptus) easdem artēs colit, ut nihil fortūnae relinquātur.</p>
            </div>
            <div class="grid grid--4"><a class="skill-card" href="index.html#grammatica">
                <svg class="skill-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 5.5C3 4.7 3.7 4 4.5 4H10a2 2 0 0 1 2 2v14a1.5 1.5 0 0 0-1.5-1.5H4.5A1.5 1.5 0 0 1 3 17V5.5Z"/><path d="M21 5.5c0-.8-.7-1.5-1.5-1.5H14a2 2 0 0 0-2 2v14a1.5 1.5 0 0 1 1.5-1.5h5.5a1.5 1.5 0 0 0 1.5-1.5V5.5Z"/></svg>
                <h3>Grammatica</h3>
                <p>Rēgulae ōrdinātae per gradum, iūnctae semper cum exercitātiōnibus in eādem pāginā.</p>
            </a><div class="skill-card">
                <svg class="skill-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19V6.5A2.5 2.5 0 0 1 6.5 4H8"/><path d="M4 13h4"/><path d="M14 19V6.5A2.5 2.5 0 0 1 16.5 4H20"/><path d="M14 13h4"/></svg>
                <h3>Vocābulārium</h3>
                <p>Verba thematica quae cum grammaticā crēscunt, ā prīmīs salūtātiōnibus ad idiōmata Attica.</p>
            </div><a class="skill-card" href="exercitationes.html">
                <svg class="skill-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                <h3>Exercitātiōnēs</h3>
                <p>Exercitātiōnēs variī generis: fōrmae, parsing, iūnctiō, ōrdinātiō verbōrum, vēra/falsa.</p>
            </a><div class="skill-card">
                <svg class="skill-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/></svg>
                <h3>Lectiō</h3>
                <p>Ā verbīs singulīs ad textūs prōgressīvē magis authenticōs, quī grammaticam in contextū pōnunt.</p>
            </div><a class="skill-card" href="gradus/fundamenta.html">
                <svg class="skill-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z"/><path d="M19 11a7 7 0 0 1-14 0"/><path d="M12 18v3"/><path d="M9 21h6"/></svg>
                <h3>Prōnūntiātiō</h3>
                <p>Exercitātiōnēs scrīptae dē spīritū, accentū, et quantitāte vōcālium &mdash; sine audiō, cum guberniīs phonēticīs plēnīs.</p>
            </a><div class="skill-card">
                <svg class="skill-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 22c4-1 8-3 10-5"/><path d="M22 2c-8 0-16 4-16 14 0 2 2 4 4 4C20 20 22 10 22 2Z"/></svg>
                <h3>Scriptiō</h3>
                <p>Exercitātiōnēs scrībendī, ā sententiīs singulīs ad compositiōnem līberam Graecam.</p>
            </div><div class="skill-card">
                <svg class="skill-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 12h.01"/><path d="M12 12h.01"/><path d="M16 12h.01"/><path d="M21 12a9 9 0 1 1-9-9c4.97 0 9 3.582 9 8Z"/></svg>
                <h3>Locūtiō</h3>
                <p>Dialogī scrīptī quōs legere et imitārī potes, prō praxī locūtiōnis sine audiō.</p>
            </div><a class="skill-card" href="gradus/fundamenta/test-yourself.html">
                <svg class="skill-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="15" r="6"/><path d="m9 10-3-7"/><path d="m15 10 3-7"/><path d="M9.5 15.5 12 17l2.5-1.5"/></svg>
                <h3>Recognitiō</h3>
                <p>\"Tē Ipsum Probā\": recognitiō cumulātīva per gradum, mixtīs omnibus argūmentīs.</p>
            </a></div>
        </div>
    </section>
<section id="consilium" class="section section--surface" aria-labelledby="why-heading">
        <div class="section__inner">
            <div class="section__head section__head--center">
                <p class="eyebrow">Cōnsilium Nostrum</p>
                <h2 id="why-heading">Cursus fideī dignus</h2>
            </div>
            <div class="grid grid--3" style="max-width:70rem;margin:0 auto;"><div class="card card--feature">
                <span class="card__icon"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m15 9-2 6-6 2 2-6 6-2Z"/></svg></span>
                <h3>Ōrdinātus per Gradūs</h3>
                <p>Quaeque lēctiō in locō suō pōnitur, ita ut semper sciās ubi stēs et quid sequātur.</p>
            </div><div class="card card--feature">
                <span class="card__icon"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg></span>
                <h3>Disce Tuō Rhythmō</h3>
                <p>Perge per gradum ōrdine, aut salta ad argūmentum quod nunc opus est.</p>
            </div><div class="card card--feature">
                <span class="card__icon"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.5 2.5 4 5.7 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.7-4-9s1.5-6.5 4-9Z"/></svg></span>
                <h3>Graecitās Authentica</h3>
                <p>Ā prīmō gradū ad ultimum, exempla cōnstanter linguisticē corrēcta &mdash; et in Gradū VII, verba ipsa Xenophōntis, Platōnis, Homērī, sine adaptātiōne.</p>
            </div></div>
        </div>
    </section>
<section class="cta-band" aria-labelledby="cta-heading">
        {site_chrome.MEANDER_ROW_GOLD}
        <p class="eyebrow" style="justify-content:center;">Parātus incipere?</p>
        <h2 id="cta-heading">Perge iter tuum per Graecitātem Classicam.</h2>
        <p>Nūlla scientia Graeca prior necessāria est &mdash; Gradus I incipit ab ipsō alphabētō.</p>
        <div class="hero__actions">
            <a class="btn btn--accent" href="gradus/fundamenta.html">Incipe cum Gradū I {ARROW_SVG}</a>
            <a class="btn btn--ghost-inverse" href="#gradus-ladder">Omnēs gradūs vidē</a>
        </div>
    </section>"""
    write(
        "index.html", main,
        "Mathemata Hellenika — Schola Graecitatis Classicae",
        "Cursus liber Graecitatis Classicae (Atticae potissimum), Latine explicatus, a primo alphabeto usque ad auctores authenticos non adaptatos.",
    )


# ---------------------------------------------------------------------
# lexicon.html
# ---------------------------------------------------------------------

def dict_card(feature, title, desc, url_template, example_word="λόγος"):
    import urllib.parse
    example_url = url_template.replace("{word}", urllib.parse.quote(example_word))
    cls = "card card--feature dict-card" if feature else "card dict-card"
    return f"""<div class="{cls}" data-url-template="{url_template}">
                        <h3 class="greek">{title}</h3>
                        <p>{desc}</p>
                        <a class="btn btn--accent btn--small dict-card__link" data-dict-link href="{example_url}" target="_blank" rel="noopener">{ARROW_SVG}Quaere</a>
                    </div>"""


def build_lexicon():
    core = "".join([
        dict_card(True, "Logeion", "Aggregat LSJ (Liddell-Scott-Jones) et alia lexica Graeca et Latina in ūnā pāginā rapidā, ab Universitāte Chicagiēnsī.", "https://logeion.uchicago.edu/{word}"),
        dict_card(True, "Perseus (Word Study Tool)", "Analyzat fōrmam ipsam quam scrībis (nōn sōlum lemma) et dat omnēs parsing possibilēs, cum ligāminibus ad LSJ plēnum.", "https://www.perseus.tufts.edu/hopper/morph?la=greek&word={word}"),
        dict_card(True, "Wiktionary (Ἑλληνική)", "Victiōnārium Anglicum, sectiō \"Ancient Greek\" — dēfīnītiōnēs breves, plūrālēs linguae metae.", "https://en.wiktionary.org/wiki/{word}#Ancient_Greek"),
    ])
    secondary = "".join([
        dict_card(False, "Scaife Viewer", "Ambiens legendī līberum (Perseus/Open Greek and Latin) cum verbīs texuī iūnctīs ad lexicōn statim.", "https://scaife.perseus.org/library/?q={word}"),
    ])

    # No leading <main> here either -- see build_index()'s comment above.
    main = f"""<div class="page-header">
        {site_chrome.MEANDER_ROW}
        <div class="page-header__inner">
            <div class="page-header__text">
                <p class="eyebrow hero__eyebrow">Fontes Externī</p>
                <h1>Lexicon</h1>
                <p class="page-header__lede">Scrībe verbum Graecum (cum vel sine accentibus) et quaere illud statim in lexicīs praecipuīs Graecīs līneīs.</p>
            </div>
        </div>
    </div>
    <section class="section section--surface" aria-labelledby="lex-heading">
        <div class="section__inner section__inner--narrow" style="text-align:center;">
            <h2 id="lex-heading" class="visually-hidden">Quaere verbum</h2>
            <input type="text" id="dict-word" class="dict-input" placeholder="Scribe verbum, e.g. &ldquo;λόγος&rdquo;" autocomplete="off" data-dict-word>
        </div>
    </section>
    <section class="section" aria-labelledby="lex-core-heading">
        <div class="section__inner">
            <div class="section__head">
                <p class="eyebrow">Praecipua</p>
                <h2 id="lex-core-heading">Lexica Prīncipālia</h2>
            </div>
            <div class="grid">{core}</div>
        </div>
    </section>
    <section class="section section--surface" aria-labelledby="lex-extra-heading">
        <div class="section__inner">
            <div class="section__head">
                <p class="eyebrow">Amplius</p>
                <h2 id="lex-extra-heading">Instrūmenta Legendī</h2>
            </div>
            <div class="grid">{secondary}</div>
        </div>
    </section>
    <section class="section section--tight" aria-labelledby="lex-note-heading">
        <div class="section__inner section__inner--narrow">
            <p class="eyebrow">Nota</p>
            <h2 id="lex-note-heading" class="visually-hidden">Nota dē Instrumentō Volitante</h2>
            <p style="color:var(--color-text-muted);">Instrūmentum lexicī volitāns (icōn librī, angulō dextrō īnferiōre huius et omnis pāginae) offert dēfīnītiōnem brevem sine hāc pāginā relinquendā, ex Victiōnāriō, cum hīsdem ligāminibus ad Logeion/Perseus/Wiktionary īnfrā sī plūra opus est. Vidē <code>docs/fonts-and-input.md</code> prō notīs dē modō scrībendī Graecum polytonicum.</p>
        </div>
    </section>"""
    write(
        "lexicon.html", main,
        "Lexicon — Mathemata Hellenika",
        "Quaere verba Graeca in Logeion, Perseus, et Wiktionary — lexica praecipua Graeca linea.",
    )


# ---------------------------------------------------------------------
# exercitationes.html / varia.html -- short, honest "in progress" hubs
# ---------------------------------------------------------------------

def build_progress_stub(name, eyebrow, title, body_html, title_tag, desc):
    # No leading <main> here: site_chrome.header() (called from write())
    # already emits the opening <main id="main-content" class="site-main">
    # tag as its last line -- repeating it here produced a duplicate,
    # malformed <main><main> pair in the generated page (a pre-existing
    # bug in this stub helper, fixed here rather than left in place).
    main = f"""<div class="page-header">
        {site_chrome.MEANDER_ROW}
        <div class="page-header__inner">
            <div class="page-header__text">
                <p class="eyebrow hero__eyebrow">{eyebrow}</p>
                <h1>{title}</h1>
            </div>
        </div>
    </div>
    <section class="section section--surface" aria-labelledby="stub-heading">
        <div class="section__inner section__inner--narrow" style="text-align:center;">
            <h2 id="stub-heading" class="visually-hidden">{title}</h2>
            {body_html}
            <a class="btn btn--accent" href="gradus/fundamenta.html">Ad Gradum I: Fundamenta {ARROW_SVG}</a>
        </div>
    </section>"""
    write(name, main, title_tag, desc)


def build_exercitationes():
    cards = "".join(
        f"""<a class="lesson-card" href="gradus/{slug}.html" style="text-align:left;display:block;text-decoration:none;">
                    <span class="lesson-card__index" aria-hidden="true">{code}</span>
                    <h3 class="lesson-card__title-link">Gradus {code} &mdash; {name}</h3>
                    <p>{site_chrome.LEVEL_DESC.get(code, "")}</p>
                </a>"""
        for code, name, slug in site_chrome.LEVELS
    )
    # No leading <main> here either -- see the comment in
    # build_progress_stub() above for why.
    main = f"""<div class="page-header">
        {site_chrome.MEANDER_ROW}
        <div class="page-header__inner">
            <div class="page-header__text">
                <p class="eyebrow hero__eyebrow">Per Omnes Gradūs</p>
                <h1>Exercitationes</h1>
                <p class="page-header__lede">Quaeque lectio, in omnibus septem gradibus, iam continet
                exercitātiōnēs suās interactīvās (ēlēctiō multiplex, complēmentum spatiōrum, iūnctiō,
                vērum/falsum) &mdash; ēlige gradum tuum īnfrā ut incipiās.</p>
            </div>
        </div>
    </div>
    <section class="section section--surface" aria-labelledby="grad-heading">
        <div class="section__inner">
            <h2 id="grad-heading" class="visually-hidden">Gradūs</h2>
            <div class="grid">{cards}</div>
        </div>
    </section>"""
    write(
        "exercitationes.html", main,
        "Exercitationes — Mathemata Hellenika",
        "Exercitationes interactivae per omnes septem gradus, ab alphabeto usque ad auctores.",
    )


def build_varia():
    body = """<p style="color:var(--color-text-muted);max-width:56ch;margin:0 auto var(--space-md);">
                Hic locus futurus est pro rebus additiciis: mythologia Graeca, historia Attica, proverbia
                et sententiae (γνῶμαι) auctorum Graecorum, notae de dialecto Homerica et Koine. Nondum
                scriptus in hoc primo schemate operis -- vide gradus/auctores.html pro consilio nostro
                de auctoribus et dialectis futuris.</p>"""
    build_progress_stub(
        "varia.html", "Mox Futurum", "Varia",
        body,
        "Varia — Mathemata Hellenika",
        "Res additiciae de cultu et lingua Graeca -- in praeparatione.",
    )


if __name__ == "__main__":
    build_index()
    build_lexicon()
    build_exercitationes()
    build_varia()
