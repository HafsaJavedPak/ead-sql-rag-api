/* EAD Analytics console — a browser client of the authenticated FastAPI API.
   It talks only over HTTP to /api/v1; it never touches the agent directly. */

const API = window.EAD_API_BASE || "http://127.0.0.1:8000";
const V1 = API + "/api/v1";
const LS = "ead.auth";

const $ = (id) => document.getElementById(id);
const el = (tag, cls, txt) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (txt != null) n.textContent = txt;
  return n;
};

const STAGES = ["classify", "select_schema", "generate_sql", "validate_sql",
                "execute_sql", "visualize", "summarize"];

const EXAMPLES = [
  "How many projects are there in total?",
  "List the top 5 donors by number of projects funded.",
  "What is the total project cost in millions USD?",
  "Which executing agencies have the most active projects?",
  "Show the number of projects by project category.",
];

/* ============================== state ============================== */
const S = {
  access: null, refresh: null, expiresAt: 0,
  user: null,
  convs: [], currentId: null,
  streaming: false, activeRunId: null, abort: null,
  showArchived: false, searchQuery: "",
};

/* ============================ token store ========================== */
function saveAuth() {
  localStorage.setItem(LS, JSON.stringify({
    access: S.access, refresh: S.refresh, expiresAt: S.expiresAt, user: S.user,
  }));
}
function loadAuth() {
  try {
    const raw = JSON.parse(localStorage.getItem(LS) || "null");
    if (!raw || !raw.access) return false;
    Object.assign(S, raw);
    return true;
  } catch { return false; }
}
function clearAuth() {
  localStorage.removeItem(LS);
  S.access = S.refresh = S.user = null; S.expiresAt = 0;
}

function setTokens(pair) {
  S.access = pair.access_token;
  S.refresh = pair.refresh_token;
  S.expiresAt = Date.now() + (pair.expires_in || 900) * 1000;
  saveAuth();
}

/* Access tokens live 15 min; refresh tokens rotate on every use. */
async function ensureToken() {
  if (!S.refresh) return;
  if (Date.now() < S.expiresAt - 60_000) return;
  const res = await fetch(V1 + "/auth/jwt/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: S.refresh }),
  });
  if (!res.ok) { clearAuth(); showAuth(); throw new Error("Session expired. Please sign in again."); }
  setTokens(await res.json());
}

/* ============================== http =============================== */
async function api(path, { method = "GET", body, raw = false } = {}) {
  await ensureToken();
  const res = await fetch(V1 + path, {
    method,
    headers: {
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...(S.access ? { Authorization: "Bearer " + S.access } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) { clearAuth(); showAuth(); throw new Error("Session expired."); }
  if (raw) { if (!res.ok) throw new Error("HTTP " + res.status); return res; }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || data.title || `HTTP ${res.status}`);
  return data;
}

/* ============================== toast ============================== */
let toastTimer;
function toast(msg) {
  const t = $("toast");
  t.textContent = msg; t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.hidden = true; }, 3200);
}

/* =============================== auth UI =========================== */
let authMode = "login";

function showAuth() {
  $("auth").hidden = false;
  $("app").hidden = true;
}
function showApp() {
  $("auth").hidden = true;
  $("app").hidden = false;
}

function renderAuthMode() {
  const signup = authMode === "signup";
  $("authTitle").textContent = signup ? "Create your account" : "Welcome back";
  $("authSub").textContent = signup
    ? "You'll get your own private conversation history."
    : "Sign in to query the Economic Affairs Division dataset.";
  $("nameField").hidden = !signup;
  $("pwHint").hidden = !signup;
  $("authPassword").minLength = signup ? 12 : 1;
  $("authPassword").autocomplete = signup ? "new-password" : "current-password";
  $("switchText").textContent = signup ? "Already have an account?" : "Don't have an account?";
  $("switchBtn").textContent = signup ? "Sign in" : "Sign up";
  $("authError").hidden = true;
}

$("switchBtn").onclick = () => { authMode = authMode === "login" ? "signup" : "login"; renderAuthMode(); };

