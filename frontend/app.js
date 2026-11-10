/* Tether — single-page app. Every action maps to a real API call; the server enforces the gates. */
"use strict";
const $ = (s, el=document) => el.querySelector(s);
const $$ = (s, el=document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const store = {
  get role() { return localStorage.getItem("tether.role") || "reviewer"; },
  set role(v) { localStorage.setItem("tether.role", v); },
  get project() { return localStorage.getItem("tether.project") || null; },
  set project(v) { v ? localStorage.setItem("tether.project", v) : localStorage.removeItem("tether.project"); },
};

/* ------------------------------------------------------------------ theme (two modes; default dark) */
const theme = {
  KEY: "tether.theme",
  get() { const t = localStorage.getItem("tether.theme"); return t === "colour" ? "colour" : "dark"; },
  set(t) { localStorage.setItem("tether.theme", t); document.documentElement.setAttribute("data-theme", t); renderThemeToggle(); },
  toggle() { theme.set(theme.get() === "dark" ? "colour" : "dark"); },
};
function renderThemeToggle() {
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;
  const dark = theme.get() === "dark";
  document.documentElement.setAttribute("data-theme", theme.get());
  btn.setAttribute("aria-pressed", String(dark));
  const name = document.getElementById("theme-name");
  if (name) name.textContent = dark ? "Dark" : "Colour";
  const sub = btn.querySelector("small");
  if (sub) sub.textContent = dark ? "switch to Colour" : "switch to Dark";
}

const ROLES = [
  {id:"leaver",    name:"Aarav Mehta",  job:"Leaver — centre-of-knowledge", initials:"AM"},
  {id:"reviewer",  name:"Sanit Salve",  job:"Reviewer — decides & signs",   initials:"SS"},
  {id:"successor", name:"Diya Raman",   job:"Successor — day one",          initials:"DR"},
  {id:"admin",     name:"Krushna Patil",job:"Admin — sources & retention",  initials:"KP"},
];

/* ------------------------------------------------------------------ api */
async function api(path, {method="GET", body=null, raw=false} = {}) {
  const res = await fetch(path, {
    method,
    headers: {"X-Tether-Role": store.role,
      ...(body && !(body instanceof FormData) ? {"Content-Type": "application/json"} : {})},
    body: body == null ? null : (body instanceof FormData ? body : JSON.stringify(body)),
  });
  if (raw) {
    if (!res.ok) throw await toError(res);
    return res;
  }
  let data = null;
  try { data = await res.json(); } catch (_) { /* empty body */ }
  if (!res.ok) throw { status: res.status, error: (data && data.error) || res.statusText, data };
  return data;
}
async function toError(res){ let d=null; try{ d=await res.json(); }catch(_){} return { status: res.status, error: (d && d.error) || res.statusText, data: d }; }

function toast(msg, kind="ok") {
  const rack = $("#toasts");
  const el = document.createElement("div");
  el.className = `toast ${kind}`;
  el.textContent = msg;
  rack.appendChild(el);
  setTimeout(() => el.remove(), 5200);
}
const errText = e => typeof e?.error === "string" ? e.error : (e?.error?.note || e?.error?.errors?.join?.(", ") || JSON.stringify(e?.error || "unknown error"));

/* ------------------------------------------------------------------ router */
const ROUTES = [
  {re: /^\/$/, view: "home"},
  {re: /^\/p\/([^/]+)\/connect$/, view: "connect"},
  {re: /^\/p\/([^/]+)\/rebuild$/, view: "rebuild"},
  {re: /^\/p\/([^/]+)\/review$/, view: "review"},
  {re: /^\/p\/([^/]+)\/signoff$/, view: "signoff"},
  {re: /^\/p\/([^/]+)\/handover$/, view: "handover"},
  {re: /^\/p\/([^/]+)\/admin$/, view: "admin"},
  {re: /^\/judge$/, view: "judge"},
];
function parseRoute() {
  const path = window.location.pathname;
  for (const r of ROUTES) {
    const m = path.match(r.re);
    if (m) return { name: r.view, projectId: m[1] || null };
  }
  return { name: "notfound", projectId: null };
}
function nav(path) { history.pushState({}, "", path); render(); window.scrollTo(0, 0); }
document.addEventListener("click", e => {
  const a = e.target.closest("[data-nav]");
  if (a) { e.preventDefault(); nav(a.getAttribute("data-nav")); }
});
window.addEventListener("popstate", render);

/* ------------------------------------------------------------------ top bar */
const STATE_ORDER = ["scoped","labelled","rebuilt","in review","signed","shared","received"];
const CHECK = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.5 8.5l3 3 6-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const LOCK = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><rect x="3" y="7" width="10" height="6.5" rx="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" stroke="currentColor" stroke-width="1.5"/></svg>';
const STEPS6 = [
  {n:1, name:"Scope Sources",     cap:"Ingest",   path:id=>`/p/${id}/connect`, unlocked:p=>!!p, done:st=>st>=1, view:"connect"},
  {n:2, name:"Label Sources",     cap:"Gate 1",   path:id=>`/p/${id}/connect`, unlocked:p=>!!p, done:st=>st>=2, view:"connect"},
  {n:3, name:"Reconstruct",       cap:"Verify",   path:id=>`/p/${id}/rebuild`, unlocked:p=>p&&p.state!=="scoped", done:st=>st>=3, view:"rebuild"},
  {n:4, name:"Review Queue",      cap:"Gate 2",   path:id=>`/p/${id}/review`,  unlocked:p=>p&&["rebuilt","in review","signed","shared","received"].includes(p.state), done:st=>st>=4, view:"review"},
  {n:5, name:"Sign Version",      cap:"Gate 3",   path:id=>`/p/${id}/signoff`, unlocked:p=>p&&["rebuilt","in review","signed","shared","received"].includes(p.state), done:st=>st>=4, view:"signoff"},
  {n:6, name:"Successor Handover",cap:"Seal",     path:id=>`/p/${id}/handover`,unlocked:p=>p&&["signed","shared","received"].includes(p.state), done:st=>st>=6, view:"handover"},
];
const stateIdx = p => p ? STATE_ORDER.indexOf(p.state) : -1;
function currentViewName() { return parseRoute().name; }
function renderChrome(project) {
  // role select in the top bar
  const sel = $("#role-select");
  if (sel) {
    if (!sel.options.length) {
      sel.innerHTML = ROLES.map(r => `<option value="${r.id}">${esc(r.name)} · ${esc(r.job.split(" — ")[0])}</option>`).join("");
    }
    sel.value = store.role;
    sel.onchange = () => { store.role = sel.value; render(); };
  }
  // top navigation links
  const route = currentViewName();
  $$("#topnav a[data-view]").forEach(a => {
    const view = a.dataset.view;
    const enabled = !!project;
    a.setAttribute("data-nav", enabled ? `/p/${project.id}/${view}` : "#");
    a.href = enabled ? a.getAttribute("data-nav") : "#";
    a.classList.toggle("disabled", !enabled);
    a.classList.toggle("current", route === view);
    if (!enabled) a.setAttribute("aria-disabled", "true"); else a.removeAttribute("aria-disabled");
  });
  // horizontal gate stepper
  const bar = $("#stepper");
  if (!bar) return;
  const st = stateIdx(project);
  let currentAssigned = false;
  bar.innerHTML = STEPS6.map(s => {
    const done = st >= 0 && s.done(st);
    const unlocked = s.unlocked(project);
    let state = done ? "done" : "";
    if (!done && !currentAssigned) { state = "current"; currentAssigned = true; }
    else if (!done && currentAssigned) state = unlocked ? "" : "locked";
    const interactive = unlocked && !done ? true : unlocked;
    const inner = `<span class="step-num">${done ? CHECK : (interactive ? s.n : LOCK)}</span><span><b>${esc(s.name)}</b><small>${esc(s.cap)}</small></span>`;
    return `<li>${interactive
      ? `<a class="step ${state}" href="${s.path(project.id)}" data-nav="${s.path(project.id)}">${inner}</a>`
      : `<span class="step ${state} locked" aria-disabled="true">${inner}</span>`}</li>`;
  }).join("");
}

/* ------------------------------------------------------------------ boot */
let currentProject = null;
const themeBtn = document.getElementById("theme-toggle");
if (themeBtn) themeBtn.addEventListener("click", () => theme.toggle());
async function boot() {
  const pid = store.project;
  if (!pid) { await render(); return; }
  try { currentProject = await api(`/api/projects/${pid}`); }
  catch (e) { if (e.status === 404) store.project = null; currentProject = null; }
  render();
}
async function render() {
  const route = parseRoute();
  const app = $("#app");
  app.innerHTML = "";
  let project = null;
  if (route.projectId) {
    try { project = currentProject = await api(`/api/projects/${route.projectId}`); store.project = project.id; }
    catch (e) {
      renderChrome(null);
      app.innerHTML = errorView(e.status === 404 ? "Project not found" : "Could not load project", errText(e));
      return;
    }
  }
  renderChrome(project);
  try {
    switch (route.name) {
      case "home": return renderHome(app);
      case "connect": return await renderConnect(app, project);
      case "rebuild": return await renderRebuild(app, project);
      case "review": return await renderReview(app, project);
      case "signoff": return await renderSignoff(app, project);
      case "handover": return await renderHandover(app, project);
      case "admin": return await renderAdmin(app, project);
      case "judge": return renderJudge(app);
      default: app.innerHTML = errorView("Page not found", "That route does not exist in Tether.");
    }
  } catch (e) {
    app.innerHTML = errorView("Something went wrong", errText(e));
  }
}
function errorView(title, detail) {
  return `<div class="card empty"><span class="empty-mark">◌</span><h2 class="card-title">${esc(title)}</h2><p>${esc(detail)}</p><div class="btn-row" style="justify-content:center"><a class="btn btn-secondary" data-nav="/" href="/">Back to start</a></div></div>`;
}
renderThemeToggle();
boot();

/* ------------------------------------------------------------------ home */
function renderHome(app) {
  app.innerHTML = `
  <div class="hero">
    <div class="hero-kicker">PROJECT TETHER · KNOWLEDGE HANDOVER ENGINE</div>
    <h1>Prevent critical engineering knowledge from leaving with people.</h1>
    <p class="lede">Tether captures what a departing engineer knows and decided while the work was happening. When they move on, the next person picks it up — settled decisions, unfinished work, true owners, and active risk — without chasing anyone.</p>
    <div class="pick-grid">
      <div class="pick">
        <div class="pick-head"><span class="badge-index">01</span></div>
        <h2>Load Demo Project: Aster</h2>
        <p>The synthetic student portal project (“Aster — campus club events app”) with 61 planted facts, 20 planted fakes, 6 planted contradictions and 6 successor gaps. Runs hermetically with zero API keys — claims are pulled in replay mode, every check is real.</p>
        <ul class="pick-list">
          <li>Sources: Git repo (~60 commits), 7 meeting notes, issues &amp; PRs, chat export</li>
          <li>Departing lead: Alex Rivera (2 weeks’ notice) — most commits authored by one person</li>
          <li>Reviewer: Sanit Salve (N1, Team Lead) · Successor: Diya Raman · Admin: Krushna Patil</li>
        </ul>
        <button class="btn btn-primary" id="cta-demo">Load Demo Project &amp; Start Flow →</button>
      </div>
      <div class="pick">
        <div class="pick-head"><span class="badge-index">02</span></div>
        <h2>Use Your Own Authorised Sources</h2>
        <p>Upload a Git bundle export, Markdown notes and a JSON chat export. A mandatory, explicit authorisation consent is logged before anything is parsed — the two connected-person channels are never read.</p>
        <ul class="pick-list">
          <li>Mandatory consent gate, logged in the tamper-evident audit trail</li>
          <li>In-memory exclusion for private / HR channels before storage</li>
          <li>Automatic secret &amp; PII redaction prior to write</li>
        </ul>
        <button class="btn btn-ghost" id="cta-own">Connect Custom Sources →</button>
      </div>
    </div>
    <div class="walk">
      <div class="walk-head">
        <h2>›_ The Four-Minute Verification Walkthrough (DM-1 to DM-4)</h2>
        <a href="/judge" data-nav="/judge">Open Interactive Guide →</a>
      </div>
      <div class="walk-grid">
        <div class="walk-cell"><b>1 · Connect</b>Review source labels and confirm the excluded private channels are never read.</div>
        <div class="walk-cell"><b>2 · Prove</b>Click citation chips to inspect character-exact source excerpts for every kept claim.</div>
        <div class="walk-cell"><b>3 · Correct</b>Settle open contradictions with mandatory reviewer sign-off; every decision is logged.</div>
        <div class="walk-cell"><b>4 · Restrict</b>Open the successor handover; verify the plain notice &amp; zero leaked restricted rows.</div>
      </div>
    </div>
    <div class="home-footer">
      <span><b>Demo data:</b> Aster is synthetic and written for this build. Every person, quote and number in it is invented; the pipeline is scored against a private answer key.</span>
      <span><b>Honesty:</b> no loss rate is ever claimed — gaps are listed, never estimated. Replay mode replays recorded model proposals; the checks and plumbing are real.</span>
    </div>
  </div>`;
  $("#cta-demo").addEventListener("click", async (ev) => {
    const btn = ev.currentTarget; btn.disabled = true; btn.textContent = "Loading Aster…";
    try {
      const p = await api("/api/projects/demo", { method: "POST", body: {} });
      store.project = p.id; currentProject = p;
      toast("Aster demo loaded — start with the labels on Connect", "ok");
      nav(`/p/${p.id}/connect`);
    } catch (e) { toast(errText(e), "error"); btn.disabled = false; btn.textContent = "Load Demo Project & Start Flow →"; }
  });
  $("#cta-own").addEventListener("click", async () => {
    try {
      const p = await api("/api/projects", { method: "POST", body: { name: "Untitled handover" } });
      store.project = p.id; currentProject = p;
      toast("Project created — bring your sources on the Connect screen", "ok");
      nav(`/p/${p.id}/connect`);
    } catch (e) { toast(errText(e), "error"); }
  });
}

/* ------------------------------------------------------------------ connect */
const KIND_LABEL = { repo: "REPO", notes: "NOTE", chat: "CHAT", issues: "ISSUE", prs: "PR" };
const LABEL_HELP = { open: "anyone with project access", internal: "project members incl. successor", restricted: "named roles only — hidden from successor", confidential: "reviewer & admin only" };

async function renderConnect(app, project) {
  const sources = await api(`/api/projects/${project.id}/sources`);
  const isReviewer = ["reviewer", "admin"].includes(store.role);
  const locked = !["scoped", "labelled"].includes(project.state);
  const readable = sources.filter(s => s.read_state !== "not read");
  const excluded = sources.filter(s => s.read_state === "not read");
  const allLabelled = readable.every(s => s.label);
  app.innerHTML = `
  <div class="crumbs">Step 1 of 5 · Connect</div>
  <h1 class="display">Bring the trail in — labelled, with consent.</h1>
  <p class="lede">Tether reads exactly three kinds of sources, and only what a named person authorised. Every source gets one label. Private and HR channels are never read — they show up as “not read” with the reason.</p>

  <div class="card">
    <h2 class="card-title">Sources</h2>
    <p class="card-sub">Label = most restrictive reader. One restricted source makes every claim backed by it restricted (weakest source, HR-2).</p>
    <div style="overflow:auto"><table class="source-table" aria-label="Sources and labels">
      <thead><tr><th>Kind</th><th>Source</th><th>Label</th><th>State</th></tr></thead>
      <tbody>
        ${readable.map(s => `
          <tr>
            <td><span class="kind-ic">${KIND_LABEL[s.kind] || "SRC"}</span></td>
            <td><div>${esc(s.name)}</div><div class="small mono">sha256 ${(s.sha256||"").slice(0,12)}…</div></td>
            <td>${isReviewer && !locked
              ? `<select class="label-select" data-sid="${s.id}" aria-label="Label for ${esc(s.name)}">
                   ${["open","internal","restricted","confidential"].map(l => `<option value="${l}" ${s.label===l?"selected":""}>${l}</option>`).join("")}
                 </select>`
              : `<span class="badge badge-label ${s.label||""}" title="${esc(LABEL_HELP[s.label]||"")}">${esc(s.label||"unlabelled")}</span>`}
            </td>
            <td><span class="status-chip ${s.read_state==="read" ? "status-read" : "status-pending"}">${s.read_state}</span></td>
          </tr>`).join("")}
        ${excluded.map(s => `
          <tr>
            <td><span class="kind-ic">🚫</span></td>
            <td><div>${esc(s.name)}</div><div class="small">never opened</div></td>
            <td><span class="badge badge-label">no label</span></td>
            <td><span class="status-chip status-excluded" title="${esc(s.not_read_reason||"excluded")}">not read — ${esc(s.not_read_reason||"excluded")}</span></td>
          </tr>`).join("")}
      </tbody>
    </table></div>
    <p class="excluded-note">Excluded channels stay out of memory entirely — nothing from them is stored, logged, exported or shown. Honeytokens embedded in them exist to prove this.</p>

    <form id="upload-form" style="margin-top:14px">
      <div class="dropzone">
        <div><b>Upload sources</b> — Markdown notes (<code>.md</code>), issues/PRs/chat export (<code>.json</code>), a git bundle (<code>.bundle</code>)</div>
        <div class="small">Make a bundle with <code>git bundle create repo.bundle --all</code>. A <code>manifest.json</code> alongside sets labels and channel exclusions.</div>
        <input type="file" id="upload-files" multiple accept=".md,.markdown,.txt,.json,.bundle" style="margin-top:10px" aria-label="Source files">
      </div>
      <div class="consent">
        <input type="checkbox" id="consent" required>
        <label for="consent">I am allowed to use these sources, and they contain no confidential workplace material that I have no permission to share.</label>
      </div>
      <div class="btn-row">
        <button type="submit" class="btn btn-secondary">Upload &amp; label</button>
        <span class="small" style="align-self:center">Uploads go through the same path as the demo. Nothing is stored before consent is ticked.</span>
      </div>
    </form>

    <div class="gate-strip">
      <div style="font-size:22px">${project.state === "scoped" ? "🔒" : "✅"}</div>
      <div style="flex:1">
        <b>Gate 1 — the reviewer clears the labels before anything is read.</b><br>
        <span class="small">${project.state === "scoped"
          ? (allLabelled ? "All sources are labelled. The reviewer can clear the labels." : "Label every source that will be read, then clear.")
          : "Labels cleared — the rebuild can read these sources."}</span>
      </div>
      ${isReviewer && project.state === "scoped"
        ? `<button class="btn btn-primary" id="clear-labels" ${allLabelled ? "" : "disabled"}>Clear labels →</button>`
        : project.state !== "scoped"
          ? `<button class="btn btn-primary" id="go-rebuild">Rebuild →</button>`
          : `<span class="small">Waiting for the reviewer.</span>`}
    </div>
  </div>`;

  $$(".label-select", app).forEach(sel => sel.addEventListener("change", async () => {
    try {
      const fd = new FormData(); fd.append("label", sel.value);
      await api(`/api/projects/${project.id}/sources/${sel.dataset.sid}`, { method: "PUT", body: fd });
      toast(`label → ${sel.value}`, "ok");
      render();
    } catch (e) { toast(errText(e), "error"); render(); }
  }));
  // PUT expects form data, not JSON
  $("#upload-form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const input = $("#upload-files");
    const consent = $("#consent").checked;
    if (!consent) { toast("Consent is required before anything is stored.", "error"); return; }
    if (!input.files.length) { toast("Choose at least one file.", "error"); return; }
    const fd = new FormData();
    fd.append("consent", "true");
    for (const f of input.files) fd.append("files", f);
    try {
      const r = await api(`/api/projects/${project.id}/sources`, { method: "POST", body: fd });
      toast(`Stored ${r.created.length} source(s). Label them, then clear the gate.`, "ok");
      render();
    } catch (e) { toast(errText(e), "error"); }
  });
  const clearBtn = $("#clear-labels");
  if (clearBtn) clearBtn.addEventListener("click", async () => {
    try {
      await api(`/api/projects/${project.id}/gates/labels`, { method: "POST", body: {} });
      toast("Labels cleared — the rebuild may read these sources.", "ok");
      render();
    } catch (e) { toast(errText(e), "error"); }
  });
  const go = $("#go-rebuild");
  if (go) go.addEventListener("click", () => nav(`/p/${project.id}/rebuild`));
}

