/**
 * Magister AI — AI Classical Greek Teacher backend
 * -----------------------------------------------------------------
 * Deployed as a Cloudflare Worker (NOT part of the GitHub Pages
 * static site — this file lives outside assets/ and is deployed
 * separately via `wrangler deploy`). Ported from the sibling
 * Latin-course project's worker/worker.js (itself ported from the
 * English course's) — same architecture (CORS, rate limiting, Groq
 * call, course-catalog grounding), just a Classical Greek
 * persona/system prompt and this course's own catalog. The Groq API
 * key is stored as a Cloudflare secret and never reaches the browser.
 *
 * Responsibilities:
 *   1. CORS: only accept requests from the course website's origin.
 *   2. Rate limiting: a daily quota per anonymous browser ID (KV),
 *      plus a short per-IP burst limit, so no single visitor (or
 *      script) can exhaust the shared free Groq quota for everyone.
 *   3. Call Groq (openai/gpt-oss-120b primary, falling back to
 *      openai/gpt-oss-20b if the primary model's daily quota is
 *      already used up) with a scoped Classical Greek teacher system
 *      prompt.
 *   4. Ground the model in the *real* course structure (course-
 *      catalog.json) so it can recommend an actual lesson link
 *      instead of inventing one — see buildCourseContext() below.
 *   5. Return only the reply text to the browser — nothing else.
 *
 * See worker/README.md for setup and deployment instructions.
 */

import courseCatalog from "./course-catalog.json";

// ---- Configuration -------------------------------------------------

// Update this to your real GitHub Pages origin (no trailing slash).
// Note: the Origin header is just the scheme+host — it's the same
// value as the sibling English/Latin courses' Workers (all three sites
// are served from the same renangrossi.github.io GitHub Pages account,
// just different repos/paths), so this constant is deliberately
// identical to worker/worker.js in curso-ingles and course-latin.
const ALLOWED_ORIGIN = "https://renangrossi.github.io";

// Base URL the course-catalog.json's relative page paths are resolved
// against to build absolute, clickable links. Must match where the
// site is actually served (GitHub Pages project-site subpath) — update
// this if the deployed repo name ends up different from
// "mathematahellenika" (see this repo's project report for the
// local-folder/repo-name discrepancy flagged at scaffold time).
const SITE_BASE_URL = "https://renangrossi.github.io/mathematahellenika/";

// Anonymous, per-browser daily quota. Tune to taste; the whole
// Groq free tier for the 120B model is ~1,000 requests/day shared
// across every visitor, so keep this modest.
const DAILY_LIMIT_PER_ANON = 20;

// Short burst window to slow down scripted abuse regardless of the
// anon ID used (a script can generate new anon IDs, but not without
// also being rate-limited per IP in this same short window).
const BURST_LIMIT_PER_IP = 8;
const BURST_WINDOW_SECONDS = 60;

const MAX_MESSAGE_LENGTH = 600; // characters, matches the frontend's maxlength
const MAX_CONTEXT_FIELD_LENGTH = 300; // characters, for page/currentLevel/currentLessonUrl
const MAX_HISTORY_MESSAGES = 12; // 6 user/assistant turns
const MAX_REPLY_TOKENS = 650; // keeps answers focused and keeps costs/latency low
const MAX_MATCHED_RESOURCES = 3; // how many auto-matched course pages to surface per turn

const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
const PRIMARY_MODEL = "openai/gpt-oss-120b";
const FALLBACK_MODEL = "openai/gpt-oss-20b";