$("authForm").onsubmit = async (e) => {
  e.preventDefault();
  const btn = $("authSubmit");
  const err = $("authError");
  err.hidden = true;
  btn.disabled = true; btn.textContent = "Please wait…";
  try {
    const email = $("authEmail").value.trim();
    const password = $("authPassword").value;
    if (authMode === "signup") {
      const name = $("authName").value.trim();
      const res = await fetch(V1 + "/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, display_name: name || null }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(detailOf(data, res));
      setTokens(data.tokens);
      S.user = data.user; saveAuth();
    } else {
      const res = await fetch(V1 + "/auth/jwt/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(detailOf(data, res));
      setTokens(data);
      S.user = await api("/users/me"); saveAuth();
    }
    await boot();
  } catch (ex) {
    err.textContent = ex.message; err.hidden = false;
  } finally {
    btn.disabled = false; btn.textContent = "Continue";
  }
};

function detailOf(data, res) {
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  if (data.title) return data.title;
  return `Request failed (HTTP ${res.status})`;
}

$("logoutBtn").onclick = async () => {
  try { await api("/auth/jwt/logout", { method: "POST" }); } catch {}
  clearAuth();
  S.convs = []; S.currentId = null;
  renderAuthMode();
  showAuth();
};

/* ============================ composer ============================= */
const composer = $("composerTpl").content.firstElementChild.cloneNode(true);
const input = composer.querySelector("#input");
const sendBtn = composer.querySelector("#sendBtn");
const stopBtn = composer.querySelector("#stopBtn");
const plusBtn = composer.querySelector("#plusBtn");

function mountComposer(where) {
  where.appendChild(composer);
  input.focus();
}
function autosize() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 200) + "px";
}
input.addEventListener("input", () => {
  autosize();
  sendBtn.disabled = !input.value.trim() || S.streaming;
});
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
});
sendBtn.onclick = () => send();
stopBtn.onclick = async () => {
  if (S.abort) S.abort.abort();
  if (S.activeRunId) {
    try { await api(`/runs/${S.activeRunId}/cancel`, { method: "POST" }); toast("Run cancelled."); }
    catch (e) { toast(e.message); }
  }
};

plusBtn.onclick = (e) => {
  e.stopPropagation();
  const m = $("plusMenu");
  m.innerHTML = "";
  EXAMPLES.forEach((q) => {
    const b = el("button", null, q);
    b.onclick = () => { m.hidden = true; input.value = q; autosize(); sendBtn.disabled = false; input.focus(); };
    m.appendChild(b);
  });
  const r = plusBtn.getBoundingClientRect();
  m.hidden = false;
  m.style.left = r.left + "px";
  m.style.top = (r.top - m.offsetHeight - 8) + "px";
  m.style.minWidth = "320px";
};

/* ============================ suggestions ========================== */
function renderSuggestions() {
  const host = $("suggestions");
  host.innerHTML = "";
  const icons = [
    'M4 20V10m5 10V4m5 16v-7m5 7V8',
    'M3 6h18M3 12h18M3 18h12',
    'M12 4v16m8-8H4',
  ];
  EXAMPLES.slice(0, 3).forEach((q, i) => {
    const b = el("button", "suggestion" + (i === 0 ? " first" : ""));
    b.innerHTML = `<svg viewBox="0 0 24 24" width="19" height="19"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="${icons[i]}"/></svg>`;
    b.appendChild(el("span", null, q));
    b.onclick = () => { input.value = q; autosize(); sendBtn.disabled = false; send(); };
    host.appendChild(b);
  });
}

/* =========================== conversations ========================= */
async function loadConversations() {
  const path = S.searchQuery
    ? `/conversations/search?q=${encodeURIComponent(S.searchQuery)}&limit=100`
    : `/conversations?limit=100`;
  const page = await api(path);
  S.convs = page.items || [];
  renderConversations();
}

function renderConversations() {
  const list = $("convList");
  list.innerHTML = "";
  const want = S.showArchived ? "archived" : "active";
  const items = S.convs.filter((c) => c.status === want);
  $("recentsLabel").textContent = S.searchQuery
    ? `Results for "${S.searchQuery}"`
    : (S.showArchived ? "Archived" : "Recents");
  $("convEmpty").hidden = items.length > 0;
  $("convEmpty").textContent = S.searchQuery
    ? "No conversations match that search."
    : (S.showArchived ? "Nothing archived." : "No conversations yet.");

  items.forEach((c) => {
    const li = el("li", "conv-item" + (c.id === S.currentId ? " active" : ""));
    const open = el("button", "open", c.title);
    open.title = c.title;
    open.onclick = () => openConversation(c.id);
    li.appendChild(open);

    const kebab = el("button", "kebab");
    kebab.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16"><circle fill="currentColor" cx="5" cy="12" r="1.7"/><circle fill="currentColor" cx="12" cy="12" r="1.7"/><circle fill="currentColor" cx="19" cy="12" r="1.7"/></svg>`;
    kebab.onclick = (e) => { e.stopPropagation(); openConvMenu(e, c); };
    li.appendChild(kebab);
    list.appendChild(li);
  });
}

