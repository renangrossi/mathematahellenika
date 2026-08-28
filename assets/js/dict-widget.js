/*!
 * Mathemata Hellenika — Instrumentum Lexici Volitans (Floating Dictionary Widget)
 * ------------------------------------------------------------------
 * A small floating lookup tool (styled like the back-to-top button),
 * available on every page, so a student can check a word without
 * losing their place.
 *
 * Adapted from the sibling Latin-course project's dict-widget.js, which
 * itself adapted the English course's (dictionaryapi.dev has no Ancient
 * Greek support either, so this also goes straight to the Wiktionary
 * fallback path). One real difference from the Latin version, verified
 * live rather than assumed: Latin ("la") is a top-level key in
 * Wiktionary's REST definition response, but Ancient Greek is NOT — the
 * API only gives top-level keys to languages with their own ISO 639-1
 * two-letter code, and Ancient Greek's code is three-letter ("grc"), so
 * every Ancient Greek section instead lands in the response's "other"
 * bucket, tagged `"language": "Ancient Greek"` (alongside any other
 * lower-traffic language on that page). fetchGreekDefinition() below
 * filters "other" for that tag instead of reading a "grc" key that does
 * not exist. Even so, the REST "definition" endpoint (stricter than the
 * full page) 404s for some real, existing Ancient Greek entries — a
 * known quirk of that endpoint, not something fixable client-side — so
 * this widget always shows the outbound lexicon links regardless of
 * whether an inline definition was found. There is no reliable free
 * source of audio pronunciation or machine-readable accentuation/IPA
 * data for Greek headwords, and this course teaches reconstructed
 * pronunciation in writing rather than by audio (see gradus/i's
 * pronunciation lessons) — so, like the Latin original, this widget has
 * NO audio button and never touches speechSynthesis. The outbound links
 * below the result point to Logeion and the Perseus Greek Word Study
 * Tool (both show full principal parts/morphology and, for Perseus, a
 * parse of the exact inflected form) plus Greek Wiktionary itself, in
 * that fixed order, matching lexicon.html.
 */