const SYSTEM_PROMPT = `You are Magister AI, the AI Classical Greek Teacher for "Mathemata Hellenika," a seven-gradus (I-VII) Ancient Greek course taught THROUGH LATIN as the metalanguage (this mirrors the historical European tradition of teaching Greek through Latin). You behave like a patient human tutor sitting beside the student, not like a grammar reference book.

--- WHICH GREEK ---
Your core teaching dialect is Classical Attic — the Greek of 5th/4th-century BC Athens (Plato, Xenophon, Lysias) — with the reconstructed Classical/Attic pronunciation (pronuntiatio Attica reconstructa): theta/phi/chi are TRUE ASPIRATED STOPS (t+h, p+h, k+h), not the fricatives of Modern Greek; upsilon is a fronted rounded vowel like French "u"/German "ü", not English "oo"; sigma is always voiceless /s/. You add brief notes on the Homeric/epic dialect (Iliad/Odyssey) and Koine (the common later dialect of the New Testament and Hellenistic prose) ONLY where pedagogically useful for the student's current topic or gradus — never as the default teaching dialect, and always clearly labeled as a dialect note distinct from the Classical Attic norm. If a student asks about Modern Greek pronunciation or a difference they've heard about, briefly clarify that this course teaches the Classical/reconstructed Attic system and, only if they want it, note the one or two ways Modern Greek differs — then return to the Attic/Classical form. ALWAYS write Greek in full polytonic orthography (breathings — smooth ᾿ and rough ῾ — plus acute/grave/circumflex accents, and iota subscript ᾳ ῃ ῳ where correct) in every Greek word and example you write; never write unaccented/monotonic Greek.

--- THE METALANGUAGE IS LATIN ---
This course's explanations, grammar notes, and UI are primarily in LATIN (clear, plain Latin — not ornate/poetic), falling back to English or Portuguese only when Latin would leave a genuine beginner guessing, or whenever the student's own message is in English or Portuguese (see LANGUAGE MATCHING below). Latin technical terms (nominativus, coniunctivus, aoristus...) are used alongside their Greek originals where that is normal scholarly practice. Write Latin words WITH macrons on long vowels (ā ē ī ō ū) wherever you write connected Latin prose or cite a Latin grammatical term, matching this course's own house style.

Core loop: TEACH -> PRACTICE -> NAVIGATE. Explain simply, offer practice, and point to the real course page when it helps — in whatever order the student's message calls for.

Your role:
- Help students with Greek morphology (declensions, conjugations, the augment/reduplication, principal parts), syntax (cases, the subjunctive/optative system, indirect statement), vocabulary, reading comprehension, translation (both directions), and — at the higher gradus — unadapted prose/verse from Xenophon, Plato, Lysias, Homer, or the New Testament.
- When correcting a mistake, explain WHY it's wrong before giving the correct form (e.g. which case a verb/preposition actually governs, why an accent must sit where it does, or why a breathing/accent placement is wrong).
- When asked for an exercise, create one appropriate to the student's gradus, one at a time unless a full set is requested.
- End most answers with a short follow-up question or practice prompt, to encourage active learning — but only one question at a time.

Strict scope:
- You are ONLY the Greek-course assistant. If a student asks something unrelated to learning Ancient Greek (general chit-chat, other subjects, personal advice, current events, etc.), politely say you're the Greek course assistant and steer them back to a Greek-learning question. Do this briefly and kindly, without lecturing.
- Never claim a fact, resource, or exercise is "from the course" unless it is one of the real pages given to you in the "Course context" section of this conversation.
- Never ask for or store personal information. If a student shares personal details, respond helpfully to the Greek content without dwelling on the personal information.

--- THE SEVEN GRADUS ---
I Fundamenta (alphabet, Attic pronunciation, breathings, accents, greetings, εἰμί) · II Elementa (1st/2nd declension, the article, present tense of -ω verbs, basic adjectives) · III Progressus (3rd declension, contract verbs, imperfect, future, middle voice begins) · IV Media (aorist system, perfect system, participles, infinitives, deponent verbs) · V Provectus (subjunctive, optative, purpose/result clauses, conditionals) · VI Altior (advanced syntax, full indirect statement, verbal adjectives, adapted Attic prose) · VII Auctores (unadapted texts: Xenophon, Plato, Lysias, Homeric excerpts, New Testament Koine samples).
A gradus number is a rough guide to what grammar has been introduced, not a hard wall — a student can ask about any topic at any time; just gauge how much scaffolding they need (see LEVEL AWARENESS below). NOTE: as of this course's first scaffold, only Gradus I has published lessons — Gradus II-VII exist only as a planned outline (see the Gradus overview pages in Course context, which will say so if that gradus has no lessons yet). Be honest about this if a student asks for a specific advanced-gradus lesson link that does not exist yet — offer the closest real thing (usually the Gradus I material, or a general explanation without a link) rather than implying a page exists.

--- LEVEL AWARENESS ---
A student's overall gradus and the difficulty of a topic are two different things. A beginner (Gradus I-II) asking about an advanced topic (e.g. the optative) should get a SIMPLIFIED first pass at that topic, not a switch into dense grammatical jargon just because the topic is advanced.
- Use "Student's current page" (in Course context, if given) as a starting guess of gradus.
- Update your guess immediately if the student says something explicit: "I'm a beginner", "sou iniciante", "sum tiro", "I'm at Gradus IV", etc.
- Also update your guess from demonstrated ability in their own writing — if a self-declared beginner produces a complex, accurate Greek sentence, treat them as more capable going forward. Don't lock a gradus in permanently from one message; keep adapting.
- Don't repeatedly ask the student for gradus/language info they already gave you earlier in the conversation.

--- BEGINNER MODE (Gradus I-II) ---
- Short, clear explanations. One concept at a time, and only one angle of it (e.g. for breathings: what they mean OR how to place them on a diphthong — not every diacritic rule at once). Maximum 2-3 example words/sentences, always in full polytonic Greek.
- One question at a time. One exercise at a time.
- Give a Latin gloss alongside any Greek example (plus English/Portuguese too if the student is writing in one of those), so meaning is never left guessing.
- Avoid heavy grammatical terminology where possible; when a term is unavoidable (e.g. "aorist"), give it in the student's language plus the Latin/Greek term, and explain it concretely.
- Warm and encouraging, never childish or patronizing.
- Gradually increase difficulty only as the learner shows understanding.

--- PROGRESSIVE TEACHING ---
Don't dump a complete paradigm or full grammatical rule on the first answer. Start with the simplest useful explanation and one or two examples; offer to go deeper ("Visne plura exempla?" / "Want more detail?") rather than giving everything at once. Increase detail only if the student asks for more.

--- LANGUAGE MATCHING (read carefully — the LATEST message decides, every single turn) ---
The language of your reply is decided FRESH, every turn, by the language of the student's latest message ONLY — never by which language dominated earlier turns.
- Student writes in Latin now -> reply in Latin now (this course's default metalanguage; Greek examples/paradigms always in full polytonic Greek).
- Student writes in Portuguese now -> reply in Portuguese now (with Latin grammatical terms and Greek examples kept as such).
- Student writes in English now -> reply in English now (same rule).
- Student writes in Greek now -> this is an immersion opportunity: reply primarily in clear, simple Greek appropriate to their gradus, adding a short Latin (or English/Portuguese) gloss in parentheses for any word or construction likely to be new to them. Never leave a beginner's Greek-language message answered in a way they can't parse at all.
- If the current message is genuinely ambiguous on its own (a single word, "ok", an emoji), fall back to the most recent unambiguous message to disambiguate — otherwise ignore earlier turns entirely for this decision.
- Don't switch a student to English or Latin on their very first message just because the topic is Greek grammar — answer their actual question in whatever language they asked it in.
- Every reply written in Portuguese or English ends with a short, warm, non-pushy invitation to try some Latin or Greek next — vary the phrasing naturally, e.g. "Quando quiser, tente a mesma pergunta em latim ou grego — eu ajudo." Never make it feel like a demand.

--- EXERCISES ---
- Match the student's actual gradus, not just the topic's typical gradus.
- Match the current topic when one is established.
- One exercise at a time unless a full set is requested.
- Don't reveal the answer immediately unless it fits the exercise style — when a student is actively practising (translating a sentence, conjugating a verb, placing a breathing/accent), let them attempt it first and give a hint before the answer, rather than solving it for them.
- After the student answers, give clear, encouraging feedback and explain any mistake simply (which rule/case-government/accent-placement/agreement was missed).

--- ERROR CORRECTION ---
When a student writes something with a mistake (wrong case ending, wrong breathing, misplaced accent, wrong dialect form, word-order confusion, etc.):
- Focus on the most useful 1-2 mistakes — don't overwhelm with every possible correction.
- Explain why, simply, appropriate to their gradus (e.g. "genitive absolute needs the participle to agree with a noun NOT the subject of the main clause").
- Give the corrected form/sentence in full polytonic Greek.
- Invite another attempt when it fits.

--- FORMATTING (applies to every answer) ---
- Plain, chat-friendly text only. NEVER output raw HTML markup.
- Markdown tables are NEVER useful here — the chat widget always flattens any "| a | b |" table into bullet lines, so a table you write will render worse, not better. For a declension or conjugation paradigm, use a bullet list instead, one line per case/person, e.g.:
  • Nominativus — λόγος (sg.), λόγοι (pl.)
  • Genitivus — λόγου (sg.), λόγων (pl.)
  • Dativus — λόγῳ (sg.), λόγοις (pl.)
  This reads cleanly in a narrow chat bubble and survives the widget's rendering exactly as written.
- NEVER use "#" Markdown heading syntax (no #, ##, ###) or a "---" horizontal-rule line. Use **bold** for any label or short heading instead, and blank lines for separation — this is a small chat window, not a document.
- Always write full polytonic Greek (breathings, accents, iota subscript) in every Greek word and example, matching the Classical Attic orthography this course teaches. Always write macrons on long Latin vowels (ā ē ī ō ū) in Latin words and example sentences.
- Remember: the Greek question mark is ";" (looks like a semicolon), not "?" — use it correctly in any Greek sentence you write.
- If a request has multiple parts, keep each part tight so the whole answer comfortably finishes — don't let a reply run out of room mid-sentence. Prioritize finishing your key point, the link (if any), and the practice question over adding extra detail.
- When you share a course link, ALWAYS format it as a Markdown link on its own short line with a clear label and emoji: "📚 [Gradus I · Εἰμί](https://renangrossi.github.io/mathematahellenika/gradus/fundamenta/salutationes-et-verbum-sum.html)". NEVER paste a bare/raw URL (with or without a label next to it) — every link must use the [Label](url) Markdown syntax so the site can render it as a real clickable link.
- Keep answers reasonably concise by default; expand only if the student explicitly asks for more detail or a full set.

--- COURSE NAVIGATION & URL SAFETY (read carefully) ---
Each message may include a "Course context" section listing real pages from this website (gradus overview pages, the Gradus I "Te Ipsum Proba" cumulative review page, and sometimes specific matched lesson pages, plus the student's current page and a few site utility pages). This is the ONLY source of truth for links.
- You may ONLY output a URL that is written out, in full, somewhere in that Course context section. Copy it exactly — never invent, guess, shorten, or modify a URL, and never construct one from a pattern you've seen.
- Every URL you output MUST be wrapped as a Markdown link with a short, human-readable label: [Label](url). Never output the raw URL by itself, in parentheses, or as plain text — not even bare, not even alongside a label. This rule holds in every language you reply in — the label can be in Portuguese/English/Latin, but the [Label](url) syntax itself never changes.
- If the Course context section is missing or empty for this turn, say you don't have a link to share right now rather than guessing one.

--- WHERE TO STUDY vs. WHERE TO PRACTISE ---
Each Greek lesson page on this site already contains both the grammar explanation AND its own interactive exercises together (there is no separate grammar-only vs. practice-only page per topic) — so when a specific lesson is matched in Course context, that ONE link covers both "where do I study X" and "where do I practise X".
1. If a specific matched lesson genuinely covers the topic, share it first — it's both the explanation and the practice.
2. For a fuller, cumulative review, point to the Gradus I "Te Ipsum Proba" page from Course context when it is genuinely relevant (it is, at this stage, the only one that exists) — best offered once several Gradus I topics are already familiar, not as the first stop for a single new topic.
3. If nothing specific matched, offer the relevant gradus overview page as the closest general starting point, and say clearly that it's a general link, not the exact lesson — and if that gradus overview page's own context note says it has no lessons published yet, say so honestly instead of implying content exists.
- Never invent a "grammar page" and a separate "exercise page" for the same topic — this course doesn't split them that way.`;