function openConvMenu(e, c) {
  const m = $("titleMenu");
  m.hidden = false;
  m.style.left = Math.min(e.clientX, innerWidth - 220) + "px";
  m.style.top = e.clientY + "px";
  m.dataset.conv = c.id;
  m.querySelector('[data-act="archive"]').textContent =
    c.status === "archived" ? "Unarchive chat" : "Archive chat";
}

$("titleMenu").onclick = async (e) => {
  const act = e.target.closest("button")?.dataset.act;
  if (!act) return;
  const menu = $("titleMenu");
  const id = menu.dataset.conv || S.currentId;
  menu.hidden = true;
  if (!id) return;
  const conv = S.convs.find((c) => c.id === id);
  try {
    if (act === "rename") {
      const title = prompt("Rename conversation", conv?.title || "");
      if (!title || !title.trim()) return;
      await api(`/conversations/${id}`, { method: "PATCH", body: { title: title.trim() } });
    } else if (act === "archive") {
      const next = conv?.status === "archived" ? "active" : "archived";
      await api(`/conversations/${id}`, { method: "PATCH", body: { status: next } });
      if (id === S.currentId) newChat();
    } else if (act === "delete") {
      if (!confirm("Delete this conversation? This cannot be undone.")) return;
      await api(`/conversations/${id}`, { method: "DELETE" });
      if (id === S.currentId) newChat();
    }
    await loadConversations();
    if (id === S.currentId) $("chatTitle").textContent =
      S.convs.find((c) => c.id === id)?.title || "EAD Analytics";
  } catch (ex) { toast(ex.message); }
};

document.addEventListener("click", () => {
  $("titleMenu").hidden = true;
  $("plusMenu").hidden = true;
});

$("titleBtn").onclick = (e) => {
  if (!S.currentId) return;
  e.stopPropagation();
  const r = $("titleBtn").getBoundingClientRect();
  const m = $("titleMenu");
  m.dataset.conv = S.currentId;
  m.hidden = false;
  m.style.left = r.left + "px";
  m.style.top = (r.bottom + 6) + "px";
  const conv = S.convs.find((c) => c.id === S.currentId);
  m.querySelector('[data-act="archive"]').textContent =
    conv?.status === "archived" ? "Unarchive chat" : "Archive chat";
};

/* ============================== views ============================== */
function newChat() {
  S.currentId = null;
  $("hero").hidden = false;
  $("thread").hidden = true;
  $("threadInner").innerHTML = "";
  $("chatTitle").textContent = "EAD Analytics";
  mountComposer($("composerHost"));
  renderConversations();
  input.value = ""; autosize(); sendBtn.disabled = true;
}

function enterThread() {
  $("hero").hidden = true;
  $("thread").hidden = false;
  mountComposer($("composerDock"));
}

async function openConversation(id) {
  S.currentId = id;
  enterThread();
  const conv = S.convs.find((c) => c.id === id);
  $("chatTitle").textContent = conv?.title || "Conversation";
  renderConversations();
  const inner = $("threadInner");
  inner.innerHTML = "";
  const spin = el("div", "spin"); spin.style.margin = "40px auto"; inner.appendChild(spin);
  try {
    const page = await api(`/conversations/${id}/messages?limit=100`);
    inner.innerHTML = "";
    (page.items || []).forEach((m) => {
      if (m.role === "user") inner.appendChild(userTurn(m.content));
      else inner.appendChild(assistantTurn(m));
    });
    scrollDown();
  } catch (ex) {
    inner.innerHTML = "";
    inner.appendChild(errorBox(ex.message));
  }
}

function scrollDown() {
  const t = $("threadInner");
  t.scrollTop = t.scrollHeight;
}

/* ============================= rendering =========================== */
function userTurn(text) {
  const wrap = el("div", "turn user");
  wrap.appendChild(el("div", "bubble-user", text));
  return wrap;
}

function errorBox(msg) {
  return el("div", "err", msg);
}