(function () {
  "use strict";

  var trigger = document.querySelector("[data-dict-widget-toggle]");
  if (!trigger) return;
  var panel = document.querySelector("[data-dict-widget-panel]");
  var input = panel.querySelector("[data-dict-widget-input]");
  var resultBox = panel.querySelector("[data-dict-widget-result]");
  var closeBtn = panel.querySelector("[data-dict-widget-close]");
  var linksBox = panel.querySelector("[data-dict-widget-links]");

  /* ---------------------------------------------------------------
   * Attention hint — "Lexicon" appears next to the button on load,
   * then drifts up and fades away letter by letter after a few
   * seconds, just to point out the button exists.
   * --------------------------------------------------------------- */
  function showHint() {
    var word = "Lexicon";
    var hint = document.createElement("div");
    hint.className = "dict-widget-hint";
    hint.setAttribute("aria-hidden", "true");
    word.split("").forEach(function (ch) {
      var span = document.createElement("span");
      span.textContent = ch;
      hint.appendChild(span);
    });
    trigger.insertAdjacentElement("beforebegin", hint);

    setTimeout(function () {
      var spans = hint.querySelectorAll("span");
      spans.forEach(function (span, i) {
        setTimeout(function () {
          span.classList.add("is-leaving");
        }, i * 40);
      });
      setTimeout(function () {
        if (hint.parentNode) hint.parentNode.removeChild(hint);
      }, spans.length * 40 + 500);
    }, 2600);
  }
  showHint();

  // Locks the page behind the widget on small phones while it's open.
  var lockedBodyScroll = false;
  function lockBodyScrollForPanel() {
    if (!(window.matchMedia && window.matchMedia("(max-width: 640px)").matches)) return;
    window.__mhPanelLock = (window.__mhPanelLock || 0) + 1;
    lockedBodyScroll = true;
    if (window.__mhPanelLock > 1) return;
    window.__mhPanelLockY = window.scrollY || window.pageYOffset || 0;
    var s = document.body.style;
    s.position = "fixed";
    s.top = "-" + window.__mhPanelLockY + "px";
    s.left = "0";
    s.right = "0";
    s.width = "100%";
  }
  function unlockBodyScrollForPanel() {
    if (!lockedBodyScroll) return;
    lockedBodyScroll = false;
    window.__mhPanelLock = Math.max(0, (window.__mhPanelLock || 1) - 1);
    if (window.__mhPanelLock > 0) return;
    var y = window.__mhPanelLockY || 0;
    var s = document.body.style;
    s.position = "";
    s.top = "";
    s.left = "";
    s.right = "";
    s.width = "";
    window.scrollTo(0, y);
  }

  function toggle(open) {
    var willOpen = open !== undefined ? open : panel.hidden;
    panel.hidden = !willOpen;
    trigger.setAttribute("aria-expanded", String(willOpen));
    if (willOpen) {
      lockBodyScrollForPanel();
      input.focus();
    } else {
      unlockBodyScrollForPanel();
    }
  }

  trigger.addEventListener("click", function (e) {
    e.stopPropagation();
    toggle();
  });
  closeBtn.addEventListener("click", function () { toggle(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) toggle(false);
  });
  var pointerDownOutside = false;
  document.addEventListener("pointerdown", function (e) {
    if (panel.hidden) return;
    pointerDownOutside = !(panel.contains(e.target) || trigger.contains(e.target));
  });
  document.addEventListener("click", function (e) {
    if (panel.hidden) return;
    if (panel.contains(e.target) || trigger.contains(e.target)) return;
    if (!pointerDownOutside) return;
    toggle(false);
  });
  panel.addEventListener("click", function (e) { e.stopPropagation(); });

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = String(s || "");
    return d.innerHTML;
  }

  function renderOutboundLinks(word) {
    var encoded = encodeURIComponent(word || "λόγος");
    // Same fixed order as lexicon.html's core cards. Logeion and Perseus
    // both cover Ancient Greek natively (Logeion aggregates LSJ; Perseus's
    // Word Study Tool parses the exact inflected form when la=greek).
    var sites = [
      ["Logeion", "https://logeion.uchicago.edu/" + encoded],
      ["Perseus (Word Study Tool)", "https://www.perseus.tufts.edu/hopper/morph?la=greek&word=" + encoded],
      ["Wiktionary (Ἑλληνική)", "https://en.wiktionary.org/wiki/" + encoded + "#Ancient_Greek"],
    ];
    linksBox.innerHTML = sites
      .map(function (s) {
        return '<a class="btn btn--ghost btn--small" target="_blank" rel="noopener" href="' + s[1] + '">' + s[0] + "</a>";
      })
      .join("");
  }

  /* ---------------------------------------------------------------
   * Word lookup — tries a few capitalization variants in order,
   * since Wiktionary page titles are case-sensitive (proper nouns
   * like "Ἀθῆναι" are capitalized; ordinary vocabulary is lowercase).
   * The \p{L} Unicode property escape (needs the "u" flag) is used
   * instead of \w, which only matches ASCII letters and would silently
   * find zero "words" to capitalize in a pure-Greek string.
   * --------------------------------------------------------------- */
  function titleCase(s) {
    return s.replace(/\p{L}\S*/gu, function (t) {
      return t.charAt(0).toUpperCase() + t.slice(1).toLowerCase();
    });
  }

  function candidateWords(word) {
    var seen = {};
    var out = [];
    [word, word.toLowerCase(), word.charAt(0).toUpperCase() + word.slice(1).toLowerCase(), titleCase(word)].forEach(function (w) {
      if (w && !seen[w]) {
        seen[w] = true;
        out.push(w);
      }
    });
    return out;
  }

  function stripHtml(s) {
    return String(s || "")
      .replace(/<[^>]+>/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  // Normalizes one Wiktionary REST response into { word, meanings }.
  // Ancient Greek has NO top-level key of its own in the response
  // (that's only given to languages with a two-letter ISO 639-1 code;
  // Greek's Wiktionary code is the three-letter "grc") — every Ancient
  // Greek section instead lands inside the "other" array, each entry
  // tagged `language: "Ancient Greek"`, verified against the live API.
  function fetchGreekDefinition(word) {
    return fetch("https://en.wiktionary.org/api/rest_v1/page/definition/" + encodeURIComponent(word))
      .then(function (res) {
        if (!res.ok) throw new Error("not found: " + word);
        return res.json();
      })
      .then(function (data) {
        var groups = ((data && data.other) || []).filter(function (g) {
          return g.language === "Ancient Greek";
        });
        if (!groups.length) throw new Error("no Ancient Greek entry: " + word);
        return {
          word: word,
          meanings: groups.map(function (g) {
            return {
              partOfSpeech: g.partOfSpeech || "",
              definitions: (g.definitions || []).slice(0, 4).map(function (d) {
                return { definition: stripHtml(d.definition) };
              }),
            };
          }),
        };
      });
  }

  function tryCandidates(candidates, index) {
    index = index || 0;
    if (index >= candidates.length) {
      return Promise.reject(new Error("no candidates matched"));
    }
    return fetchGreekDefinition(candidates[index]).catch(function () {
      return tryCandidates(candidates, index + 1);
    });
  }

  var lookupTimer;
  var lastQuery = "";

  function lookup(word) {
    word = word.trim();
    if (!word) {
      resultBox.innerHTML = '<p class="dict-widget__hint">Verbum scribe et Enter preme, vel paulisper mane postquam scripsisti.</p>';
      linksBox.innerHTML = "";
      return;
    }
    if (word !== lastQuery && window.ProgressTracker && typeof window.ProgressTracker.recordDictionaryUse === "function") {
      window.ProgressTracker.recordDictionaryUse();
    }
    renderOutboundLinks(word);
    resultBox.innerHTML = '<p class="dict-widget__hint">&ldquo;' + escapeHtml(word) + '&rdquo; quaeritur&hellip;</p>';
    lastQuery = word;

    tryCandidates(candidateWords(word))
      .then(function (data) {
        if (lastQuery !== word) return; // a newer query has since started
        renderDefinition(data);
      })
      .catch(function () {
        if (lastQuery !== word) return;
        resultBox.innerHTML =
          '<p class="dict-widget__hint">Nulla definitio automatica inventa pro &ldquo;' + escapeHtml(word) + '&rdquo;. Lexicon infra elige:</p>';
      });
  }

  function renderDefinition(data) {
    resultBox.innerHTML = "";
    var wordRow = document.createElement("div");
    wordRow.className = "dict-widget__word-row";
    var wordEl = document.createElement("span");
    wordEl.className = "dict-widget__word";
    wordEl.textContent = data.word;
    wordRow.appendChild(wordEl);
    resultBox.appendChild(wordRow);

    (data.meanings || []).slice(0, 3).forEach(function (m) {
      var pos = document.createElement("div");
      pos.className = "dict-widget__pos";
      pos.textContent = m.partOfSpeech;
      resultBox.appendChild(pos);
      var list = document.createElement("ol");
      list.className = "dict-widget__defs";
      (m.definitions || []).slice(0, 3).forEach(function (d) {
        var li = document.createElement("li");
        li.textContent = d.definition;
        list.appendChild(li);
      });
      resultBox.appendChild(list);
    });

    var note = document.createElement("p");
    note.className = "dict-widget__hint";
    note.style.marginTop = "0.75em";
    note.textContent = "Vocabularium Anglice a Victionario mutuatum est; pro accentibus, spiritibus, et partibus principalibus plenis, Logeion vel Perseus infra consule.";
    resultBox.appendChild(note);
  }

  input.addEventListener("input", function () {
    clearTimeout(lookupTimer);
    lookupTimer = setTimeout(function () {
      lookup(input.value);
    }, 500);
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      clearTimeout(lookupTimer);
      lookup(input.value);
    }
  });
})();