/* ------------------------------------------------------------------ rebuild */
async function renderRebuild(app, project) {
  const isReviewer = ["reviewer", "admin"].includes(store.role);
  const latest = await api(`/api/projects/${project.id}/runs/latest`);
  const counts = latest.counts;
  const ran = !!counts;
  const canRun = isReviewer && ["labelled", "rebuilt", "in review"].includes(project.state);
  const dropped = ran ? await api(`/api/projects/${project.id}/dropped`) : [];

  app.innerHTML = `
  <div class="crumbs">Step 2 of 5 · Rebuild</div>
  <h1 class="display">What the project actually says.</h1>
  <p class="lede">One reader per source walks every line. For each claim it proposes a quote; we look for that exact quote in the source. If it isn't there, the claim is dropped and counted — the machine never gets to blur.</p>

  <div class="disclosure"><b>Mode:</b> replay — the extraction model's output was recorded beforehand and is being re-checked live by the deterministic checker (quote found character-for-character, source label, confidence floor). The plumbing and the checks are real; the model's own throughput is not being exercised in this mode.</div>

  ${project.state === "scoped"
    ? `<div class="card"><div class="empty">Labels aren't cleared yet. <a href="/p/${project.id}/connect" data-nav="/p/${project.id}/connect">Clear the labels first →</a></div></div>`
    : `<div class="card">
        <h2 class="card-title">${ran ? "Latest rebuild" : "Not rebuilt yet"}</h2>
        <p class="card-sub">${ran
          ? `Run <code class="mono">${esc(latest.run.id)}</code> · extractor: <b>${esc(counts.extractor)}</b> · finished ${esc(latest.run.finished_at || "")}`
          : "Nothing has been read yet. Run the rebuild when the labels are clear."}</p>
        <div class="btn-row">
          ${canRun ? `<button class="btn btn-primary" id="run-rebuild">${ran ? "Re-run the rebuild" : "Run the rebuild →"}</button>` : ""}
          ${["rebuilt","in review","signed","shared","received"].includes(project.state)
            ? `<a class="btn btn-secondary" href="/p/${project.id}/review" data-nav="/p/${project.id}/review">Go to review →</a>` : ""}
        </div>
        ${ran ? `
        <div class="stat-tiles" aria-label="Rebuild counts">
          ${[
            ["spans", counts.spans, "windows of source walked"],
            ["candidates", counts.candidates, "claims the reader proposed"],
            ["kept", counts.kept, "found back in the source"],
            ["dropped", counts.dropped, "quote not found — not admitted"],
            ["conflicts", counts.conflicts, "sources disagree — reviewer picks"],
            ["gaps", counts.gaps, "not written down anywhere"],
            ["redactions", counts.redactions, "private details masked on read"],
            ["quarantined", counts.quarantined, "failed a safety check"],
          ].map(([k,v,d]) => `<div class="stat-tile"><div class="stat-num">${v ?? 0}</div><div class="stat-name">${k}</div><div class="stat-desc">${esc(d)}</div></div>`).join("")}
        </div>
        ${counts.not_read_sources && counts.not_read_sources.length ? `
          <div class="excluded-note" style="margin-top:10px"><b>Never read:</b> ${counts.not_read_sources.map(s => esc(typeof s === "string" ? s : (s.name || s.id))).join(" · ")} — these were excluded at upload and are absent from memory, log, exports and this screen.</div>` : ""}
        ${counts.extractor === "rules" ? `<div class="excluded-note" style="margin-top:8px"><b>Fewer than ten claims kept</b> — the rules extractor ran as a backup. Treat the queue accordingly; this says nothing about your project.</div>` : ""}
        ` : ""}
      </div>

      ${ran && dropped.length ? `
      <div class="card">
        <h2 class="card-title">Dropped claims <span class="count-chip">${dropped.length}</span></h2>
        <p class="card-sub">Every candidate whose quote could not be found, or that failed a check. Shown so you can see the boundary of what Tether knows.</p>
        <div style="overflow:auto;max-height:380px"><table class="source-table">
          <thead><tr><th>Type</th><th>Claim text (as proposed)</th><th>Quote (as proposed)</th><th>Why dropped</th></tr></thead>
          <tbody>${dropped.map(d => `<tr><td>${esc(d.type||"?")}</td><td class="small">${esc((d.text||"").slice(0,140))}</td><td class="small mono">${esc((d.quote||"").slice(0,120))}</td><td>${esc(d.drop_reason||"quote not found")}</td></tr>`).join("")}</tbody>
        </table></div>
      </div>` : ""}

      ${ran && counts.steps && counts.steps.length ? `
      <div class="card">
        <h2 class="card-title">What happened, step by step</h2>
        <ol class="step-list">${counts.steps.map(s => `<li><b>${esc(s.step)}</b><span class="small">${esc(s.detail||"")}${s.ms != null ? ` · ${s.ms} ms` : ""}</span></li>`).join("")}</ol>
      </div>` : ""}`}
  `;

  const btn = $("#run-rebuild");
  if (btn) btn.addEventListener("click", async () => {
    btn.disabled = true; btn.textContent = "Rebuilding…";
    try {
      toast("Rebuild started — reading sources and checking every quote", "ok");
      const r = await api(`/api/projects/${project.id}/runs`, { method: "POST", body: {} });
      toast(`Kept ${r.counts.kept} claims, dropped ${r.counts.dropped}`, "ok");
      render();
    } catch (e) { toast(errText(e), "error"); btn.disabled = false; btn.textContent = "Re-run the rebuild"; }
  });
}

/* ------------------------------------------------------------------ citation modal */
async function showCitation(spanId, quote) {
  const modal = $("#modal");
  modal.hidden = false;
  $("#cite-locator").textContent = "Loading…";
  $("#cite-meta").textContent = "";
  $("#cite-text").textContent = "";
  $("#cite-redactions").hidden = true;
  const status = $("#cite-status");
  status.hidden = true; status.className = "cite-status"; status.textContent = "";
  try {
    const s = await api(`/api/spans/${encodeURIComponent(spanId)}`);
    const text = s.text || "";
    $("#cite-locator").textContent = s.locator;
    $("#cite-meta").innerHTML = `${esc(s.source_name)} · label <span class="badge badge-label ${esc(s.source_label)}">${esc(s.source_label)}</span> · captured ${esc(s.captured_at || "unknown")} · sha256 <code>${esc((s.sha256||"").slice(0,16))}…</code>`;
    const reds = s.redactions || [];
    if (reds.length) {
      $("#cite-redactions").hidden = false;
      $("#cite-redactions").textContent = `Redacted on read: ${reds.map(r => `${r.count ?? 1}× ${r.kind || "private detail"}`).join(", ")} — the file keeps them masked; nothing sensitive reaches the screen.`;
    }
    if (quote) {
      const i = text.indexOf(quote);
      if (i >= 0) {
        $("#cite-text").innerHTML = esc(text.slice(0, i)) + '<mark class="cite-hit">' + esc(quote) + '</mark>' + esc(text.slice(i + quote.length));
        status.hidden = false; status.classList.add("cite-status-ok");
        status.textContent = "✓ Exact Quote Match (CK-1) — the highlighted region is the quote, nothing more.";
      } else {
        $("#cite-text").textContent = text;
        status.hidden = false; status.classList.add("cite-status-warn");
        status.textContent = "! Quote not found in this span — do not trust the claim it supports.";
      }
    } else {
      $("#cite-text").textContent = text;
    }
  } catch (e) {
    $("#cite-locator").textContent = "Citation restricted";
    $("#cite-meta").textContent = errText(e);
  }
}
(function wireModal() {
  const close = () => { $("#modal").hidden = true; };
  document.addEventListener("click", e => {
    if (e.target.id === "cite-close") close();
    if (e.target.id === "modal") close();
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape") close(); });
})();
document.addEventListener("click", e => {
  const b = e.target.closest("[data-cite]");
  if (b) { e.preventDefault(); showCitation(b.getAttribute("data-cite"), b.getAttribute("data-quote") || ""); }
});

/* ------------------------------------------------------------------ shared bits */
function confidenceTag(c) {
  const n = typeof c.confidence === "number" ? c.confidence : null;
  if (n == null) return "";
  const floor = 0.80;  // mirrors config.CONFIDENCE_VERIFIED_FLOOR
  return `<span class="conf ${n < floor ? "conf-low" : ""}" title="confidence ${n.toFixed(2)} · ${esc(c.confidence_rule || "")}">${n.toFixed(2)}</span>`;
}
const TYPE_CHIP = {"decision":"chip-decision","dependency":"chip-dependency","repeated problem":"chip-repeated","next step":"chip-next","fact":"chip-fact"};
function claimCardHTML(c, mode) {
  const ev = (c.evidence || []).map(e => `
      <div class="evidence-row">
        <div class="evidence-quote">“${esc(e.quote)}”</div>
        <div class="evidence-meta">
          <button class="mono locator-btn" data-cite="${esc(e.span_id)}" data-quote="${esc(e.quote || "")}" title="Open the source line">${esc(e.locator)}</button>
          <span class="badge badge-label ${esc(e.source_label||"")}">${esc(e.source_label||"")}</span>
          <span class="small">${esc(e.captured_at || "")}</span>
        </div>
      </div>`).join("");
  const decided = c.review_state !== "pending";
  const stamp = decided
    ? `<div class="review-stamp stamp-${esc(c.review_state)}">${esc(c.review_state.toUpperCase())}${c.review_reason ? ` — ${esc(c.review_reason)}` : ""}</div>`
    : "";
  return `
  <article class="claim-card ${decided ? "decided" : ""} status-${esc(c.status)}" data-claim="${esc(c.id)}">
    <div class="claim-head">
      <span class="type-chip ${TYPE_CHIP[c.type] || ""}">${esc(c.type)}</span>
      ${c.status === "uncertain" ? '<span class="uncertain-flag">UNCERTAIN</span>' : ""}
      <span class="badge badge-label ${esc(c.label)}" title="weakest source wins — HR-2">${esc(c.label)}</span>
      ${confidenceTag(c)}
      ${c.risk_estimate != null ? `<span class="risk-est" title="${esc(c.risk_rule || "risk estimate")}">risk ${c.risk_estimate}</span>` : ""}
    </div>
    <p class="claim-text">${esc(c.text)}</p>
    ${c.reason ? `<p class="claim-reason"><b>Why:</b> ${esc(c.reason)}${c.rejected_options && c.rejected_options.length ? ` · <b>Rejected:</b> ${esc(c.rejected_options.join("; "))}` : ""}</p>` : ""}
    <div class="evidence-block">${ev || '<div class="small">No in-source quote — this claim cannot be cited.</div>'}</div>
    ${stamp}
    <div class="claim-actions"></div>
  </article>`;
}

/* ------------------------------------------------------------------ review */
let reviewTab = "claims";
let claimFilter = "pending";

function reviewClaimsHTML(claims, role) {
  const counts = claims.reduce((m, c) => { m[c.review_state] = (m[c.review_state]||0)+1; return m; }, {});
  const total = claims.length;
  const pending = claims.filter(c => c.review_state === "pending");
  const settled = claims.filter(c => c.review_state !== "pending");
  const uncertainPending = pending.filter(c => c.status === "uncertain").length;
  const sortedPending = [...pending].sort((a, b) => {
    if (a.status !== b.status) return a.status === "uncertain" ? -1 : 1;
    return (b.risk_estimate||0) - (a.risk_estimate||0);
  });
  const shown = claimFilter === "pending" ? sortedPending : settled;
  return `
    <div class="progress-strip" aria-label="Review progress">
      <span><b>${counts.confirmed||0}</b> confirmed</span>
      <span><b>${counts.edited||0}</b> edited</span>
      <span><b>${counts.rejected||0}</b> rejected</span>
      <span><b>${counts.parked||0}</b> parked</span>
      <span class="${pending.length ? "progress-open" : "progress-done"}"><b>${pending.length}</b> pending${uncertainPending ? ` (${uncertainPending} uncertain)` : ""}</span>
      <span><b>${total}</b> total</span>
    </div>
    <div class="filter-bar" role="group" aria-label="Show">
      <button class="filter-chip ${claimFilter==="pending"?"active":""}" data-filter="pending">Pending · ${pending.length}</button>
      <button class="filter-chip ${claimFilter==="settled"?"active":""}" data-filter="settled">Settled · ${settled.length}</button>
    </div>
    ${shown.length === 0
      ? `<div class="empty">${claimFilter === "pending" ? "Queue clear — nothing pending." : "Nothing settled yet."}</div>`
      : `<div class="claim-list">${shown.map(c => claimCardHTML(c, role)).join("")}</div>`}`;
}

function injectClaimActions(root, claims, role) {
  for (const card of $$(".claim-card", root)) {
    const c = claims.find(x => x.id === card.dataset.claim);
    if (!c) continue;
    const box = $(".claim-actions", card);
    if (role === "reviewer" && c.review_state === "pending") {
      box.innerHTML = `
        <button class="btn btn-primary btn-sm" data-act="confirm">Confirm</button>
        <button class="btn btn-secondary btn-sm" data-act="edit">Edit</button>
        <button class="btn btn-ghost btn-sm" data-act="reject">Reject</button>
        <button class="btn btn-ghost btn-sm" data-act="park">Park</button>`;
    } else if (role === "leaver") {
      box.innerHTML = `<button class="btn btn-secondary btn-sm" data-act="propose">Propose a correction</button>`;
    } else {
      box.innerHTML = role === "admin" ? '<span class="small">read-only — the reviewer decides</span>' : "";
    }
  }
}

async function postClaimAction(project, claimId, payload) {
  return api(`/api/claims/${encodeURIComponent(claimId)}/review`, { method: "POST", body: payload });
}

function bindClaimEvents(root, project, claims, role) {
  root.addEventListener("click", async (e) => {
    const fchip = e.target.closest(".filter-chip[data-filter]");
    if (fchip) { claimFilter = fchip.dataset.filter; render(); return; }
    const btn = e.target.closest("[data-act]");
    if (!btn) return;
    const card = btn.closest(".claim-card");
    const claimId = card.dataset.claim;
    const act = btn.dataset.act;
    const box = $(".claim-actions", card);
    if (act === "confirm") {
      btn.disabled = true;
      try { await postClaimAction(project, claimId, { action: "confirm" }); toast("Confirmed — re-verified against its source.", "ok"); render(); }
      catch (err) { toast(errText(err), "error"); btn.disabled = false; }
    } else if (act === "edit") {
      const current = claims.find(c => c.id === claimId);
      box.innerHTML = `
        <textarea class="edit-area" maxlength="240" rows="2">${esc(current.text)}</textarea>
        <div class="btn-row"><button class="btn btn-primary btn-sm" data-act="save-edit">Save edit</button>
        <button class="btn btn-ghost btn-sm" data-act="cancel">Cancel</button>
        <span class="small">One short sentence, 240 chars — the citation must still hold.</span></div>`;
    } else if (act === "save-edit") {
      const text = $(".edit-area", box).value.trim();
      if (!text) { toast("Edit needs the new text.", "error"); return; }
      btn.disabled = true;
      try { await postClaimAction(project, claimId, { action: "edit", text }); toast("Edited — kept, and logged.", "ok"); render(); }
      catch (err) { toast(errText(err), "error"); btn.disabled = false; }
    } else if (act === "reject" || act === "park") {
      box.innerHTML = `
        <input class="reason-input" type="text" placeholder="${act === "reject" ? "Why is this wrong? (written reason)" : "Why park this? (written reason)"}" aria-label="Reason">
        <div class="btn-row"><button class="btn btn-primary btn-sm" data-act="save-${act}">${act === "reject" ? "Reject with reason" : "Park with reason"}</button>
        <button class="btn btn-ghost btn-sm" data-act="cancel">Cancel</button></div>`;
      $(".reason-input", box).focus();
    } else if (act === "save-reject" || act === "save-park") {
      const reason = $(".reason-input", box).value.trim();
      if (reason.length < 3) { toast("A written reason (3+ chars) is required.", "error"); return; }
      btn.disabled = true;
      const action = act === "save-reject" ? "reject" : "park";
      try { await postClaimAction(project, claimId, { action, reason }); toast(`${action === "reject" ? "Rejected" : "Parked"} — reason logged.`, "ok"); render(); }
      catch (err) { toast(errText(err), "error"); btn.disabled = false; }
    } else if (act === "propose") {
      box.innerHTML = `
        <input class="reason-input" type="text" placeholder="What should change? (your correction)" aria-label="Correction">
        <input class="reason-input" type="text" placeholder="Note for the reviewer (optional)" aria-label="Note">
        <div class="btn-row"><button class="btn btn-primary btn-sm" data-act="save-propose">Send to the reviewer</button>
        <button class="btn btn-ghost btn-sm" data-act="cancel">Cancel</button></div>`;
      $(".reason-input", box).focus();
    } else if (act === "save-propose") {
      const inputs = $$(".reason-input", box);
      const text = inputs[0].value.trim(), note = inputs[1].value.trim();
      if (!text && !note) { toast("A proposal needs text or a note.", "error"); return; }
      btn.disabled = true;
      try { await postClaimAction(project, claimId, { action: "proposal", text, reason: note }); toast("Proposal sent — the reviewer decides what lands.", "ok"); render(); }
      catch (err) { toast(errText(err), "error"); btn.disabled = false; }
    } else if (act === "cancel") {
      render();
    }
  });
}

function conflictCardHTML(cf, role) {
  const decided = cf.state !== "open";
  const sides = (cf.claims || []).map(c => `
    <label class="conflict-side ${decided ? "" : "pickable"}">
      <input type="radio" name="conflict-${esc(cf.id)}" value="${esc(c.value)}" ${decided ? "disabled" : ""} ${decided && cf.decided_value === c.value ? "checked" : ""}>
      <span class="conflict-value">${esc(c.value)}</span>
      <span class="conflict-quote">“${esc(((c.evidence||[])[0]||{}).quote || "")}”</span>
      <span class="conflict-meta">
        <span class="badge badge-label ${esc(c.label)}">${esc(c.label)}</span>
        ${(c.evidence||[])[0] ? `<button class="mono locator-btn" data-cite="${esc(c.evidence[0].span_id)}" data-quote="${esc(c.evidence[0].quote || "")}">${esc(c.evidence[0].locator)}</button>` : ""}
      </span>
    </label>`).join("");
  return `
  <article class="conflict-card ${decided ? "decided" : ""}" data-conflict="${esc(cf.id)}">
    <div class="conflict-head">
      <div><span class="kicker">CONFLICT</span><h3>${esc(cf.subject)} — ${esc(cf.attribute)}</h3></div>
      <span class="state-tag ${decided ? "tag-closed" : "tag-open"}">${esc(cf.state)}</span>
    </div>
    <p class="small">Two sources disagree. The machine does not pick — you do, and your reason is logged with the decision.</p>
    <div class="conflict-sides">${sides}</div>
    ${decided
      ? `<div class="review-stamp stamp-decided">WINNER: ${esc(cf.decided_value || "parked")}${cf.reason ? ` — ${esc(cf.reason)}` : ""}${cf.decided_by ? ` <span class="small">(${esc(cf.decided_by)})</span>` : ""}</div>`
      : role === "reviewer" ? `
      <input class="reason-input" type="text" placeholder="Why? (written reason — logged with the decision)" aria-label="Decision reason">
      <div class="btn-row">
        <button class="btn btn-primary btn-sm" data-cact="decide">Decide — log the winner</button>
        <button class="btn btn-ghost btn-sm" data-cact="park">Park with reason</button>
      </div>` : `<p class="small">Waiting for the reviewer to pick a winner.</p>`}
  </article>`;
}

function gapsHTML(gaps, role) {
  if (!gaps.length) return '<div class="empty">No gaps — every CK-4 subject has a kept claim behind it.</div>';
  return `<div class="gap-list">${gaps.map(g => `
    <article class="gap-card ${g.state !== "open" ? "decided" : ""}" data-gap="${esc(g.id)}">
      <div class="gap-head">
        <div><span class="kicker">GAP${g.state === "suggested" ? " · SUGGESTED" : ""}</span><h3>${esc(g.question || g.subject)}</h3></div>
        <span class="state-tag ${g.state === "open" ? "tag-open" : g.state === "suggested" ? "tag-suggested" : "tag-closed"}">${esc(g.state)}</span>
      </div>
      ${g.state === "open" || g.state === "suggested"
        ? (role === "reviewer" ? `
        <div class="gap-form">
          <input type="text" class="reason-input" data-field="owner" placeholder="Who may know? (owner)" value="${esc(g.owner || "")}" aria-label="Owner">
          <input type="text" class="reason-input" data-field="next_step" placeholder="Next step (how we find out)" value="${esc(g.next_step || "")}" aria-label="Next step">
          <input type="text" class="reason-input" data-field="park_reason" placeholder="Park reason (required only if parking)" aria-label="Park reason">
          <div class="btn-row">
            <button class="btn btn-primary btn-sm" data-gact="assign">Assign &amp; close</button>
            <button class="btn btn-ghost btn-sm" data-gact="park">Park with reason</button>
          </div>
        </div>` : `
        <p class="small"><b>Owner:</b> ${esc(g.owner || "—")} · <b>Next step:</b> ${esc(g.next_step || "—")}</p>`)
        : `<p class="small">${g.state === "closed"
              ? `<b>Owner:</b> ${esc(g.owner || "—")} · <b>Next step:</b> ${esc(g.next_step || "—")}`
              : `<b>Parked:</b> ${esc(g.parked_reason || "")}`}</p>`}
    </article>`).join("")}</div>`;
}

function quarantineHTML(items, role) {
  if (!items.length) return '<div class="empty">Quarantine is empty — no span tripped a safety check.</div>';
  return `<div class="quar-list">${items.map(q => `
    <article class="quar-card" data-quar="${esc(q.id)}">
      <div class="quar-head"><span class="kicker">QUARANTINE</span><span class="small">${esc(q.reason)}</span></div>
      <pre class="quar-excerpt">${esc((q.excerpt || "").slice(0, 600))}</pre>
      ${q.action
        ? `<div class="review-stamp stamp-${esc(q.action === "dismissed" ? "confirmed" : "rejected")}">${esc(q.action.toUpperCase())}</div>`
        : (role === "reviewer" ? `
      <div class="btn-row">
        <button class="btn btn-secondary btn-sm" data-qact="dismissed">Dismiss — not an attack</button>
        <button class="btn btn-ghost btn-sm" data-qact="confirmed">Confirm injection</button>
      </div>` : '<span class="small">awaiting the reviewer</span>')}
    </article>`).join("")}</div>`;
}

function proposalsHTML(props) {
  if (!props.length) return '<div class="empty">No proposals from the leaver yet.</div>';
  return `<div class="prop-list">${props.map(p => {
    let after = p.after || {};
    if (typeof after === "string") { try { after = JSON.parse(after); } catch (_) {} }
    return `
    <article class="prop-card">
      <div class="prop-head"><span class="kicker">PROPOSAL</span><span class="small">${esc(p.actor || "")} · ${esc(p.at || "")}</span></div>
      <p class="claim-text">${esc(after.proposal || after.text || "(no text)")}</p>
      ${after.note || p.reason ? `<p class="small">Note: ${esc(after.note || p.reason)}</p>` : ""}
      <p class="small">On ${esc(p.target_type || "claim")} <code class="mono">${esc((p.target_id || "").slice(0, 18))}…</code> — accept by confirming/editing the claim itself.</p>
    </article>`; }).join("")}</div>`;
}

async function renderReview(app, project) {
  const role = store.role;
  if (role === "successor") {
    app.innerHTML = `<div class="crumbs">Review</div>
      <h1 class="display">The review queue isn't yours.</h1>
      <div class="card"><p>The successor reads the signed handover — not the queue where claims are decided. <a class="btn btn-primary" href="/p/${project.id}/handover" data-nav="/p/${project.id}/handover">Open the handover →</a></p></div>`;
    return;
  }
  const [claims, conflicts, gaps, proposals] = await Promise.all([
    api(`/api/projects/${project.id}/claims`),
    api(`/api/projects/${project.id}/conflicts`),
    api(`/api/projects/${project.id}/gaps`),
    ["reviewer", "admin"].includes(role) ? api(`/api/projects/${project.id}/proposals`) : Promise.resolve([]),
  ]);
  let quarantine = [];
  if (["reviewer", "admin"].includes(role)) {
    try { quarantine = await api(`/api/projects/${project.id}/quarantine`); } catch (_) {}
  }
  const openConflicts = conflicts.filter(c => c.state === "open").length;
  const openGaps = gaps.filter(g => g.state === "open").length;
  const pendingClaims = claims.filter(c => c.review_state === "pending").length;
  const openQuar = quarantine.filter(q => !q.action).length;
  const tabs = [
    ["claims", `Claims · ${pendingClaims} pending`],
    ["conflicts", `Conflicts · ${openConflicts} open`],
    ["gaps", `Gaps · ${openGaps} open`],
    ["quarantine", `Quarantine · ${openQuar}`],
    ["proposals", `Proposals · ${proposals.length}`],
  ];
  app.innerHTML = `
  <div class="crumbs">Step 3 of 5 · Review</div>
  <h1 class="display">Every conflict decided. Every gap owned.</h1>
  <p class="lede">${role === "reviewer"
    ? "Read the quote, not the summary. Pick the winner, write why. Parked items stay visible and never enter the signed handover."
    : role === "leaver" ? "You can read what the system rebuilt and propose corrections — Sanit decides what lands." : "Read-only: the reviewer is the only role that may decide."}</p>
  <div class="tabs" role="tablist">${tabs.map(([id, label]) => `<button class="tab ${reviewTab===id?"active":""}" role="tab" data-tab="${id}">${esc(label)}</button>`).join("")}</div>
  <div id="tab-body">
    ${reviewTab === "claims" ? reviewClaimsHTML(claims, role) : ""}
    ${reviewTab === "conflicts" ? `<div class="conflict-list">${conflicts.length ? conflicts.map(c => conflictCardHTML(c, role)).join("") : '<div class="empty">No conflicts — sources told one story.</div>'}</div>` : ""}
    ${reviewTab === "gaps" ? gapsHTML(gaps, role) : ""}
    ${reviewTab === "quarantine" ? quarantineHTML(quarantine, role) : ""}
    ${reviewTab === "proposals" ? proposalsHTML(proposals) : ""}
  </div>`;
  const body = $("#tab-body");
  const tabsEl = $(".tabs", app);
  tabsEl.addEventListener("click", e => {
    const t = e.target.closest(".tab[data-tab]");
    if (t) { reviewTab = t.dataset.tab; render(); }
  });
  if (reviewTab === "claims") { injectClaimActions(body, claims, role); bindClaimEvents(body, project, claims, role); }
  body.addEventListener("click", async (e) => {
    const cbtn = e.target.closest("[data-cact]");
    if (cbtn) {
      const card = cbtn.closest(".conflict-card");
      const cf = conflicts.find(x => x.id === card.dataset.conflict);
      const reason = $(".reason-input", card).value.trim();
      if (reason.length < 3) { toast("A written reason (3+ chars) is required.", "error"); return; }
      const picked = $(`input[name="conflict-${cf.id}"]:checked`, card);
      if (cbtn.dataset.cact === "decide" && !picked) { toast("Pick the winning value first.", "error"); return; }
      cbtn.disabled = true;
      try {
        await api(`/api/conflicts/${encodeURIComponent(cf.id)}/decide`, { method: "POST", body: cbtn.dataset.cact === "decide" ? { value: picked.value, reason } : { park: true, reason } });
        toast(cbtn.dataset.cact === "decide" ? "Decision logged." : "Parked with reason.", "ok");
        render();
      } catch (err) { toast(errText(err), "error"); cbtn.disabled = false; }
      return;
    }
    const gbtn = e.target.closest("[data-gact]");
    if (gbtn) {
      const card = gbtn.closest(".gap-card");
      const gapId = card.dataset.gap;
      if (gbtn.dataset.gact === "assign") {
        const owner = $('[data-field="owner"]', card).value.trim();
        const next_step = $('[data-field="next_step"]', card).value.trim();
        if (!owner || !next_step) { toast("Assign needs an owner and a next step.", "error"); return; }
        gbtn.disabled = true;
        try { await api(`/api/gaps/${encodeURIComponent(gapId)}/assign`, { method: "POST", body: { owner, next_step } }); toast("Gap assigned and closed.", "ok"); render(); }
        catch (err) { toast(errText(err), "error"); gbtn.disabled = false; }
      } else {
        const parkInput = $('[data-field="park_reason"]', card);
        const reason = (parkInput ? parkInput.value : "").trim();
        if (reason.length < 3) { toast("Park needs a written reason in the field above.", "error"); return; }
        gbtn.disabled = true;
        try { await api(`/api/gaps/${encodeURIComponent(gapId)}/assign`, { method: "POST", body: { park: true, reason } }); toast("Gap parked with reason.", "ok"); render(); }
        catch (err) { toast(errText(err), "error"); gbtn.disabled = false; }
      }
      return;
    }
    const qbtn = e.target.closest("[data-qact]");
    if (qbtn) {
      const card = qbtn.closest(".quar-card");
      qbtn.disabled = true;
      try { await api(`/api/quarantine/${encodeURIComponent(card.dataset.quar)}/act`, { method: "POST", body: { action: qbtn.dataset.qact } }); toast(`Marked ${qbtn.dataset.qact}.`, "ok"); render(); }
      catch (err) { toast(errText(err), "error"); qbtn.disabled = false; }
    }
  });
}

/* ------------------------------------------------------------------ sign-off */
const GATE_LABELS = { gate1_labels: ["Gate 1 — labels cleared", "No source is read before the reviewer clears its label."],
                      gate2_conflicts: ["Gate 2a — conflicts decided", "Every disagreement has a winner and a written reason, or is parked with one."],
                      gate2_uncertain: ["Gate 2b — uncertain items settled", "Nothing the reader was unsure about slips through silently."],
                      gate3_citation: ["Gate 3 — citation test 100%", "Every confirmed claim's quote is found back in the source it came from."] };

async function renderSignoff(app, project) {
  const role = store.role;
  if (!["reviewer", "admin"].includes(role)) {
    app.innerHTML = `<div class="crumbs">Step 4 of 5 · Sign</div>
      <h1 class="display">Sign-off belongs to the reviewer.</h1>
      <div class="card"><p class="card-sub">${role === "successor" ? "You will get the handover once it is signed and shared." : "The leaver proposes; Sanit Salve signs. You are valuable at the review step instead."}</p>
      <a class="btn btn-primary" href="/p/${project.id}/${role === "successor" ? "handover" : "review"}" data-nav="/p/${project.id}/${role === "successor" ? "handover" : "review"}">${role === "successor" ? "Open the handover →" : "Go to review →"}</a></div>`;
    return;
  }
  const gates = await api(`/api/projects/${project.id}/gates`);
  const signed = ["signed", "shared", "received"].includes(project.state);
  let version = null;
  if (signed) { try { version = await api(`/api/projects/${project.id}/versions/latest`); } catch (_) {} }
  app.innerHTML = `
  <div class="crumbs">Step 4 of 5 · Sign</div>
  <h1 class="display">The gates are the product.</h1>
  <p class="lede">Sign-off is refused unless every gate below passes. There is no override button — that is deliberate: the machine can't sign, and neither can anyone who skipped the work.</p>
  <div class="card">
    <h2 class="card-title">Gate report <span class="state-tag ${gates.all ? "tag-closed" : "tag-open"}">${gates.all ? "ALL PASS" : "BLOCKED"}</span></h2>
    <p class="card-sub">${gates.confirmed_or_edited} confirmed/edited claim(s) in the version so far.</p>
    <ul class="gate-list">${Object.entries(GATE_LABELS).map(([key, [title, help]]) => {
      const g = gates[key];
      return `<li class="gate ${g.ok ? "gate-ok" : "gate-fail"}">
        <span class="gate-mark">${g.ok ? "✓" : "✕"}</span>
        <span class="gate-body"><b>${esc(title)}</b><br><span class="small">${esc(g.detail)}</span><br><span class="gate-help">${esc(help)}</span></span>
      </li>`; }).join("")}
    </ul>
    ${!signed ? (role === "reviewer"
      ? `<div class="btn-row"><button class="btn btn-amber" id="sign-btn" ${gates.all ? "" : "disabled"}>Sign — freeze the handover</button>
         ${gates.all ? "" : '<span class="small" style="align-self:center">Fix the red gates in Review. The button unlocks itself when they pass.</span>'}</div>`
      : '<p class="small">Admin read-only — only Sanit Salve may sign.</p>') : ""}
  </div>
  ${signed && version ? `
  <div class="card version-card">
    <h2 class="card-title">Version ${esc(version.number)} — signed &amp; frozen</h2>
    <div class="kv">
      <dt>Signed by</dt><dd>${esc(version.signed_by)} · ${esc(version.signed_at || "")}</dd>
      <dt>SHA-256</dt><dd><code class="mono">${esc(version.sha256)}</code></dd>
      <dt>State</dt><dd>${esc(project.state)}</dd>
    </div>
    <p class="card-sub" style="margin-top:10px">The hash covers the payload — items, gaps, reasons. Any later edit breaks it. Verification is re-run on every gate call and on demand in Admin.</p>
    <div class="btn-row">
      ${project.state === "signed" ? `<button class="btn btn-primary" id="share-btn">Share with the successor</button>` : ""}
      <a class="btn btn-secondary" href="/p/${project.id}/handover" data-nav="/p/${project.id}/handover">Open the handover →</a>
    </div>
  </div>` : ""}`;
  const signBtn = $("#sign-btn");
  if (signBtn) signBtn.addEventListener("click", async () => {
    signBtn.disabled = true; signBtn.textContent = "Signing…";
    try {
      const v = await api(`/api/projects/${project.id}/versions/sign`, { method: "POST", body: {} });
      toast(`${v.number} signed — ${v.items} items frozen.`, "ok");
      render();
    } catch (e) {
      toast((e.status === 409 && e.data && e.data.gates) ? "Sign-off refused — a gate failed. The report above shows which." : errText(e), "error");
      render();
    }
  });
  const shareBtn = $("#share-btn");
  if (shareBtn) shareBtn.addEventListener("click", async () => {
    shareBtn.disabled = true;
    try { await api(`/api/projects/${project.id}/share`, { method: "POST", body: {} }); toast("Shared — the successor can now open it.", "ok"); render(); }
    catch (e) { toast(errText(e), "error"); shareBtn.disabled = false; }
  });
}

/* ------------------------------------------------------------------ handover */
function handoverItemHTML(it) {
  const ev = (it.evidence || []).slice(0, 1).map(e => `
      <div class="handover-cite">“${esc(e.quote)}”
        <button class="mono locator-btn" data-cite="${esc(e.span_id)}" data-quote="${esc(e.quote || "")}" title="Open the source line">${esc(e.locator)}</button>
        <span class="badge badge-label ${esc(e.source_label||"")}">${esc(e.source_label||"")}</span>
      </div>`).join("");
  return `
  <article class="handover-item">
    <div class="claim-head"><span class="type-chip ${TYPE_CHIP[it.type] || ""}">${esc(it.type)}</span>${confidenceTag(it)}${it.risk_estimate != null ? `<span class="risk-est" title="${esc(it.risk_rule || "")}">risk ${it.risk_estimate}</span>` : ""}</div>
    <p class="claim-text">${esc(it.text)}</p>
    ${it.reason ? `<p class="claim-reason"><b>Why:</b> ${esc(it.reason)}${it.rejected_options && it.rejected_options.length ? ` · <b>Rejected:</b> ${esc(it.rejected_options.join("; "))}` : ""}</p>` : ""}
    ${ev}
  </article>`;
}
function handoverGapHTML(g) {
  const state = g.state === "parked" ? `<span class="state-tag tag-open">parked — ${esc(g.parked_reason || "")}</span>` : "";
  return `
  <article class="handover-item gap">
    <div class="claim-head"><span class="type-chip chip-gap">GAP</span>${state}</div>
    <p class="claim-text">${esc(g.question || g.subject)}</p>
    <p class="claim-reason"><b>Who may know:</b> ${esc(g.owner || "unassigned")} · <b>Next step:</b> ${esc(g.next_step || "—")}</p>
  </article>`;
}

async function renderHandover(app, project) {
  const role = store.role;
  let ho;
  try { ho = await api(`/api/projects/${project.id}/handover`); }
  catch (e) {
    app.innerHTML = `<div class="crumbs">Step 5 of 5 · Handover</div>
      <h1 class="display">The handover isn't open yet.</h1>
      <div class="card"><p class="card-sub">${esc(errText(e))}</p>
      <a class="btn btn-primary" href="/p/${project.id}/signoff" data-nav="/p/${project.id}/signoff">Go to sign-off →</a></div>`;
    return;
  }
  app.innerHTML = `
  <div class="crumbs">Step 5 of 5 · Handover</div>
  <div class="handover-banner">
    <div>
      <div class="kicker">SIGNED HANDOVER · ${esc(ho.version.number)}</div>
      <h1 class="display" style="margin:6px 0 4px">${esc(ho.project.name)} <span class="codename">· ${esc(ho.project.codename)}</span></h1>
      <div class="small">Signed by ${esc(ho.version.signed_by)} on ${esc(ho.version.signed_at)} · SHA-256 <code class="mono">${esc((ho.version.sha256||"").slice(0, 20))}…</code></div>
      <div class="small" style="margin-top:4px">Risk order ranks the work — it never ranks people. Evidence: one quote per claim. What nobody knows stays visible below.</div>
    </div>
    <div class="handover-actions">
      <button class="btn btn-secondary" id="print-btn">Print / save PDF</button>
      ${role === "successor" ? (ho.receipt
        ? `<span class="receipt-done">✓ Receipt logged</span>`
        : `<button class="btn btn-amber" id="receipt-btn">I received this handover — log it</button>`) : ""}
    </div>
  </div>
  ${ho.restricted_notice ? `<div class="restricted-notice">🔒 ${esc(ho.restricted_notice)} Everything you see below has been filtered for the ${esc(ho.role)} role; the signed file itself is unchanged.</div>` : ""}
  <div class="sections-grid">${ho.sections.filter(s => s.items.length).map(s => `
    <section class="section-card" aria-label="${esc(s.title)}">
      <div class="section-head"><h2>${esc(s.title)} <span class="count-chip">${s.items.length}</span></h2><p class="small">${esc(s.hint)}</p></div>
      <div class="section-items">${s.items.map(it => s.kind === "gaps" ? handoverGapHTML(it) : handoverItemHTML(it)).join("")}</div>
    </section>`).join("")}</div>
  <div class="handover-foot">Risk rule (from the signed file): ${esc(ho.risk_rule || "estimate · ranks work, never people")}</div>`;
  const printBtn = $("#print-btn");
  if (printBtn) printBtn.addEventListener("click", () => window.print());
  const receiptBtn = $("#receipt-btn");
  if (receiptBtn) receiptBtn.addEventListener("click", async () => {
    receiptBtn.disabled = true;
    try { await api(`/api/projects/${project.id}/receipt`, { method: "POST", body: {} }); toast("Receipt logged — thank you. The leaver can now close the loop.", "ok"); render(); }
    catch (e) { toast(errText(e), "error"); receiptBtn.disabled = false; }
  });
}

/* ------------------------------------------------------------------ admin */
async function renderAdmin(app, project) {
  const role = store.role;
  if (role !== "admin") {
    app.innerHTML = `<div class="crumbs">Admin</div>
      <h1 class="display">Admin belongs to ops.</h1>
      <div class="card"><p class="card-sub">Switch to Krushna Patil (Admin) in the rail to manage retention, the audit log, export and deletion.</p></div>`;
    return;
  }
  const [logData] = await Promise.all([api(`/api/projects/${project.id}/log?verify=1`)]);
  const rows = (logData.rows || []).slice(-40).reverse();
  const chain = logData.chain || {};
  app.innerHTML = `
  <div class="crumbs">Admin · ${esc(project.name)}</div>
  <h1 class="display">Sources, retention, the log.</h1>
  <p class="lede">Every action in Tether is appended to a hash-chained log. Nothing edits a past line; you can verify the chain end to end from here.</p>

  <div class="card">
    <h2 class="card-title">Audit log <span class="state-tag ${chain.ok ? "tag-closed" : "tag-open"}">${chain.ok ? `CHAIN OK · ${chain.rows} lines` : "CHAIN BROKEN"}</span></h2>
    <p class="card-sub">Head <code class="mono">${esc((chain.head||"").slice(0, 24))}…</code> — the most recent 40 of ${logData.rows ? logData.rows.length : 0} lines. Detail JSON truncated for reading; the file itself keeps everything.</p>
    <div style="overflow:auto;max-height:420px"><table class="source-table log-table">
      <thead><tr><th>When</th><th>Who</th><th>Action</th><th>Object</th><th>Detail</th></tr></thead>
      <tbody>${rows.map(r => `<tr>
        <td class="mono small">${esc((r.at||"").replace("T", " ").slice(0, 19))}</td>
        <td>${esc(r.actor)} <span class="small">(${esc(r.role)})</span></td>
        <td><code>${esc(r.action)}</code></td>
        <td class="mono small">${esc(String(r.object||"").slice(0, 18))}</td>
        <td class="small">${esc(String(r.detail||"").slice(0, 110))}</td>
      </tr>`).join("")}</tbody>
    </table></div>
    <div class="btn-row" style="margin-top:12px"><button class="btn btn-secondary" id="verify-chain">Re-verify the chain from genesis</button></div>
  </div>

  <div class="card">
    <h2 class="card-title">Retention</h2>
    <p class="card-sub">Raw source spans are kept for <b>${esc(project.retention_days ?? 30)}</b> days, then deleted. The signed handover and the log persist.</p>
    <form id="retention-form" class="btn-row">
      <input type="number" min="1" max="365" class="reason-input" style="width:120px" id="retention-days" value="${esc(project.retention_days ?? 30)}" aria-label="Retention days">
      <span class="small" style="align-self:center">days</span>
      <button class="btn btn-secondary" type="submit">Set retention</button>
    </form>
  </div>

  <div class="card">
    <h2 class="card-title">Export</h2>
    <p class="card-sub">Everything Tether holds about this project — sources, claims, evidence, gaps, quarantine, reviews, versions, the full log — as one JSON file. Every export is logged.</p>
    <div class="btn-row"><button class="btn btn-primary" id="export-btn">Download export (JSON)</button></div>
  </div>

  <div class="card danger-zone">
    <h2 class="card-title">Deletion</h2>
    <p class="card-sub">A person may ask for their rows to be deleted — that request is logged, and the project is kept until you act. Deleting the project removes sources, claims, versions and the log of this project. This cannot be undone.</p>
    <form id="delete-request-form" class="btn-row" style="margin-bottom:10px">
      <input type="text" class="reason-input" id="delete-request-detail" value="a person asked for their rows to be deleted" aria-label="Request detail">
      <button class="btn btn-secondary" type="submit">Log a deletion request</button>
    </form>
    <div class="btn-row">
      <button class="btn btn-ghost" id="arm-delete">Delete this project…</button>
      <button class="btn btn-danger" id="confirm-delete" hidden>Click again — permanently delete “${esc(project.name)}”</button>
    </div>
  </div>`;

  $("#verify-chain").addEventListener("click", async (e) => {
    const btn = e.currentTarget; btn.disabled = true; btn.textContent = "Verifying…";
    try {
      const r = await api(`/api/projects/${project.id}/verify-chain`, { method: "POST", body: {} });
      toast(r.ok ? `Chain intact — ${r.rows} lines verified from genesis.` : `CHAIN BROKEN at line ${r.broken_at}.`, r.ok ? "ok" : "error");
    } catch (err) { toast(errText(err), "error"); }
    btn.disabled = false; btn.textContent = "Re-verify the chain from genesis";
  });
  $("#retention-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const days = parseInt($("#retention-days").value, 10);
    const fd = new FormData(); fd.append("days", String(days));
    try { const r = await api(`/api/projects/${project.id}/retention`, { method: "PUT", body: fd }); toast(`Retention set to ${r.retention_days} days.`, "ok"); render(); }
    catch (err) { toast(errText(err), "error"); }
  });
  $("#delete-request-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(); fd.append("detail", $("#delete-request-detail").value.trim());
    try { await api(`/api/projects/${project.id}/delete-request`, { method: "POST", body: fd }); toast("Deletion request logged.", "ok"); }
    catch (err) { toast(errText(err), "error"); }
  });
  $("#export-btn").addEventListener("click", async () => {
    try {
      const res = await fetch(`/api/projects/${project.id}/export`, { headers: { "X-Tether-Role": store.role } });
      if (!res.ok) throw new Error(`export failed (${res.status})`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `tether-export-${project.id}.json`; a.click();
      URL.revokeObjectURL(url);
      toast("Export downloaded — the download itself was logged.", "ok");
    } catch (err) { toast(err.message || "export failed", "error"); }
  });
  const arm = $("#arm-delete"), confirmBtn = $("#confirm-delete");
  arm.addEventListener("click", () => { arm.hidden = true; confirmBtn.hidden = false; });
  confirmBtn.addEventListener("click", async () => {
    confirmBtn.disabled = true;
    try {
      await api(`/api/projects/${project.id}`, { method: "DELETE" });
      store.project = null; currentProject = null;
      toast("Project deleted. The log line for the deletion was written first.", "ok");
      nav("/");
    } catch (err) { toast(errText(err), "error"); confirmBtn.disabled = false; }
  });
}

/* ------------------------------------------------------------------ judge */
function renderJudge(app) {
  app.innerHTML = `
  <div class="judge-page">
    <div class="crumbs">For judges &amp; reviewers</div>
    <h1 class="display">Tether, in one page.</h1>
    <p class="lede">Tether is a knowledge-handover product: when the person who knows the project leaves, it rebuilds what they knew into claims that carry their own evidence, forces the disagreements and the unknowns into the open, gives the decisions to a named human reviewer, and freezes the result into a signed file the successor can open on day one. Everything in this demo is synthetic.</p>

    <div class="judge-grid">
      <div class="card judge-card">
        <h2 class="card-title">The golden path (10 minutes)</h2>
        <ol class="judge-steps">
          <li><b>Home → Load the Aster demo project.</b> Synthetic campus-club events app written for this demo. No real person, system or number is represented.</li>
          <li><b>Connect.</b> Tick consent; 58 sources appear with labels. Two channels — <code>#hr-leave</code> and <code>#private-aarav</code> — never appear as readable: they are not read at all. Clear the labels as Sanit.</li>
          <li><b>Rebuild.</b> One pass over 165 spans. 63 candidates proposed; the quote check keeps 61 and drops the rest, counting each drop as evidence the checker works.</li>
          <li><b>Review.</b> Conflicts: pick a winner, write why. Gaps: assign an owner or park with a reason. Uncertain claims: confirm or park. Quarantine: read the injection attempt the reader tripped on.</li>
          <li><b>Sign.</b> Four gates must pass — labels, conflicts, uncertain items, citation test at 100%. No override exists.</li>
          <li><b>Handover.</b> Switch role to Diya (successor). Restricted material is filtered server-side; she sees her sections, an open list of unknowns, and logs a receipt.</li>
        </ol>
      </div>

      <div class="card judge-card">
        <h2 class="card-title">What is real vs recorded</h2>
        <div class="kv">
          <dt>Real</dt><dd>Consent enforcement, label policy (HR-2 weakest source), quote verification character-for-character, the conflict/gap queues, the gates, the signature, the restriction filter, the hash-chained audit log, the deletion request path.</dd>
          <dt>Recorded</dt><dd>The extraction model's answers (replay mode). The model calls are not exercised live in this demo; a live mode exists and is documented in <code>docs/LIMITATIONS.md</code>. Replay proves the plumbing and the checks — it cannot and does not prove model quality.</dd>
          <dt>Synthetic</dt><dd>The whole Aster project — people, quotes, tickets, chat. Marked as such at every entrance. No personal data ever left any real system, because none was used.</dd>
          <dt>Never claimed</dt><dd>A loss-rate or accuracy percentage Tether did not measure. "Knowledge captured" scores. Model skill. Anything about real workplaces.</dd>
        </div>
      </div>
    </div>

    <div class="card judge-card">
      <h2 class="card-title">Architecture at a glance</h2>
      <svg viewBox="0 0 960 210" class="arch-svg" role="img" aria-label="Pipeline diagram">
        <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>
        <g font-family="inherit" font-size="12" fill="currentColor">
          <rect x="6" y="60" width="130" height="74" rx="10" fill="none" stroke="currentColor" stroke-width="1.6"/>
          <text x="71" y="90" text-anchor="middle" font-weight="700">Sources</text>
          <text x="71" y="110" text-anchor="middle" font-size="10">repo · issues · PRs · chat · notes</text>
          <line x1="136" y1="97" x2="168" y2="97" stroke="currentColor" stroke-width="1.6" marker-end="url(#arr)"/>
          <rect x="172" y="60" width="140" height="74" rx="10" fill="none" stroke="currentColor" stroke-width="1.6"/>
          <text x="242" y="88" text-anchor="middle" font-weight="700">Redact on read</text>
          <text x="242" y="106" text-anchor="middle" font-size="10">emails · phones · keys masked</text>
          <text x="242" y="122" text-anchor="middle" font-size="10">never stored raw</text>
          <line x1="312" y1="97" x2="344" y2="97" stroke="currentColor" stroke-width="1.6" marker-end="url(#arr)"/>
          <rect x="348" y="60" width="150" height="74" rx="10" fill="none" stroke="currentColor" stroke-width="1.6"/>
          <text x="423" y="88" text-anchor="middle" font-weight="700">Reader (replay)</text>
          <text x="423" y="106" text-anchor="middle" font-size="10">proposes claim + quote</text>
          <text x="423" y="122" text-anchor="middle" font-size="10">never decides</text>
          <line x1="498" y1="97" x2="530" y2="97" stroke="currentColor" stroke-width="1.6" marker-end="url(#arr)"/>
          <rect x="534" y="60" width="150" height="74" rx="10" fill="none" stroke="currentColor" stroke-width="1.6"/>
          <text x="609" y="88" text-anchor="middle" font-weight="700">Deterministic checks</text>
          <text x="609" y="106" text-anchor="middle" font-size="10">quote found exactly → keep</text>
          <text x="609" y="122" text-anchor="middle" font-size="10">else dropped + counted</text>
          <line x1="684" y1="97" x2="716" y2="97" stroke="currentColor" stroke-width="1.6" marker-end="url(#arr)"/>
          <rect x="720" y="18" width="234" height="172" rx="12" fill="none" stroke="currentColor" stroke-width="2.2"/>
          <text x="837" y="46" text-anchor="middle" font-weight="700">Human review</text>
          <text x="837" y="68" text-anchor="middle" font-size="10">conflicts → winner + reason</text>
          <text x="837" y="84" text-anchor="middle" font-size="10">gaps → owner + next step</text>
          <text x="837" y="100" text-anchor="middle" font-size="10">uncertain → settle or park</text>
          <text x="837" y="116" text-anchor="middle" font-size="10">sign → gates must all pass</text>
          <text x="837" y="140" text-anchor="middle" font-size="11" font-weight="700">→ signed v1.0 → successor</text>
          <text x="837" y="162" text-anchor="middle" font-size="10">restricted items filtered server-side</text>
        </g>
      </svg>
    </div>

    <div class="judge-grid">
      <div class="card judge-card">
        <h2 class="card-title">Run it yourself</h2>
        <pre class="judge-code">make setup    # venv + pinned deps