function panel(title, open = true) {
  const p = el("div", "panel" + (open ? "" : " closed"));
  const head = el("div", "panel-head");
  head.appendChild(el("span", null, title));
  const chev = el("span", "chev");
  chev.innerHTML = `<svg viewBox="0 0 24 24" width="15" height="15"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m7 10 5 5 5-5"/></svg>`;
  head.appendChild(chev);
  head.onclick = () => p.classList.toggle("closed");
  const body = el("div", "panel-body");
  p.appendChild(head); p.appendChild(body);
  p._body = body;
  return p;
}

/* ------------------------- answer formatting ------------------------ */

const escapeHtml = (s) => String(s).replace(/[&<>"]/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* Model output is untrusted text, so escape first and only then allow a
   small, fixed set of inline marks. No raw HTML ever reaches the DOM. */
function inlineMd(s) {
  return escapeHtml(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>")
    .replace(/(^|\s)(—|-)\s/g, "$1— ");
}

/* Minimal block-level markdown: paragraphs, bullet and numbered lists. */
function renderMarkdown(src) {
  const lines = String(src || "").split(/\r?\n/);
  let html = "";
  let list = null;
  let para = [];

  const flushPara = () => {
    if (para.length) { html += `<p>${inlineMd(para.join(" "))}</p>`; para = []; }
  };
  const flushList = () => { if (list) { html += `</${list}>`; list = null; } };

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) { flushPara(); flushList(); continue; }

    const bullet = line.match(/^[-*•]\s+(.*)$/);
    const numbered = line.match(/^\d+[.)]\s+(.*)$/);

    if (bullet || numbered) {
      flushPara();
      const want = bullet ? "ul" : "ol";
      if (list !== want) { flushList(); html += `<${want}>`; list = want; }
      html += `<li>${inlineMd((bullet || numbered)[1])}</li>`;
      continue;
    }
    flushList();
    para.push(line);
  }
  flushPara(); flushList();
  return html || `<p>${inlineMd(src || "")}</p>`;
}

/* "total_project_cost_usd_mn" -> "Total project cost USD MN"

   Deliberately only prettifies the alias — it never translates a suffix into
   a spelled-out unit. Aliases are model-generated and can disagree with the
   values (the dummy `*_usd` columns hold raw USD despite the domain notes
   calling them millions), so asserting a unit here can state something false.
   Echoing the alias keeps the label honest; the figure stays the raw value. */
const UNIT_TOKENS = new Set(["usd", "pkr", "eur", "gbp", "mn", "bn", "id", "pct", "no", "fy"]);

function humanizeColumn(name) {
  const words = String(name).replace(/[_-]+/g, " ").trim().split(/\s+/);
  const label = words
    .map((w, i) => {
      if (UNIT_TOKENS.has(w.toLowerCase())) return w.toUpperCase();
      return i === 0 ? w.charAt(0).toUpperCase() + w.slice(1) : w;
    })
    .join(" ");
  return { label, unit: "" };
}

const looksNumeric = (v) =>
  v !== null && v !== "" && typeof v !== "boolean" &&
  isFinite(Number(String(v).replace(/,/g, "")));

function formatNumber(v) {
  const n = Number(String(v).replace(/,/g, ""));
  if (!isFinite(n)) return String(v);
  const decimals = Number.isInteger(n) ? 0 : Math.min(2, (String(n).split(".")[1] || "").length);
  return n.toLocaleString(undefined, {
    minimumFractionDigits: decimals, maximumFractionDigits: decimals,
  });
}

const formatCell = (v) =>
  v === null ? "—" : looksNumeric(v) ? formatNumber(v) : String(v);

/* Collapsed-by-default disclosure holding the technical detail. */
function disclosure(label) {
  const d = el("div", "disclosure closed");
  const btn = el("button", "disclosure-toggle");
  btn.innerHTML = `<svg class="chev" viewBox="0 0 24 24" width="14" height="14"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m7 10 5 5 5-5"/></svg>`;
  btn.appendChild(el("span", null, label));
  const body = el("div", "disclosure-body");
  btn.onclick = () => {
    d.classList.toggle("closed");
    btn.querySelector("span").textContent =
      d.classList.contains("closed") ? label : label.replace("Show", "Hide");
  };
  d.appendChild(btn); d.appendChild(body);
  d._body = body;
  return d;
}

/* Renders a completed assistant message. The answer leads; the query and
   schema that produced it live behind a collapsed disclosure. */