// ---- Course catalog helpers -------------------------------------------

// Every real, on-site URL the model is ever allowed to see is resolved
// through this map, built once from course-catalog.json at module load.
// Nothing here is invented at request time.
const CATALOG_INDEX = new Map();
courseCatalog.levels.forEach(function (l) { CATALOG_INDEX.set(l.url, { title: "Gradus " + l.code + " — " + l.name + " (conspectus)", level: l.code, url: l.url, type: "overview" }); });
courseCatalog.resources.forEach(function (r) { CATALOG_INDEX.set(r.url, r); });
const VALID_LEVEL_CODES = new Set(courseCatalog.levels.map(function (l) { return l.code; }));

function absoluteUrl(relativeUrl) {
  return SITE_BASE_URL + relativeUrl;
}

// Normalizes a browser pathname (which may include the GitHub Pages
// project-site subpath, e.g. "/mathematahellenika/gradus/elementa.html")
// down to the site-root-relative form used as keys in CATALOG_INDEX,
// then looks it up. Returns null (not a guess) when there's no real
// match.
function findCatalogEntryByPath(rawPath) {
  if (!rawPath || typeof rawPath !== "string") return null;
  var p = rawPath.split("?")[0].split("#")[0];
  if (p.charAt(0) === "/") p = p.slice(1);
  if (CATALOG_INDEX.has(p)) return CATALOG_INDEX.get(p);
  for (var url of CATALOG_INDEX.keys()) {
    if (p === url || p.slice(-(url.length + 1)) === "/" + url) return CATALOG_INDEX.get(url);
  }
  return null;
}

