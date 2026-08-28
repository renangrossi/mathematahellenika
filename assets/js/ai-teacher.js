/*!
 * Magister AI — AI Classical Greek Teacher chat widget
 * -----------------------------------------------------------------
 * Ported from the sibling Latin-course project's assets/js/ai-teacher.js,
 * itself ported from the English course's (see that file's own header
 * comment for the full rationale — this is the same architecture, just
 * re-branded for Mathemata Hellenika).
 *
 * No login, no account, no data stored beyond the current browser
 * session. Sends the student's message (plus a short in-memory
 * conversation history, cleared when the tab/window closes) to a
 * Cloudflare Worker, which holds the real API key server-side and
 * forwards the request to Groq. This file never sees or stores an
 * API key.
 * -----------------------------------------------------------------
 */
(function () {
  "use strict";

  var scriptTag = document.querySelector("script[data-ai-endpoint]");
  var toggle = document.querySelector("[data-ai-teacher-toggle]");
  if (!scriptTag || !toggle) return;

  /* ---------------------------------------------------------------
   * Owl-tetradrachm intro — draws attention to the Magister AI button
   * once per browser tab session (sessionStorage key
   * "aiTeacherIntroShown"; sessionStorage rather than localStorage on
   * purpose, so it plays again next visit/tab but not on every page
   * within the same visit). Skips entirely under
   * prefers-reduced-motion, or once the session key is set — in both
   * cases the button just renders normally with no extra markup, no
   * delay, and no behavior change. See ".ai-teacher-intro" /
   * ".ai-teacher-toggle--pending" / "@keyframes ai-coin-spin" in
   * ai-teacher.css.
   *
   * The coin itself: a gold disc styled after the Athenian silver
   * tetradrachm (5th century BC) — Athena's owl, front-facing with
   * round eyes and ear-tufts, flanked by a small olive sprig and
   * crescent moon exactly as the real coin's reverse, with the
   * abbreviated "ΑΘΕ" (short for ΑΘΕΝΑΙΩΝ, "of the Athenians") legend
   * beneath — the Greek-course counterpart to the Latin course's
   * waving SPQR vexillum, itself in place of the English course's
   * Betsy Ross flag. Colors are the raw palette tokens (--gold-*,
   * --attic-red, --olive-700), not the semantic --color-* aliases, so —
   * like the banner it replaces — the coin looks the same regardless of
   * light/dark mode (see tokens.css / dark-mode.css).
   * --------------------------------------------------------------- */
  var INTRO_SESSION_KEY = "aiTeacherIntroShown";
  var INTRO_WAVE_MS = 2200; // must match the CSS animation-duration above
  var INTRO_BURST_DELAY_MS = 1250; // when the sparkle burst starts, partway through the spin
  var OWL_COIN_SVG =
    '<svg class="ai-teacher-intro__coin" viewBox="0 0 60 60" role="img" aria-label="Tetradrachmon Atticum cum noctua Athenae sacra">' +
    // Coin disc + inner rim
    '<circle cx="30" cy="30" r="27" fill="var(--gold-500)" stroke="var(--gold-600)" stroke-width="2"/>' +
    '<circle cx="30" cy="30" r="22.5" fill="none" stroke="var(--gold-600)" stroke-width="0.6" opacity="0.6"/>' +
    // Owl: body, wings, head, eyes, beak, ear-tufts, feet
    '<ellipse cx="30" cy="33" rx="9.5" ry="12" fill="var(--attic-red)"/>' +
    '<path d="M21 28 Q17 34 21.5 41" stroke="var(--attic-red)" stroke-width="2.6" fill="none" stroke-linecap="round"/>' +
    '<path d="M39 28 Q43 34 38.5 41" stroke="var(--attic-red)" stroke-width="2.6" fill="none" stroke-linecap="round"/>' +
    '<circle cx="30" cy="24" r="8" fill="var(--attic-red)"/>' +
    '<circle cx="26.5" cy="23" r="2.6" fill="var(--gold-300)"/>' +
    '<circle cx="33.5" cy="23" r="2.6" fill="var(--gold-300)"/>' +
    '<circle cx="26.5" cy="23" r="1" fill="var(--attic-red)"/>' +
    '<circle cx="33.5" cy="23" r="1" fill="var(--attic-red)"/>' +
    '<path d="M28.6 26.5 L30 29 L31.4 26.5 Z" fill="var(--gold-300)"/>' +
    '<path d="M24.5 18 L26 22" stroke="var(--attic-red)" stroke-width="1.6" stroke-linecap="round"/>' +
    '<path d="M35.5 18 L34 22" stroke="var(--attic-red)" stroke-width="1.6" stroke-linecap="round"/>' +
    '<path d="M26 44 L25 47 M30 45 L30 48 M34 44 L35 47" stroke="var(--attic-red)" stroke-width="1.6" fill="none" stroke-linecap="round"/>' +
    // Olive sprig (upper-left) and crescent moon (upper-right), as on the real coin's reverse
    '<path d="M13 15 Q17 12 20 16" stroke="var(--olive-700)" stroke-width="1.4" fill="none" stroke-linecap="round"/>' +
    '<ellipse cx="14.5" cy="14.5" rx="2" ry="1.1" fill="var(--olive-700)" transform="rotate(-35 14.5 14.5)"/>' +
    '<ellipse cx="18.5" cy="14.5" rx="2" ry="1.1" fill="var(--olive-700)" transform="rotate(20 18.5 14.5)"/>' +
    '<path d="M45 14 a4 4 0 1 0 0.2 6.4 a3.1 3.1 0 1 1 -0.2 -6.4 Z" fill="var(--ink-900)" opacity="0.55"/>' +
    // ΑΘΕ legend
    '<text x="30" y="53" text-anchor="middle" font-family="Cardo, Cormorant Garamond, Georgia, serif" font-size="8" font-weight="700" letter-spacing="1" fill="var(--attic-red)">ΑΘΕ</text>' +
    "</svg>";

  // A small golden sparkle burst, timed to land partway through the
  // coin's spin rather than at t=0. Reuses the exact .xp-burst /
  // .xp-burst__spark classes and @keyframes the gamification toasts
  // use (see components.css and progress.js's buildBurst()) for a
  // consistent look — just with a later --delay/--glow-delay so it
  // reads as "during the wave" instead of "the moment the coin
  // appears." Only ever called from playCoinIntro(), which already
  // skips the whole standard (and this burst with it) under
  // prefers-reduced-motion.
  function buildSparkleBurst() {
    var burst = document.createElement("div");
    burst.className = "xp-burst xp-burst--badge";
    burst.style.setProperty("--glow-delay", INTRO_BURST_DELAY_MS + "ms");
    var count = 12;
    for (var i = 0; i < count; i++) {
      var spark = document.createElement("span");
      spark.className = "xp-burst__spark";
      spark.style.setProperty("--angle", Math.round((360 / count) * i + (Math.random() * 20 - 10)) + "deg");
      spark.style.setProperty("--delay", (INTRO_BURST_DELAY_MS + Math.round(Math.random() * 150)) + "ms");
      burst.appendChild(spark);
    }
    return burst;
  }

  // A handful of extra sparkle bursts at random points scattered around
  // the coin/button corner — not just the one centered on the
  // standard (buildSparkleBurst() above). Each "spot" is its own tiny
  // anchor positioned at a random spot inside .ai-teacher-fireworks
  // (which itself just hugs the same corner as the coin/button, see
  // ai-teacher.css), reusing .xp-burst/.xp-burst__spark so every burst
  // — centered or scattered — looks identical, just relocated and
  // independently timed. Delays are spread across (and a little past)
  // the coin's spin so the fireworks read as happening *during* the
  // moment, not all at once. Only ever called from playCoinIntro(),
  // which already skips this entirely under prefers-reduced-motion.
  function buildScatteredFireworks() {
    var host = document.createElement("div");
    host.className = "ai-teacher-fireworks";
    host.setAttribute("aria-hidden", "true");
    var SPOTS = 4;
    for (var i = 0; i < SPOTS; i++) {
      var spot = document.createElement("div");
      spot.className = "ai-teacher-fireworks__spot";
      // Random point well inside the zone (10-90%) so a burst's sparks
      // don't get clipped right at the edge.
      spot.style.left = Math.round(10 + Math.random() * 80) + "%";
      spot.style.top = Math.round(10 + Math.random() * 80) + "%";

      var delay = INTRO_BURST_DELAY_MS + Math.round(Math.random() * 700);
      var burst = document.createElement("div");
      burst.className = "xp-burst xp-burst--badge";
      burst.style.setProperty("--glow-delay", delay + "ms");
      // Fewer sparks per scattered burst than the single on-standard one
      // (buildSparkleBurst() uses 12) — several small pops read better
      // than several big ones at this scale.
      var sparkCount = 5 + Math.floor(Math.random() * 3);
      for (var j = 0; j < sparkCount; j++) {
        var spark = document.createElement("span");
        spark.className = "xp-burst__spark";
        spark.style.setProperty("--angle", Math.round((360 / sparkCount) * j + (Math.random() * 30 - 15)) + "deg");
        spark.style.setProperty("--delay", (delay + Math.round(Math.random() * 120)) + "ms");
        burst.appendChild(spark);
      }
      spot.appendChild(burst);
      host.appendChild(spot);
    }
    return host;
  }

  function playCoinIntro() {
    var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var alreadyShown = true;
    try {
      alreadyShown = sessionStorage.getItem(INTRO_SESSION_KEY) === "1";
    } catch (e) {
      alreadyShown = true; // storage unavailable — skip the animation rather than risk repeating it forever
    }
    if (reducedMotion || alreadyShown) return; // toggle already renders normally, nothing else to do

    toggle.classList.add("ai-teacher-toggle--pending");
    var intro = document.createElement("div");
    intro.className = "ai-teacher-intro";
    intro.setAttribute("aria-hidden", "true"); // purely decorative; the real button carries the accessible label
    intro.innerHTML = OWL_COIN_SVG;
    intro.appendChild(buildSparkleBurst());
    // .ai-teacher-fireworks is itself position:fixed (see ai-teacher.css),
    // so nesting it inside `intro` is just for lifecycle convenience —
    // one `intro.remove()` in finish() below clears both together —
    // it isn't laid out relative to the coin's own small inline box.
    intro.appendChild(buildScatteredFireworks());
    document.body.appendChild(intro);

    var done = false;
    function finish() {
      if (done) return;
      done = true;
      clearTimeout(fallbackTimer);
      intro.remove();
      toggle.classList.remove("ai-teacher-toggle--pending");
      try {
        sessionStorage.setItem(INTRO_SESSION_KEY, "1");
      } catch (e) { /* ignore — worst case the intro plays again next page */ }
    }
    // animationend is the normal path; the timeout is a safety net in
    // case the animation never fires/completes for any reason, so the
    // button is never stuck invisible.
    var fallbackTimer = setTimeout(finish, INTRO_WAVE_MS + 200);
    intro.querySelector(".ai-teacher-intro__coin").addEventListener("animationend", finish);
  }
  playCoinIntro();

  var ENDPOINT = scriptTag.getAttribute("data-ai-endpoint");
  var panel = document.querySelector("[data-ai-teacher-panel]");
  var closeBtn = document.querySelector("[data-ai-teacher-close]");
  var messagesBox = document.querySelector("[data-ai-teacher-messages]");
  var form = document.querySelector("[data-ai-teacher-form]");
  var input = document.querySelector("[data-ai-teacher-input]");
  var sendBtn = document.querySelector("[data-ai-teacher-send]");
  var hint = document.querySelector("[data-ai-teacher-hint]");

  // Conversation history lives only in memory for this page view —
  // never written to localStorage/sessionStorage, and lost on reload
  // or tab close. Capped so a long chat can't blow up the request size.
  var history = [];
  var MAX_HISTORY_TURNS = 6;

  // Anonymous rate-limiting identity: a random ID with no personal
  // information, stored locally only so the same browser can be
  // recognized for a fair per-day quota. Not sent anywhere except as
  // an opaque token to our own Worker.
  function getAnonId() {
    try {
      var id = localStorage.getItem("aiTeacherAnonId");
      if (!id) {
        id = "anon-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
        localStorage.setItem("aiTeacherAnonId", id);
      }
      return id;
    } catch (e) {
      return "anon-session-" + Date.now();
    }
  }

  // Cheap, page-derived context so the Worker can ground answers in the
  // real course structure — no page markup changes needed beyond what
  // site_chrome.py already renders on every page. The gradus (level)
  // comes straight from <body data-level-code="…">, which every
  // generated page already carries (I-VII; empty on top-level pages
  // like index.html) — see scripts/site_chrome.py's header(). The
  // "lesson" name is just the first segment of <title> (e.g. "Alphabetum
  // et Soni — Gradus I — Mathemata Hellenika" -> "Alphabetum et Soni").
  // The Worker re-validates all of this against its own course catalog
  // before ever using it — nothing here is trusted as-is.
  var courseContext = (function () {
    var levelCode = (document.body.getAttribute("data-level-code") || "").trim();
    var titleParts = (document.title || "").split("—"); // split on em dash "—"
    return {
      currentLevel: levelCode,
      currentLesson: titleParts[0] ? titleParts[0].trim() : "",
      currentLessonUrl: window.location.pathname,
    };
  })();

  // On small phones, locks the *page* behind the fixed-position panel
  // while it's open, so a scroll/rubber-band gesture that starts on
  // the panel's message list can't drag the underlying page (and,
  // with it, the visual viewport's scale/position) along with it —
  // one more contributor to a "loses proportions after opening" bug
  // alongside the 16px input fix in ai-teacher.css. Scoped to small
  // viewports only (matchMedia below) so desktop, where the panel sits
  // beside the page rather than over it, is unaffected — see
  // window.__mhPanelLock in dict-widget.js, which shares this same
  // counter so the Lexicon widget and Magister AI never fight over who
  // "owns" the lock if a student somehow opens both.
  var lockedBodyScroll = false;
  function lockBodyScrollForPanel() {
    if (!(window.matchMedia && window.matchMedia("(max-width: 640px)").matches)) return;
    window.__mhPanelLock = (window.__mhPanelLock || 0) + 1;
    lockedBodyScroll = true;
    if (window.__mhPanelLock > 1) return; // another panel already holds the lock
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
    if (window.__mhPanelLock > 0) return; // still held by another panel
    var y = window.__mhPanelLockY || 0;
    var s = document.body.style;
    s.position = "";
    s.top = "";
    s.left = "";
    s.right = "";
    s.width = "";
    window.scrollTo(0, y);
  }

  function toggleOpen(open) {
    var willOpen = open !== undefined ? open : panel.hidden;
    panel.hidden = !willOpen;
    toggle.setAttribute("aria-expanded", String(willOpen));
    if (willOpen) {
      lockBodyScrollForPanel();
      input.focus();
      messagesBox.scrollTop = messagesBox.scrollHeight;
    } else {
      unlockBodyScrollForPanel();
    }
  }

  toggle.addEventListener("click", function () { toggleOpen(); });
  closeBtn.addEventListener("click", function () { toggleOpen(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) toggleOpen(false);
  });
  document.addEventListener("click", function (e) {
    if (panel.hidden) return;
    if (panel.contains(e.target) || toggle.contains(e.target)) return;
    toggleOpen(false);
  });
  panel.addEventListener("click", function (e) { e.stopPropagation(); });

  // Keep the panel clear of the on-screen keyboard on mobile.
  // 100vh/100dvh (see ai-teacher.css) already keep the panel inside
  // the *layout* viewport, but iOS Safari doesn't shrink either unit
  // when a software keyboard opens — only `window.visualViewport`
  // reflects that. Without this, the panel (positioned via `bottom`
  // against the unchanged layout viewport) stays put while the
  // keyboard slides up over it, burying the input/send row exactly
  // as described in the "keyboard shouldn't push the panel off-screen"
  // requirement. When supported, we measure how much of the layout
  // viewport the keyboard is covering and feed that back in as
  // `--ai-kb-offset`, which ai-teacher.css's `bottom`/`max-height`
  // both already read from — so the whole panel (not just the input)
  // rises above the keyboard, keeping messages, input and send all
  // reachable. No-op (offset stays 0) on desktop and on browsers
  // without VisualViewport support, where the existing CSS is enough.
  if (window.visualViewport) {
    var vv = window.visualViewport;
    var syncKeyboardOffset = function () {
      if (panel.hidden) return;
      var covered = window.innerHeight - vv.height - vv.offsetTop;
      panel.style.setProperty("--ai-kb-offset", Math.max(0, Math.round(covered)) + "px");
    };
    vv.addEventListener("resize", syncKeyboardOffset);
    vv.addEventListener("scroll", syncKeyboardOffset);
    input.addEventListener("focus", function () {
      // The keyboard animates in, so the viewport doesn't reach its
      // final size until a beat after focus fires.
      setTimeout(syncKeyboardOffset, 50);
      setTimeout(syncKeyboardOffset, 350);
    });
    input.addEventListener("blur", function () {
      setTimeout(syncKeyboardOffset, 50);
    });
  }

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = String(s || "");
    return d.innerHTML;
  }

  // Very small, safe subset of markdown-ish formatting the model
  // tends to use (bold, line breaks, simple numbered/bulleted lists)
  // rendered without any HTML injection risk, since we escape first.
  //
  // Markdown tables get special handling: the system prompt discourages
  // them, but if the model produces one anyway (well-formed, malformed,
  // or truncated), a raw "| a | b |" row is unreadable in a narrow chat
  // bubble. Rather than trying to render an actual <table> (which isn't
  // valid inside the <p> these messages live in), every pipe-delimited
  // row is converted into a short bullet line instead — this guarantees
  // the student never sees broken/raw Markdown syntax.
  function isTableSeparatorRow(line) {
    return /^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$/.test(line.trim());
  }

  function splitTableRow(line) {
    var t = line.trim().replace(/^\|/, "").replace(/\|$/, "");
    return t.split("|").map(function (c) { return c.trim(); }).filter(function (c) { return c.length > 0; });
  }

  function inlineBold(s) {
    return s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  }

  // Base the site's own relative paths (as sent to the model in the
  // Worker's "Course context") resolve against — used only by the bare
  // relative-path safety net below.
  var SITE_BASE_URL = "https://renangrossi.github.io/mathematahellenika/";

  // Turns Markdown links [Label](url) into real, clickable <a> elements.
  // Two safety nets, for on the rare chance the model doesn't follow
  // the system prompt's "always use [Label](url)" instruction:
  //   1. A bare absolute http(s) URL still becomes a clickable link
  //      (using the raw URL itself as the label, since there's no
  //      label to reuse).
  //   2. A bare *relative* site path (e.g. "gradus/fundamenta/sum-verbum-essendi.html"
  //      or "gradus/fundamenta.html#te-ipsum-proba", missing the
  //      "https://…" origin entirely) is resolved against SITE_BASE_URL
  //      and linked too — this is the case that otherwise shows up as
  //      inert, unclickable plain text in the chat.
  // A single regex/replace pass avoids double-wrapping a URL that was
  // already turned into an <a> by an earlier branch in the same pass.
  var RELATIVE_PATH_PATTERN = "gradus\\/[A-Za-z0-9\\-\\/.]+\\.html(?:#[A-Za-z0-9\\-]+)?" +
    "|(?:exercitationes|examina|varia|lexicon|probatio|iter|hodie|verba-irregularia|index)\\.html(?:#[A-Za-z0-9\\-]+)?";
  var LINK_PATTERN = new RegExp(
    "\\[([^\\[\\]]+)\\]\\((https?:\\/\\/[^\\s()]+)\\)" + // 1 label, 2 mdUrl
    "|(https?:\\/\\/[^\\s<>\"']+)" + // 3 bareUrl
    "|\\b(" + RELATIVE_PATH_PATTERN + ")\\b", // 4 relPath
    "g"
  );
  function inlineLinks(s) {
    return s.replace(LINK_PATTERN, function (match, label, mdUrl, bareUrl, relPath) {
      if (label && mdUrl) {
        return '<a href="' + mdUrl + '" target="_blank" rel="noopener noreferrer">' + label + "</a>";
      }
      if (relPath) {
        return '<a href="' + SITE_BASE_URL + relPath + '" target="_blank" rel="noopener noreferrer">' + relPath + "</a>";
      }
      // Trim trailing punctuation (., , ; : ! ? ) ]) that's almost
      // always sentence punctuation, not part of the URL itself.
      var trimmed = bareUrl.replace(/[.,;:!?)\]]+$/, "");
      var trailing = bareUrl.slice(trimmed.length);
      return '<a href="' + trimmed + '" target="_blank" rel="noopener noreferrer">' + trimmed + "</a>" + trailing;
    });
  }

  // The system prompt asks the model to avoid "#" heading syntax, but
  // as a safety net (same reasoning as the table handling above): if
  // it slips one in anyway, never show the raw "### Heading" text —
  // render it as a bold line instead, since <p> can't hold real
  // heading elements and a literal "###" reads as broken Markdown.
  function formatLine(line) {
    var heading = line.match(/^#{1,6}\s+(.*)$/);
    if (heading) return "<strong>" + inlineLinks(inlineBold(heading[1])) + "</strong>";
    return inlineLinks(inlineBold(line));
  }

  function renderBotText(raw) {
    var safe = escapeHtml(raw);
    var lines = safe.split("\n");
    var out = [];
    var i = 0;
    while (i < lines.length) {
      var line = lines[i];
      if (/^-{3,}$/.test(line.trim())) {
        // Bare "---" horizontal-rule Markdown — drop it rather than
        // showing literal dashes; surrounding blank lines already
        // give enough visual separation in a chat bubble.
        i++;
        continue;
      }
      if (line.indexOf("|") !== -1 && line.trim() !== "") {
        var block = [];
        var j = i;
        while (j < lines.length && lines[j].indexOf("|") !== -1 && lines[j].trim() !== "") {
          block.push(lines[j]);
          j++;
        }
        block.forEach(function (rowLine, idx) {
          if (idx === 1 && isTableSeparatorRow(rowLine)) return; // drop the "---|---" row
          var cells = splitTableRow(rowLine);
          if (cells.length === 0) return;
          var label = inlineLinks(cells[0].replace(/\*\*/g, ""));
          var rest = cells.slice(1).map(function (c) { return inlineLinks(inlineBold(c)); });
          out.push("• <strong>" + label + "</strong>" + (rest.length ? " — " + rest.join(" — ") : ""));
        });
        i = j;
        continue;
      }
      out.push(formatLine(line));
      i++;
    }
    var html = out.join("\n");
    html = html.replace(/\n\s*[-*]\s+/g, "\n• ");
    html = html.replace(/\n/g, "<br>");
    return html;
  }

  function addMessage(role, text) {
    var msg = document.createElement("div");
    msg.className = "ai-teacher-msg ai-teacher-msg--" + (role === "user" ? "user" : "bot");
    var p = document.createElement("p");
    if (role === "user") {
      p.textContent = text;
    } else {
      p.innerHTML = renderBotText(text);
    }
    msg.appendChild(p);
    messagesBox.appendChild(msg);
    messagesBox.scrollTop = messagesBox.scrollHeight;
    return msg;
  }

  function addTypingIndicator() {
    var msg = document.createElement("div");
    msg.className = "ai-teacher-msg ai-teacher-msg--bot ai-teacher-msg--typing";
    msg.innerHTML = "<p><span></span><span></span><span></span></p>";
    messagesBox.appendChild(msg);
    messagesBox.scrollTop = messagesBox.scrollHeight;
    return msg;
  }

  function setBusy(busy) {
    input.disabled = busy;
    sendBtn.disabled = busy;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text) return;

    addMessage("user", text);
    history.push({ role: "user", content: text });
    if (history.length > MAX_HISTORY_TURNS * 2) {
      history = history.slice(-MAX_HISTORY_TURNS * 2);
    }
    input.value = "";
    input.style.height = "auto";
    setBusy(true);
    var typing = addTypingIndicator();

    fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        history: history.slice(0, -1),
        anonId: getAnonId(),
        page: window.location.pathname,
        currentLevel: courseContext.currentLevel,
        currentLesson: courseContext.currentLesson,
        currentLessonUrl: courseContext.currentLessonUrl,
      }),
    })
      .then(function (res) {
        if (res.status === 429) {
          throw new Error("RATE_LIMIT");
        }
        if (!res.ok) throw new Error("SERVER_ERROR");
        return res.json();
      })
      .then(function (data) {
        typing.remove();
        var reply = data && data.reply ? data.reply : "Ignosce, nullum responsum accepi. Itera, quaeso.";
        addMessage("bot", reply);
        history.push({ role: "assistant", content: reply });
      })
      .catch(function (err) {
        typing.remove();
        if (err && err.message === "RATE_LIMIT") {
          addMessage("bot", "Hodie iam ad numerum quaestionum maximum pervenisti apud Magistrum AI. Cras redi, quaeso — interim exercitationibus ipsius cursus uti potes!");
        } else {
          addMessage("bot", "Ignosce, Magistrum AI nunc adire non potui. Quaeso conexionem tuam proba et post paulum itera.");
        }
      })
      .finally(function () {
        setBusy(false);
        input.focus();
      });
  });

  // Auto-grow the textarea up to a reasonable max height.
  input.addEventListener("input", function () {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });
})();