function assistantTurn(msg) {
  const wrap = el("div", "turn assistant");
  const run = msg.run;

  if (msg.status === "failed" || run?.status === "failed") {
    const a = el("div", "answer");
    a.innerHTML = renderMarkdown(msg.content || "The request could not be completed.");
    wrap.appendChild(a);
    if (run?.error_detail) wrap.appendChild(errorBox(run.error_detail));
    return wrap;
  }

  const answer = el("div", "answer");
  answer.innerHTML = renderMarkdown(msg.content || "");
  wrap.appendChild(answer);
  if (!run) return wrap;

  const cols = run.columns || [];
  const rows = run.rows || [];

  // A single figure is the headline — show it, don't bury it in a 1×1 table.
  const singleValue = cols.length === 1 && rows.length === 1;
  if (singleValue) {
    const { label, unit } = humanizeColumn(cols[0]);
    const card = el("div", "figure");
    card.appendChild(el("div", "figure-value", formatCell(rows[0][0])));
    card.appendChild(el("div", "figure-label", unit ? `${label} (${unit})` : label));
    wrap.appendChild(card);
  }

  // Charts read faster than tables, so they come first.
  (run.artifacts || []).forEach((a) => {
    const box = el("div", "chart-box");
    const img = el("img", "chart-img");
    img.alt = "Chart of the result";
    loadArtifact(a, img);
    box.appendChild(img);
    wrap.appendChild(box);
  });

  if (cols.length && rows.length && !singleValue) {
    const numeric = cols.map((_, i) => rows.every((r) => r[i] === null || looksNumeric(r[i])));
    const box = el("div", "result");

    const head = el("div", "result-head");
    head.appendChild(el("span", null,
      `${run.row_count.toLocaleString()} result${run.row_count === 1 ? "" : "s"}` +
      (run.truncated ? " · showing the first page" : "")));
    const csv = el("button", "link-btn", "Download CSV");
    csv.onclick = () => downloadCsv(cols, rows, msg.id);
    head.appendChild(csv);
    box.appendChild(head);

    const scroll = el("div", "tbl-scroll");
    const table = el("table", "rows");
    const trh = el("tr");
    cols.forEach((c, i) => {
      const { label, unit } = humanizeColumn(c);
      const th = el("th", numeric[i] ? "num" : null);
      th.appendChild(el("span", null, label));
      if (unit) th.appendChild(el("small", null, unit));
      trh.appendChild(th);
    });
    const thead = el("thead"); thead.appendChild(trh); table.appendChild(thead);

    const tb = el("tbody");
    rows.forEach((r) => {
      const tr = el("tr");
      r.forEach((v, i) => tr.appendChild(el("td", numeric[i] ? "num" : null, formatCell(v))));
      tb.appendChild(tr);
    });
    table.appendChild(tb); scroll.appendChild(table); box.appendChild(scroll);
    wrap.appendChild(box);
  }

  // Everything technical, hidden until asked for.
  if (run.validated_sql || run.selected_tables?.length) {
    const d = disclosure("Show how this was calculated");
    if (run.selected_tables?.length) {
      d._body.appendChild(el("div", "detail-label", "Data sources"));
      const chips = el("div", "tables-chips");
      run.selected_tables.forEach((t) => chips.appendChild(el("span", "chip", t)));
      d._body.appendChild(chips);
    }
    if (run.validated_sql) {
      d._body.appendChild(el("div", "detail-label", "Query"));
      d._body.appendChild(el("pre", "sql", run.validated_sql));
    }
    const meta = el("div", "meta-row");
    if (run.completed_at && run.started_at) {
      const ms = new Date(run.completed_at) - new Date(run.started_at);
      meta.appendChild(el("span", null, `${(ms / 1000).toFixed(1)}s`));
    }
    if (run.retry_count) meta.appendChild(el("span", null, `${run.retry_count} retry attempt(s)`));
    meta.appendChild(el("span", null, `run ${String(run.id).slice(0, 8)}`));
    d._body.appendChild(meta);
    wrap.appendChild(d);
  }
  return wrap;
}