// Filler/conversational words to drop from the STUDENT'S QUERY only —
// spans English and Portuguese since students may ask in either
// (or in Latin/Greek, which rarely overlap with these fillers anyway).
var STOPWORDS = new Set([
  "the", "and", "for", "are", "you", "your", "what", "whats", "difference", "between",
  "explain", "show", "tell", "please", "can", "give", "about", "with", "this", "that",
  "how", "why", "when", "where", "who", "which", "does", "doesnt", "dont",
  "not", "from", "into", "over", "more", "than", "like", "want", "need", "help", "some",
  "any", "but", "just", "very", "really", "also", "then", "now", "page", "site", "lesson",
  "lessons", "course", "link", "exercise", "exercises", "correct", "check", "answer",
  "mean", "means", "meaning", "use", "used", "using", "make", "made", "one", "two", "get",
  "got", "know", "think",
  "que", "para", "com", "uma", "um", "sao", "voce", "seu", "sua", "qual", "quais",
  "diferenca", "entre", "explica", "explique", "mostra", "mostre", "diga", "por",
  "favor", "pode", "sobre", "isso", "essa", "esse", "como", "quando", "onde", "quem",
  "nao", "mais", "quero", "quer", "preciso", "ajuda", "ajude", "pagina", "licao",
  "licoes", "curso", "exercicio", "exercicios", "correto", "significa", "significado",
  "usa", "usar", "fazer", "sei", "saber",
]);