make seed     # fresh synthetic Aster demo (stops at the label gate)
make run      # http://localhost:8000 — one process, API + UI
make verify   # self-check: DB, files, fixtures, chain
make test     # the test-suite: gates, roles, injection, E2E</pre>
        <p class="small">Docker is not available on this build machine; a <code>docker-compose.yml</code> is included for fidelity, but the verified path is the two commands above. Honesty over ceremony.</p>
      </div>
      <div class="card judge-card">
        <h2 class="card-title">Where the thinking is</h2>
        <ul class="judge-why">
          <li><b>HR-2 weakest source.</b> One restricted source makes every claim backed by it restricted. Labels are assigned per source and enforced per claim server-side — the successor never receives a filtered page because a row was mis-tagged.</li>
          <li><b>The machine never decides.</b> Conflicts and gaps are surfaced, not resolved. A named reviewer wins every tie.</li>
          <li><b>Parked ≠ deleted.</b> Parked claims and gaps leave the signed file visibly marked — silence would lie to the successor.</li>
          <li><b>Weakest link logging.</b> Honeytokens live in the two not-read channels; if they ever surface anywhere, the read path is broken by definition.</li>
          <li><b>Counts, not percentages.</b> Tether reports spans, kept, dropped and reasons — never a completeness score it cannot earn.</li>
        </ul>
      </div>
    </div>
    <p class="home-footer"><span><b>Data:</b> 100% synthetic.</span><span><b>Mode:</b> replay — the model call is recorded; checks and plumbing are live.</span><span><b>Limitations:</b> <code>docs/LIMITATIONS.md</code></span></p>
  </div>`;
}