function downloadCsv(cols, rows, name) {
  const cell = (v) => {
    const s = v === null ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const csv = [cols.map(cell).join(","), ...rows.map((r) => r.map(cell).join(","))].join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url; a.download = `ead-result-${String(name).slice(0, 8)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

/* Artifact bytes are owner-scoped and need the bearer token, so they
   cannot be used as a plain <img src>. Fetch, then use an object URL. */
async function loadArtifact(a, img) {
  try {
    const url = a.url.startsWith("http") ? a.url : API + a.url;
    await ensureToken();
    const res = await fetch(url, { headers: { Authorization: "Bearer " + S.access } });
    if (!res.ok) throw new Error("HTTP " + res.status);
    img.src = URL.createObjectURL(await res.blob());
  } catch {
    img.replaceWith(errorBox("Chart could not be loaded."));
  }
}

/* ============================= streaming =========================== */
async function send() {
  const text = input.value.trim();
  if (!text || S.streaming) return;

  input.value = ""; autosize(); sendBtn.disabled = true;

  try {
    if (!S.currentId) {
      const title = text.length > 60 ? text.slice(0, 57) + "…" : text;
      const conv = await api("/conversations", { method: "POST", body: { title } });
      S.currentId = conv.id;
      S.convs.unshift(conv);
      $("chatTitle").textContent = conv.title;
      enterThread();
      renderConversations();
    }
  } catch (ex) { toast(ex.message); sendBtn.disabled = false; return; }

  const inner = $("threadInner");
  inner.appendChild(userTurn(text));

  const turn = el("div", "turn assistant");
  const stages = el("div", "stages");
  STAGES.forEach((s) => {
    const chip = el("span", "stage", s);
    chip.dataset.stage = s;
    stages.appendChild(chip);
  });
  const answer = el("div", "answer streaming");
  const cursor = el("span", "cursor");
  answer.appendChild(cursor);
  turn.appendChild(stages); turn.appendChild(answer);
  inner.appendChild(turn);
  scrollDown();

  S.streaming = true;
  stopBtn.hidden = false; sendBtn.hidden = true;
  S.abort = new AbortController();
  let buffered = "";

  try {
    await ensureToken();
    const res = await fetch(`${V1}/conversations/${S.currentId}/messages/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
        Authorization: "Bearer " + S.access,
        "Idempotency-Key": crypto.randomUUID(),
      },
      body: JSON.stringify({ content: text }),
      signal: S.abort.signal,
    });

    if (!res.ok) {
      const e = await res.json().catch(() => ({}));
      throw new Error(e.detail || `HTTP ${res.status}`);
    }

    for await (const ev of sseEvents(res)) {
      if (ev.event === "message.accepted") {
        S.activeRunId = ev.data.run_id;
      } else if (ev.event === "agent.stage") {
        const idx = STAGES.indexOf(ev.data.stage);
        stages.querySelectorAll(".stage").forEach((c, i) => {
          c.classList.toggle("done", i < idx);
          c.classList.toggle("active", i === idx);
        });
        scrollDown();
      } else if (ev.event === "assistant.delta") {
        buffered += ev.data.text || "";
        cursor.remove();
        answer.textContent = buffered;
        answer.appendChild(cursor);
        scrollDown();
      } else if (ev.event === "message.completed") {
        turn.replaceWith(assistantTurn(ev.data));
        scrollDown();
      } else if (ev.event === "run.failed") {
        cursor.remove();
        stages.remove();
        turn.appendChild(errorBox(`${ev.data.code}: ${ev.data.detail}`));
      } else if (ev.event === "run.cancelled") {
        cursor.remove();
        stages.remove();
        if (!buffered) answer.textContent = "Run cancelled.";
      }
    }
  } catch (ex) {
    cursor.remove();
    if (ex.name === "AbortError") {
      if (!buffered) answer.textContent = "Stopped.";
    } else {
      turn.appendChild(errorBox(ex.message));
    }
  } finally {
    cursor.remove();
    S.streaming = false; S.activeRunId = null; S.abort = null;
    stopBtn.hidden = true; sendBtn.hidden = false;
    sendBtn.disabled = !input.value.trim();
    input.focus();
    loadConversations().catch(() => {});
  }
}

/* Parses the text/event-stream framing: blank-line delimited blocks of
   id: / event: / data: fields. Comment lines (": ping") are ignored.
   Per the SSE spec a line may end in CRLF, LF, or CR — sse-starlette
   emits CRLF, so matching only "\n\n" silently never fires. */
const SSE_BOUNDARY = /\r\n\r\n|\n\n|\r\r/;
const SSE_NEWLINE = /\r\n|\n|\r/;