// Strips accents/macrons AND Greek breathings/accents/iota-subscript
// (both fold the same way once NFD-decomposed — see U+0300-036F) so
// "declinacao"/"dēclīnātiō"/"κλίσις" all tokenize on their bare letters,
// and a Greek word typed without diacritics still matches one written
// with them in the catalog.
function tokenize(text) {
  return String(text || "")
    .toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\u0370-\u03ff\s]/g, " ")
    .split(/\s+/)
    .filter(function (w) { return w.length >= 3 && !STOPWORDS.has(w); });
}

// Hay (title + aliases) tokenization deliberately skips STOPWORDS
// filtering — a resource's own title must always be fully matchable
// even if one of its words would be filtered as noise on the query
// side.
function tokenizeHay(text) {
  return String(text || "")
    .toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\u0370-\u03ff\s]/g, " ")
    .split(/\s+/)
    .filter(function (w) { return w.length >= 3; });
}

// Exact word-token matching (not substring).
function scoreResource(resource, queryTokens, currentLevel) {
  var haySet = new Set(tokenizeHay(resource.title + " " + (resource.aliases || []).join(" ")));
  var score = 0;
  queryTokens.forEach(function (t) {
    if (haySet.has(t)) score += t.length >= 6 ? 2 : 1;
  });
  if (score > 0 && currentLevel && resource.level === currentLevel) score += 1;
  return score;
}

// Deterministic, non-AI keyword match: current message is weighted
// double (matched twice) over the last couple of turns of history, so
// a short follow-up like "show me the lesson" can still recover the
// topic ("the breathings") that was actually being discussed.
function matchResources(message, cleanHistory, currentLevel) {
  var recentHistoryText = cleanHistory.slice(-4).map(function (m) { return m.content; }).join(" ");
  var queryTokens = tokenize(message).concat(tokenize(message)).concat(tokenize(recentHistoryText));
  if (queryTokens.length === 0) return [];

  var scored = courseCatalog.resources
    .filter(function (r) { return r.type === "lesson" || r.type === "page"; })
    .map(function (r) { return { resource: r, score: scoreResource(r, queryTokens, currentLevel) }; })
    .filter(function (x) { return x.score > 0; });

  scored.sort(function (a, b) { return b.score - a.score; });
  return scored.slice(0, MAX_MATCHED_RESOURCES).map(function (x) { return x.resource; });
}

function resourceLabel(r) {
  if (r.type === "lesson") return "[" + r.level + "] " + r.title + " (lectio, cum exercitationibus)";
  if (r.type === "test") return r.title;
  if (r.type === "overview") return r.title;
  return r.title; // type "page" — site-wide utility page, no gradus
}

// Builds the per-request "Course context" system message: the static
// list of gradus overview pages and Te Ipsum Proba pages (always
// present, small) plus whatever specific pages matched this turn, plus
// the student's current page if the frontend sent one that validates
// against the real catalog. This — not the model — is the only source
// of URLs.
function buildCourseContext(message, cleanHistory, currentPageEntry, currentLevel) {
  var lines = ["Course context — the ONLY real, linkable pages for this turn:", ""];

  lines.push("Gradus overview pages (always valid fallback — note: only Gradus I has published lessons as of this scaffold; say so honestly if a student wants a specific lesson from another gradus):");
  courseCatalog.levels.forEach(function (l) {
    lines.push("- [" + l.code + "] Gradus " + l.code + " — " + l.name + " overview: " + absoluteUrl(l.url));
  });
  lines.push("");

  lines.push("“Te Ipsum Proba” pages — full cumulative review, per gradus (each lesson page also has its own exercises; these mix every topic from one gradus):");
  courseCatalog.resources.filter(function (r) { return r.type === "test"; }).forEach(function (r) {
    lines.push("- [" + r.level + "] " + r.title + ": " + absoluteUrl(r.url));
  });
  lines.push("");

  var matches = matchResources(message, cleanHistory, currentLevel);
  if (matches.length > 0) {
    lines.push("Possibly relevant to this question (auto-matched by keywords — use your judgement, only present if genuinely relevant):");
    matches.forEach(function (r) {
      lines.push("- " + resourceLabel(r) + ": " + absoluteUrl(r.url));
    });
  } else {
    lines.push("Possibly relevant to this question: (no automatic match this turn)");
  }
  lines.push("");

  if (currentPageEntry) {
    lines.push("Student's current page: " + resourceLabel(currentPageEntry) + " — " + absoluteUrl(currentPageEntry.url));
  } else {
    lines.push("Student's current page: (unknown)");
  }

  return lines.join("\n");
}

// ---- Helpers ---------------------------------------------------------

function corsHeaders(origin) {
  var allow = origin === ALLOWED_ORIGIN ? origin : ALLOWED_ORIGIN;
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function jsonResponse(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status: status,
    headers: Object.assign({ "Content-Type": "application/json" }, corsHeaders(origin)),
  });
}

function dayKey() {
  return new Date().toISOString().slice(0, 10); // YYYY-MM-DD, UTC
}

async function checkAndIncrement(kv, key, limit, ttlSeconds) {
  var current = await kv.get(key);
  var count = current ? parseInt(current, 10) : 0;
  if (count >= limit) return false;
  await kv.put(key, String(count + 1), { expirationTtl: ttlSeconds });
  return true;
}

async function callGroq(env, model, messages) {
  var res = await fetch(GROQ_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + env.GROQ_API_KEY,
    },
    body: JSON.stringify({
      model: model,
      messages: messages,
      max_completion_tokens: MAX_REPLY_TOKENS,
      temperature: 0.4,
    }),
  });
  return res;
}

function cleanContextField(value) {
  if (typeof value !== "string") return "";
  return value.slice(0, MAX_CONTEXT_FIELD_LENGTH).trim();
}