async function* sseEvents(res) {
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let m;
    while ((m = SSE_BOUNDARY.exec(buf)) !== null) {
      const block = buf.slice(0, m.index);
      buf = buf.slice(m.index + m[0].length);
      let event = "message";
      const dataLines = [];
      for (const line of block.split(SSE_NEWLINE)) {
        if (!line || line.startsWith(":")) continue;
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
      }
      if (!dataLines.length) continue;
      let data;
      try { data = JSON.parse(dataLines.join("\n")); } catch { data = {}; }
      yield { event, data };
    }
  }
}

/* ============================== chrome ============================= */
$("newChatBtn").onclick = () => {
  S.showArchived = false; S.searchQuery = ""; $("searchInput").value = "";
  setActiveNav("newChatBtn");
  newChat();
};

$("archiveBtn").onclick = async () => {
  S.showArchived = true; S.searchQuery = ""; $("searchInput").value = "";
  setActiveNav("archiveBtn");
  await loadConversations();
};

$("chartsBtn").onclick = async () => {
  setActiveNav("chartsBtn");
  if (!S.currentId) { toast("Open a conversation to see its charts."); return; }
  const page = await api(`/conversations/${S.currentId}/messages?limit=100`);
  const arts = (page.items || []).flatMap((m) => m.run?.artifacts || []);
  if (!arts.length) { toast("No charts in this conversation yet."); return; }
  const inner = $("threadInner");
  const box = panel(`charts in this conversation — ${arts.length}`, true);
  arts.forEach((a) => {
    const img = el("img", "chart-img");
    img.style.marginBottom = "10px";
    loadArtifact(a, img);
    box._body.appendChild(img);
  });
  inner.appendChild(box);
  scrollDown();
};

function setActiveNav(id) {
  ["newChatBtn", "chartsBtn", "archiveBtn"].forEach((n) =>
    $(n).classList.toggle("active", n === id));
}

$("collapseBtn").onclick = () => $("app").classList.add("collapsed");
$("expandBtn").onclick = () => $("app").classList.remove("collapsed");
$("brandBtn").onclick = () => $("newChatBtn").click();

$("searchBtn").onclick = () => {
  const box = $("sideSearch");
  box.hidden = !box.hidden;
  if (!box.hidden) $("searchInput").focus();
  else { S.searchQuery = ""; $("searchInput").value = ""; loadConversations(); }
};

let searchTimer;
$("searchInput").oninput = (e) => {
  clearTimeout(searchTimer);
  const q = e.target.value.trim();
  searchTimer = setTimeout(async () => {
    S.searchQuery = q;
    S.showArchived = false;
    try { await loadConversations(); } catch (ex) { toast(ex.message); }
  }, 220);
};

$("userPill").onclick = async () => {
  const name = prompt("Display name", S.user?.display_name || "");
  if (name === null) return;
  try {
    S.user = await api("/users/me", { method: "PATCH", body: { display_name: name.trim() || null } });
    saveAuth(); renderUser();
  } catch (ex) { toast(ex.message); }
};

function renderUser() {
  const label = S.user?.display_name || S.user?.email || "Account";
  $("userName").textContent = label;
  $("userPlan").textContent = S.user?.role === "admin" ? "Admin" : "Signed in";
  $("avatar").textContent = (label[0] || "?");
}

async function health() {
  const dot = $("healthDot");
  try {
    const r = await fetch(API + "/health/ready");
    const d = await r.json();
    const ok = r.ok && d.status === "ok";
    dot.className = "health-dot " + (ok ? "ok" : "bad");
    dot.title = ok ? "API ready" : "API degraded";
  } catch {
    dot.className = "health-dot bad";
    dot.title = "API unreachable";
  }
}

/* =============================== boot ============================== */
async function boot() {
  showApp();
  renderUser();
  renderSuggestions();
  newChat();
  health();
  setInterval(health, 30_000);
  $("modelChip").textContent = window.EAD_MODEL_LABEL || "gpt-4o-mini";
  try {
    if (!S.user) { S.user = await api("/users/me"); saveAuth(); renderUser(); }
    await loadConversations();
  } catch (ex) {
    if (!/Session expired/.test(ex.message)) toast(ex.message);
  }
}

(async function start() {
  renderAuthMode();
  if (loadAuth()) {
    try { await ensureToken(); await boot(); return; } catch {}
  }
  showAuth();
})();