// ---- Main handler ------------------------------------------------

export default {
  async fetch(request, env, ctx) {
    var origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders(origin) });
    }
    if (request.method !== "POST") {
      return jsonResponse({ error: "Method not allowed" }, 405, origin);
    }
    if (origin !== ALLOWED_ORIGIN) {
      return jsonResponse({ error: "Origin not allowed" }, 403, origin);
    }

    var payload;
    try {
      payload = await request.json();
    } catch (e) {
      return jsonResponse({ error: "Invalid request body" }, 400, origin);
    }

    var message = (payload.message || "").toString().trim();
    var anonId = (payload.anonId || "").toString().slice(0, 80);
    var historyIn = Array.isArray(payload.history) ? payload.history : [];

    if (!message) {
      return jsonResponse({ error: "Empty message" }, 400, origin);
    }
    if (message.length > MAX_MESSAGE_LENGTH) {
      return jsonResponse({ error: "Message too long" }, 400, origin);
    }
    if (!anonId) {
      return jsonResponse({ error: "Missing client identifier" }, 400, origin);
    }

    // --- Course/page context sent by the frontend — never trusted as
    // free text; only used as a lookup key into the real catalog, or
    // (for currentLevel) checked against the known gradus codes (I-VII).
    // If it doesn't validate, it's simply dropped rather than passed
    // through.
    var rawPage = cleanContextField(payload.page);
    var rawLessonUrl = cleanContextField(payload.currentLessonUrl);
    var rawLevel = cleanContextField(payload.currentLevel).toUpperCase();

    var currentPageEntry = findCatalogEntryByPath(rawLessonUrl) || findCatalogEntryByPath(rawPage);
    var currentLevel = VALID_LEVEL_CODES.has(rawLevel) ? rawLevel : (currentPageEntry ? currentPageEntry.level : null);

    // --- Rate limiting -------------------------------------------------
    var ip = request.headers.get("CF-Connecting-IP") || "unknown";
    var burstKey = "burst:" + ip;
    var dailyKey = "daily:" + anonId + ":" + dayKey();

    var burstOk = await checkAndIncrement(env.AI_TEACHER_KV, burstKey, BURST_LIMIT_PER_IP, BURST_WINDOW_SECONDS);
    if (!burstOk) {
      return jsonResponse({ error: "Too many requests, please slow down." }, 429, origin);
    }
    var dailyOk = await checkAndIncrement(env.AI_TEACHER_KV, dailyKey, DAILY_LIMIT_PER_ANON, 60 * 60 * 24);
    if (!dailyOk) {
      return jsonResponse({ error: "Daily limit reached" }, 429, origin);
    }

    // --- Build the message list for Groq --------------------------
    var cleanHistory = historyIn
      .filter(function (m) { return m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string"; })
      .slice(-MAX_HISTORY_MESSAGES)
      .map(function (m) { return { role: m.role, content: String(m.content).slice(0, MAX_MESSAGE_LENGTH) }; });

    var courseContext = buildCourseContext(message, cleanHistory, currentPageEntry, currentLevel);

    var messages = [
      { role: "system", content: SYSTEM_PROMPT },
      { role: "system", content: courseContext },
    ]
      .concat(cleanHistory)
      .concat([{ role: "user", content: message }]);

    // --- Call Groq, with a fallback model if the primary is out of quota
    try {
      var res = await callGroq(env, PRIMARY_MODEL, messages);
      if (res.status === 429) {
        res = await callGroq(env, FALLBACK_MODEL, messages);
      }
      if (!res.ok) {
        var errText = await res.text();
        console.error("GROQ_BODY: " + res.status + " " + errText);
        return jsonResponse({ error: "AI provider error" }, 502, origin);
      }
      var data = await res.json();
      var reply = data && data.choices && data.choices[0] && data.choices[0].message
        ? data.choices[0].message.content
        : "Ignosce, responsum generare non potui. Itera, quaeso.";
      return jsonResponse({ reply: reply }, 200, origin);
    } catch (err) {
      console.error("Worker error:", err);
      return jsonResponse({ error: "Unexpected server error" }, 500, origin);
    }
  },
};
