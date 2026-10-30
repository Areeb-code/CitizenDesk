const API = "";
const state = {
  view: "dashboard",
  dashboard: null,
  complaints: [],
  contacts: [],
  apiOnline: false,
  ollamaOnline: false,
  modelAvailable: false,
  modelReady: false,
  ollamaStatus: null,
  installedModels: [],
  currentModel: "",
  modelDirectory: "",
  ggufFiles: [],
  selectedContactIds: new Set(),
  contactSearch: "",
  activeRun: false,
  activeCase: null,
  pendingComplaint: null,
  currentDraft: 0,
  recordFilter: "all",
  recordSearch: "",
};

const ICONS = {
  grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  "plus-square": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M12 8v8M8 12h8"/>',
  layers: '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>',
  contact: '<rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="9" cy="10" r="2.2"/><path d="M5.8 16c.7-1.7 2-2.5 3.2-2.5s2.5.8 3.2 2.5M15 9h3M15 13h3M15 17h3"/>',
  "shield-check": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
  "more-horizontal": '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
  "refresh-cw": '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M5.6 9A7 7 0 0 1 18 6l2 6M4 12l2 6a7 7 0 0 0 12.4-3"/>',
  "circle-help": '<circle cx="12" cy="12" r="9"/><path d="M9.6 9a2.5 2.5 0 1 1 4.2 1.8c-1.2 1-1.8 1.5-1.8 3M12 17h.01"/>',
  "arrow-up-right": '<path d="M7 17 17 7M7 7h10v10"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  search: '<circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 4.5 4.5"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h8"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  map: '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z"/><path d="M9 3v15M15 6v15"/>',
  searchcheck: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 4 4M8 10.5l1.7 1.7 3.3-3.5"/>',
  filecheck: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 14l2 2 5-5"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
  phone: '<path d="M7 3H5a2 2 0 0 0-2 2c0 8.8 7.2 16 16 16a2 2 0 0 0 2-2v-2l-5-2-2 2a14 14 0 0 1-7-7l2-2-2-5Z"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>',
  alert: '<path d="m10.3 3.9-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3.1l-8-14a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
  "external-link": '<path d="M14 3h7v7M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
  x: '<path d="m18 6-12 12M6 6l12 12"/>',
  trash: '<path d="M3 6h18M8 6V4h8v2m3 0-1 14H6L5 6m4 4v6m6-6v6"/>',
  copy: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
  "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
  "chevron-left": '<path d="m15 18-6-6 6-6"/>',
  "chevron-down": '<path d="m6 9 6 6 6-6"/>',
  activity: '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
  "file-plus": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M12 12v6M9 15h6"/>',
  "list-checks": '<path d="m3 6 2 2 4-4M3 13l2 2 4-4M3 20l2 2 4-4M13 6h8M13 13h8M13 20h8"/>',
  "building-2": '<path d="M3 21h18M5 21V5l7-3 7 3v16M9 9h.01M15 9h.01M9 13h.01M15 13h.01M10 21v-4h4v4"/>',
  cpu: '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 9h6v6H9zM9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M3 9h18"/>',
  harddrive: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 15h.01M11 15h.01M3 10h18"/>',
};

function icon(name, size = 16) {
  const body = ICONS[name] || ICONS.file;
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${body}</svg>`;
}
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function shortDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "—";
  return new Intl.DateTimeFormat(undefined, { day: "2-digit", month: "short", year: "numeric" }).format(d);
}
function getIssue(item) {
  return item?.facts?.issue || item?.complaint || "Untitled complaint";
}
function getCaseStatus(item) {
  if (item?.review?.passed === true) return { label: "Reviewed", tone: "good" };
  if (item?.status === "manual_review" || item?.status === "needs_info" || item?.status === "save_failed" || item?.review?.passed === false) return { label: "Needs attention", tone: "warning" };
  return { label: "Saved", tone: "neutral" };
}
function setIconMarkup() {
  document.querySelectorAll("[data-icon]").forEach(el => { el.innerHTML = icon(el.dataset.icon); });
}
function toast(message, type = "success") {
  const region = document.getElementById("toast-region");
  const el = document.createElement("div");
  el.className = `toast ${type === "error" ? "error" : ""}`;
  el.textContent = message;
  region.appendChild(el);
  window.setTimeout(() => { el.style.opacity = "0"; el.style.transform = "translateY(6px)"; window.setTimeout(() => el.remove(), 220); }, 3400);
}

async function apiGet(path) {
  const response = await fetch(`${API}${path}`, { headers: { "Accept": "application/json" } });
  if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || `Request failed (${response.status})`);
  return response.json();
}
async function loadData() {
  try {
    const [health, dashboard, complaints, contacts, modelSettings] = await Promise.all([
      apiGet("/api/health"), apiGet("/api/dashboard"), apiGet("/api/complaints"),
      apiGet("/api/contacts"), apiGet("/api/settings/models").catch(() => null),
    ]);
    state.apiOnline = !!health.ok;
    state.ollamaStatus = health.ollama || null;
    state.ollamaOnline = !!health.ollama?.online;
    state.modelAvailable = !!health.ollama?.model_available;
    state.modelReady = !!health.model_ready;
    state.dashboard = dashboard;
    state.complaints = complaints.items || [];
    state.contacts = contacts.items || [];
    state.installedModels = modelSettings?.models || health.ollama?.models || [];
    state.currentModel = modelSettings?.current_model || health.model || "";
  } catch (error) {
    state.apiOnline = false;
    state.ollamaOnline = false;
    state.modelAvailable = false;
    state.modelReady = false;
    state.ollamaStatus = null;
    state.dashboard = null;
    state.complaints = [];
    state.contacts = [];
    state.installedModels = [];
  }
  updateConnection();
  document.getElementById("nav-record-count").textContent = String(state.complaints.length);
}

function updateConnection() {
  const led = document.getElementById("api-led");
  const label = document.getElementById("api-status");
  const online = state.apiOnline && state.modelReady;
  led.className = `status-led ${online ? "online" : "offline"}`;
  if (!state.apiOnline) label.textContent = "Local API unavailable";
  else if (!state.ollamaOnline) label.textContent = "Ollama is offline";
  else if (!state.modelAvailable) label.textContent = "Local model not installed";
  else label.textContent = "Local services ready";
}
function ollamaNotice() {
  const details = state.ollamaStatus || {};
  if (!state.apiOnline) {
    return `<div class="service-notice danger"><strong>CitizenDesk API is not running.</strong><p>Start the FastAPI service in your project terminal, then refresh this page.</p><code>python -m uvicorn app.api:app --reload</code></div>`;
  }
  if (state.modelReady) return "";
  const offline = !details.online;
  const title = offline ? "Ollama is not reachable from CitizenDesk." : `The selected model ${esc(details.model || "")} is not installed.`;
  const instructions = offline
    ? "The connection-refused error (WinError 10061) means nothing is accepting connections at the configured Ollama address. Open the Ollama desktop app. Only run 'ollama serve' if the desktop service is not already running; if it says port 11434 is in use, do not start another copy."
    : "Open Settings & models to choose an installed model, or scan a folder for a standalone GGUF model.";
  return `<div class="service-notice danger"><strong>${title}</strong><p>${instructions}</p>${offline ? `<code>http://localhost:11434</code>` : `<code>Current model: ${esc(details.model || "not selected")}</code>`}<p class="service-hint">Your complaint text is not lost. CitizenDesk will not pretend extraction succeeded while the local model is unavailable.</p><button class="button button-light button-small" data-nav="settings">Open Settings & models ${icon("arrow-up-right",12)}</button></div>`;
}

function navigate(view) {
  state.view = view;
  const title = { dashboard: "OVERVIEW", new: "NEW COMPLAINT", records: "CASE RECORDS", contacts: "CONTACT LIBRARY", detail: "CASE DETAIL", settings: "SETTINGS & MODELS" }[view] || "OVERVIEW";
  document.getElementById("page-crumb").textContent = title;
  document.querySelectorAll(".nav-link").forEach(el => el.classList.toggle("active", el.dataset.nav === view));
  document.querySelectorAll(".view").forEach(el => el.classList.toggle("view-active", el.dataset.view === view));
  if (view === "dashboard") renderDashboard();
  if (view === "new") renderNewComplaint();
  if (view === "records") renderRecords();
  if (view === "contacts") renderContacts();
  if (view === "detail") renderDetail();
  if (view === "settings") renderSettings();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function metricCard(label, value, foot, ico, accent = false) {
  return `<article class="metric-card ${accent ? "accent" : ""}"><div class="metric-top"><span>${label}</span><span class="metric-icon">${icon(ico, 14)}</span></div><div class="metric-value">${value}</div><div class="metric-foot">${foot}</div></article>`;
}
function recentRows(items) {
  if (!items.length) return `<tr><td colspan="4" class="empty-row">No saved complaints yet. Your first case will appear here.</td></tr>`;
  return items.map(item => {
    const status = getCaseStatus(item);
    return `<tr data-open="${esc(item.complaint_id)}"><td><div class="case-name"><span class="case-symbol">${icon("file",14)}</span><span><strong>${esc(getIssue(item))}</strong><small>${esc(String(item.complaint_id || "").slice(0,10).toUpperCase())}</small></span></div></td><td>${esc(item.facts?.city || item.facts?.country || "Location not recorded")}</td><td><span class="status-pill ${status.tone === "warning" ? "warning" : status.tone === "neutral" ? "neutral" : ""}">${status.label}</span></td><td>${shortDate(item.created_at)}</td></tr>`;
  }).join("");
}
function renderDashboard() {
  const d = state.dashboard || {};
  const items = state.complaints.slice(0, 5);
  const root = document.getElementById("view-dashboard");
  root.innerHTML = `
    <div class="page-intro">
      <div><div class="eyebrow"><span class="eyebrow-line"></span> YOUR CIVIC WORKSPACE / 01</div><h1>A clearer path from issue to action.</h1><p>Turn a real-world problem into a structured complaint, find the right public office, and prepare what to say next.</p></div>
      <div class="intro-aside"><span class="tiny-ring"></span>${state.apiOnline ? "LOCAL DATA CONNECTED" : "WAITING FOR LOCAL API"}</div>
    </div>
    <section class="hero-panel">
      <div class="hero-copy"><span class="hero-tag"><span></span> THE CITIZENDESK WORKFLOW</span><h2>Make the next step <em>clear.</em></h2><p>Describe what's happening. CitizenDesk organizes the details, researches a likely authority, assesses contact evidence, and prepares a practical complaint.</p><div class="hero-actions"><button class="button button-mint" data-action="start-complaint">Start a complaint ${icon("arrow-up-right",14)}</button><span class="hero-note">PRIVATE · LOCAL-FIRST · EVIDENCE-LED</span></div></div>
      <div class="hero-visual"><div class="hero-grid"></div><div class="hero-orbit"></div><svg class="hero-graphic" viewBox="0 0 320 220" fill="none" aria-hidden="true"><path d="M24 171 87 133l48 23 63-72 42 22 54-66" stroke="#BFE4D0" stroke-width="1.5" opacity=".8"/><path d="M24 191 87 153l48 23 63-72 42 22 54-66" stroke="#BFE4D0" stroke-width="1" opacity=".25"/><path d="M24 151 87 113l48 23 63-72 42 22 54-66" stroke="#BFE4D0" stroke-width="1" opacity=".25"/><g fill="#BFE4D0"><circle cx="87" cy="133" r="5"/><circle cx="135" cy="156" r="5"/><circle cx="198" cy="84" r="5"/><circle cx="240" cy="106" r="5"/><circle cx="294" cy="40" r="5"/></g><circle cx="198" cy="84" r="13" stroke="#BFE4D0" opacity=".3"/><path d="M198 71v26M185 84h26" stroke="#BFE4D0" opacity=".55"/><path d="M35 32h73M35 42h44M234 176h51M257 186h28" stroke="#BFE4D0" stroke-width="1" opacity=".3"/><rect x="49" y="61" width="54" height="37" rx="6" fill="#BFE4D0" fill-opacity=".1" stroke="#BFE4D0" stroke-opacity=".35"/><path d="M62 73h28M62 81h18M62 89h23" stroke="#BFE4D0" stroke-linecap="round" opacity=".7"/></svg><div class="hero-stamp"><span></span> EVERY CASE STARTS WITH A DETAIL</div></div>
    </section>
    <section class="metric-grid">
      ${metricCard("COMPLAINTS IN YOUR FILE", d.total_complaints ?? 0, "Saved to your local JSON record", "layers")}
      ${metricCard("REVIEWED DRAFTS", d.reviewed_complaints ?? 0, "Passed the current review checks", "filecheck", true)}
      ${metricCard("NEEDS ATTENTION", d.needs_attention ?? 0, "Cases that need another look", "alert")}
      ${metricCard("CONTACT CANDIDATES", d.contact_candidates ?? 0, "Collected research records", "contact")}
    </section>
    <section class="dashboard-grid">
      <article class="panel flow-panel"><div class="panel-head"><div><div class="panel-title">How a case moves</div><div class="panel-subtitle">A transparent path through the current workflow</div></div><span class="status-pill neutral">WORKFLOW</span></div><div class="flow-canvas"><div class="flow-line"><div class="flow-line-active"></div></div><div class="flow-steps"><div class="flow-step"><span class="flow-step-icon">${icon("file-plus")}</span><div><strong>Understand</strong><small>Extract details</small></div></div><div class="flow-step"><span class="flow-step-icon">${icon("building-2")}</span><div><strong>Identify</strong><small>Likely authority</small></div></div><div class="flow-step"><span class="flow-step-icon">${icon("searchcheck")}</span><div><strong>Research</strong><small>Assess contacts</small></div></div><div class="flow-step"><span class="flow-step-icon">${icon("filecheck")}</span><div><strong>Prepare</strong><small>Draft & review</small></div></div></div></div><div class="flow-caption"><span>Every stage leaves a trace in the case log.</span><b>NO BLACK BOX</b></div></article>
      <article class="panel pulse-panel"><div class="panel-head"><div><div class="panel-title">Workspace pulse</div><div class="panel-subtitle">Saved cases by activity</div></div><span class="metric-icon">${icon("activity",14)}</span></div><div class="pulse-body"><div class="pulse-graphic" aria-label="Recent activity visualization">${Array.from({length:10},(_,i)=>`<div class="pulse-bar-wrap"><span class="pulse-bar" style="--bar-height:${items.length ? [22,32,25,47,38,60,45,76,57,88][i] : [7,9,6,12,9,14,8,13,10,16][i]}%;animation-delay:${i*.035}s"></span></div>`).join("")}</div><div class="pulse-days"><span>01</span><span>05</span><span>10</span><span>15</span><span>20</span><span>NOW</span></div><div class="pulse-summary"><span>${items.length ? "Latest saved activity" : "No activity recorded yet"}</span><strong>${items.length ? shortDate(items[0].created_at) : "—"}</strong></div></div></article>
    </section>
    <section class="panel records-panel"><div class="panel-head"><div><div class="panel-title">Recent cases</div><div class="panel-subtitle">Your latest saved complaint records</div></div><button class="panel-action" data-nav="records">View all records ${icon("arrow-up-right",12)}</button></div><div class="table-wrap"><table><thead><tr><th>COMPLAINT</th><th>LOCATION</th><th>STATUS</th><th>CREATED</th></tr></thead><tbody>${recentRows(items)}</tbody></table></div></section>
  `;
}

function renderNewComplaint() {
  const root = document.getElementById("view-new");
  root.innerHTML = `
    <div class="page-intro"><div><div class="eyebrow"><span class="eyebrow-line"></span> START WITH WHAT YOU KNOW / 02</div><h1>Tell us what happened.</h1><p>Use your own words. You don't need to know which department is responsible — that's part of the research.</p></div><div class="intro-aside"><span class="tiny-ring"></span>STEP 01 / INTAKE</div></div>
    <div class="section-grid"><section class="panel form-panel"><h2 class="form-title">New complaint</h2><p class="form-copy">Include whatever you know about the issue, where it is happening, how long it has continued, and who is affected. You can write naturally; missing context can be added later.</p>
      ${ollamaNotice()}
      <form id="complaint-form"><div class="field"><label for="complaint-text">Describe the problem <small>REQUIRED</small></label><textarea id="complaint-text" name="complaint" required minlength="8" maxlength="12000" placeholder="For example: Stray dogs have been gathering near Street 5, Model Town, Lahore for the past two weeks. Residents are worried about children walking to school..."></textarea><div class="field-hint"><span>Write naturally in your language or mix languages. CitizenDesk detects the main language automatically.</span><span id="char-count">0 / 12,000</span></div></div>
      <div class="language-auto"><span class="language-auto-icon">Aa</span><span><strong>Automatic language detection</strong><small>CitizenDesk detects the language of your complaint and prepares the response in that language.</small></span><span class="status-pill neutral">AUTO</span></div>
      <div class="form-actions"><small>Your complaint is processed through your local workflow.</small><button class="button button-primary" type="submit">Analyze complaint ${icon("arrow-up-right",14)}</button></div></form>
    </section>
    <aside class="side-info"><article class="info-card tinted"><div class="eyebrow">A USEFUL STARTING POINT</div><h3>Specific details make better cases.</h3><p>You don't need formal language. A clear description gives the workflow something concrete to work with.</p><div class="checklist"><div class="check-row"><span class="check-circle">${icon("check",12)}</span><div><strong>What is happening?</strong><small>Describe the issue in simple terms.</small></div></div><div class="check-row"><span class="check-circle">${icon("check",12)}</span><div><strong>Where is it happening?</strong><small>City, neighbourhood, street or landmark.</small></div></div><div class="check-row"><span class="check-circle">${icon("check",12)}</span><div><strong>What is the impact?</strong><small>Explain how residents or services are affected.</small></div></div></div></article>
      <article class="info-card"><h3>What happens after submit?</h3><p>CitizenDesk follows the same predictable sequence every time. You can see each stage and its log as the workflow runs.</p><div class="stage-list"><div class="stage-row"><div class="stage-track"><span class="stage-dot"></span><span class="stage-stem"></span></div><div><strong>Understand the complaint</strong><small>Extract facts and ask for missing details.</small></div></div><div class="stage-row"><div class="stage-track"><span class="stage-dot"></span><span class="stage-stem"></span></div><div><strong>Research the right authority</strong><small>Search for relevant public contact channels.</small></div></div><div class="stage-row"><div class="stage-track"><span class="stage-dot"></span><span class="stage-stem"></span></div><div><strong>Prepare your next step</strong><small>Generate, review and save draft material.</small></div></div></div></article>
    </aside></div><div id="run-area"></div>
  `;
  const textarea = document.getElementById("complaint-text");
  textarea?.addEventListener("input", () => { document.getElementById("char-count").textContent = `${textarea.value.length.toLocaleString()} / 12,000`; });
  document.getElementById("complaint-form")?.addEventListener("submit", event => {
    event.preventDefault();
    const text = textarea.value.trim();
    if (text.length < 8) return toast("Please add a little more detail before submitting.", "error");
    if (!state.modelReady) return toast("Ollama is not ready. Follow the service notice above, then refresh.", "error");
    state.pendingComplaint = { complaint: text, language: "auto", complaint_id: (crypto.randomUUID ? crypto.randomUUID().replaceAll("-", "") : `cd-${Date.now()}`) };
    runWorkflow({ ...state.pendingComplaint, answers: {} });
  });
}

function deriveStageFlags(s) {
  const logs = (s.log || []).join(" ").toLowerCase();
  const flags = [
    !!(s.facts && Object.keys(s.facts).length) || logs.includes("intake started"),
    !!s.authority || logs.includes("authority identification started"),
    Number(s.attempt || 0) > 0 || logs.includes("research round"),
    (s.channels || []).some(c => c.verification_status) || logs.includes("verifier started"),
    (s.draft || []).length > 0 || logs.includes("writer started"),
    !!(s.review && Object.keys(s.review).length) || logs.includes("reviewer"),
  ];
  return flags;
}
function progressIndex(s) {
  const flags = deriveStageFlags(s);
  let current = 0;
  for (let i = 0; i < flags.length; i++) if (flags[i]) current = i;
  if (s.saved_file || s.status === "saved") return 6;
  return current;
}
function renderWorkflow(snapshot = {}, running = false) {
  const area = document.getElementById("run-area");
  if (!area) return;
  const flags = deriveStageFlags(snapshot);
  const current = progressIndex(snapshot);
  const steps = ["Intake", "Authority", "Research", "Verification", "Drafting", "Review"];
  const icons = ["file", "building-2", "search", "shield-check", "mail", "list-checks"];
  const progressMarkup = steps.map((label,i) => `<div class="workflow-step ${flags[i] ? "done" : ""} ${running && current === i && !flags[i] ? "current" : ""}"><span class="step-icon">${flags[i] ? icon("check",15) : icon(icons[i],15)}</span><strong>${label}</strong></div>`).join("");
  const log = (snapshot.log || []).slice(-12);
  const logsMarkup = log.length ? log.map(line => `<div class="log-line ${/failed|error|stopped/i.test(line) ? "error" : ""}"><span class="log-bullet"></span><span>${esc(line)}</span></div>`).join("") : `<div class="log-line"><span class="log-bullet"></span><span>Waiting for the first workflow update…</span></div>`;
  area.innerHTML = `<section class="workflow-panel"><div class="workflow-head"><div><h3>${running ? "Your case is moving through the workflow" : "Workflow summary"}</h3><p>${running ? "These updates come from actual LangGraph state changes." : "The workflow has returned its latest state."}</p></div>${running ? '<span class="status-pill"><span class="spinner"></span> RUNNING</span>' : `<span class="status-pill ${["needs_info", "manual_review", "service_unavailable", "extraction_failed"].includes(snapshot.status) ? "warning" : "neutral"}">${esc(String(snapshot.status || "Complete").replaceAll("_"," ").toUpperCase())}</span>`}</div><div class="workflow-steps">${progressMarkup}</div><div class="workflow-log">${logsMarkup}</div></section>`;
  if (!running && snapshot.status === "needs_info" && snapshot.error_message) {
    area.insertAdjacentHTML("beforeend", `<div class="service-notice"><strong>Intake needs another pass.</strong><p>${esc(snapshot.error_message)}</p></div>`);
  }
  if (!running && ["service_unavailable", "extraction_failed"].includes(snapshot.status)) {
    const title = snapshot.status === "service_unavailable" ? "Local model service unavailable" : "Could not extract complaint details";
    area.insertAdjacentHTML("beforeend", `<section class="service-notice danger"><strong>${title}</strong><p>${esc(snapshot.error_message || "Check the local model configuration and retry.")}</p><button class="button button-light button-small" data-action="retry-health">Check connection again</button></section>`);
  } else if (!running && snapshot.status === "needs_info" && Array.isArray(snapshot.questions) && snapshot.questions.length) renderQuestions(snapshot);
  else if (!running && (snapshot.draft?.length || snapshot.channels?.length || snapshot.authority)) renderResults(snapshot);
  else if (!running && snapshot.status === "manual_review") toast("The automatic revision limit was reached. Human review is needed.", "error");
}
function renderQuestions(snapshot) {
  const area = document.getElementById("run-area");
  if (!area) return;
  const missing = Array.isArray(snapshot.missing) ? snapshot.missing : [];
  const labels = {
    issue: "what the problem is", country: "which country it is in", city: "which city or town",
    location: "the specific area, street, or landmark", duration: "how long it has been happening",
    impact: "who is affected and how",
  };
  const readable = missing.map(field => labels[field] || field.replaceAll("_", " ")).filter(Boolean);
  const missingText = readable.length ? readable.join(", ") : "a little more context";
  const questionText = snapshot.questions?.[0]?.question || `Could you add a little more context about ${missingText}? You can answer naturally in one message.`;
  area.insertAdjacentHTML("beforeend", `<section class="question-panel"><div class="eyebrow"><span class="eyebrow-line"></span> ONE MORE DETAIL / INTAKE</div><h3>One quick clarification.</h3><p>${esc(questionText)} Your answer is combined with the original complaint and re-read by the model; it is not copied blindly into a field.</p><form id="answers-form"><div class="field"><label for="clarification-text">Add or clarify details</label><textarea id="clarification-text" name="clarification" rows="4" placeholder="Write naturally. You can include the city, area, duration, who is affected, or correct a detail from the first description..."></textarea></div><div class="form-actions"><small>One message is enough; the model will extract every supported fact again.</small><button class="button button-primary" type="submit">Re-analyze details ${icon("arrow",14)}</button></div></form></section>`);
  document.getElementById("answers-form")?.addEventListener("submit", event => {
    event.preventDefault();
    const clarification = document.getElementById("clarification-text")?.value.trim();
    if (!clarification) return toast("Add the missing context in your own words.", "error");
    if (!state.pendingComplaint) return toast("The original complaint is no longer available. Start a new one.", "error");
    runWorkflow({ ...state.pendingComplaint, answers: { clarification } });
  });
}

async function runWorkflow(payload) {
  if (!state.apiOnline) return toast("Start the CitizenDesk API first, then refresh this page.", "error");
  if (!state.modelReady) {
    const runArea = document.getElementById("run-area");
    if (runArea) runArea.innerHTML = ollamaNotice();
    return toast("Ollama is unavailable. Start the local service and refresh CitizenDesk.", "error");
  }
  if (state.activeRun) return;
  state.activeRun = true;
  const runArea = document.getElementById("run-area");
  if (runArea) runArea.innerHTML = `<section class="workflow-panel"><div class="workflow-head"><div><h3>Preparing your complaint</h3><p>Connecting to the local LangGraph workflow…</p></div><span class="status-pill"><span class="spinner"></span> STARTING</span></div></section>`;
  try {
    const response = await fetch("/api/complaints/run", { method: "POST", headers: { "Content-Type": "application/json", "Accept": "text/event-stream" }, body: JSON.stringify(payload) });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `Workflow request failed (${response.status})`);
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let lastSnapshot = {};
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let cut;
      while ((cut = buffer.indexOf("\n\n")) !== -1) {
        const block = buffer.slice(0, cut);
        buffer = buffer.slice(cut + 2);
        const dataLine = block.split("\n").find(line => line.startsWith("data:"));
        if (!dataLine) continue;
        const event = JSON.parse(dataLine.slice(5).trim());
        if (event.type === "snapshot" || event.type === "complete") {
          lastSnapshot = event.state || lastSnapshot;
          renderWorkflow(lastSnapshot, event.type !== "complete");
        } else if (event.type === "error") {
          lastSnapshot = event.state || lastSnapshot;
          renderWorkflow(lastSnapshot, false);
          toast(event.message || "The workflow encountered an error.", "error");
        }
      }
    }
    state.activeCase = lastSnapshot;
    if (lastSnapshot.status === "saved" || lastSnapshot.saved_file) {
      toast("Complaint saved to your local records.");
      await loadData();
    } else if (lastSnapshot.status === "needs_info") {
      toast("CitizenDesk needs a few more details.");
    } else if (lastSnapshot.status === "manual_review") {
      toast("A human review is needed before finalizing this case.", "error");
    } else if (lastSnapshot.status === "save_failed") {
      toast("The complaint could not be saved. Check the server log.", "error");
    } else if (lastSnapshot.status === "service_unavailable" || lastSnapshot.status === "extraction_failed") {
      toast(lastSnapshot.error_message || "Intake could not run. Check Ollama and retry.", "error");
    }
  } catch (error) {
    toast(error.message || "Could not reach CitizenDesk.", "error");
    if (runArea) runArea.insertAdjacentHTML("beforeend", `<div class="question-panel"><h3>We couldn't run the workflow.</h3><p>${esc(error.message)}. Check that FastAPI and Ollama are running, then try again.</p></div>`);
  } finally {
    state.activeRun = false;
  }
}

function renderResults(snapshot) {
  const area = document.getElementById("run-area");
  if (!area) return;
  const channels = snapshot.channels || [];
  const drafts = snapshot.draft || [];
  const review = snapshot.review || {};
  state.currentDraft = drafts.length ? Math.min(state.currentDraft, drafts.length - 1) : 0;
  const score = Math.round((Number(review.score) || 0) * 100);
  const authority = snapshot.authority || "No authority candidate was returned.";
  const channelMarkup = channels.length ? channels.map(channel => {
    const type = String(channel.type || "contact").toLowerCase();
    const ico = type.includes("email") ? "mail" : type.includes("phone") ? "phone" : "globe";
    const status = channel.verification_status || "not assessed";
    const scoreText = channel.verification_score != null ? `${Math.round(channel.verification_score*100)}%` : "—";
    const source = channel.source_url || channel.url || "";
    return `<div class="channel-item"><span class="channel-icon">${icon(ico,14)}</span><div><strong>${esc(channel.value || "Unspecified contact")}</strong><small>${esc(type)} · ${esc(status.replaceAll("_"," "))} · ${channel.live_contact_tested ? "live tested" : "not live-tested"}</small>${source ? `<a class="source-link" href="${esc(source)}" target="_blank" rel="noopener">View source ${icon("external-link",10)}</a>` : ""}</div><span class="channel-score">${scoreText}</span></div>`;
  }).join("") : `<p>No contact candidates were returned by this research run.</p>`;
  const draftTabs = drafts.map((draft,i) => `<button class="draft-tab ${i === state.currentDraft ? "active" : ""}" data-draft="${i}">${esc(draft.format || `Draft ${i+1}`).toUpperCase()}</button>`).join("");
  const selected = drafts[state.currentDraft] || drafts[0];
  area.insertAdjacentHTML("beforeend", `<div class="result-grid"><section class="result-card"><h3>Research outcome</h3><p>Authority and contact candidates returned by the workflow. A passed heuristic is not proof that a contact is currently active.</p><div class="authority-name">${esc(authority)}</div><div class="channel-list" style="margin-top:13px">${channelMarkup}</div></section><section class="result-card"><h3>Review outcome</h3><p>Automated checks applied to the generated drafts.</p><div class="review-score"><div class="score-ring" style="--score:${score*3.6}deg"><strong>${score}%</strong></div><div class="review-score-copy"><strong>${review.passed ? "Review checks passed" : "Review needs attention"}</strong><small>${(review.failed || []).length} check(s) need attention · ${drafts.length} draft(s)</small></div></div><div class="review-checks">${(review.failed || []).slice(0,6).map(item => `<div class="review-check fail"><span class="checkmark">!</span><span>${esc(item)}</span></div>`).join("") || `<div class="review-check"><span class="checkmark">✓</span><span>No failed checks were recorded.</span></div>`}</div></section></div><section class="result-card" style="margin-top:14px"><div class="panel-head" style="padding:0"><div><h3>Prepared complaint material</h3><p style="margin:4px 0 0">Review and copy the draft before sending it.</p></div><button class="button button-light button-small" data-action="copy-draft">${icon("copy",12)} Copy draft</button></div><div class="draft-tabs">${draftTabs || '<span class="draft-tab active">NO DRAFTS</span>'}</div><div class="draft-content" id="draft-content">${esc(selected?.text || "No draft was generated. Review the workflow log for details.")}</div></section>`);
  area.querySelectorAll("[data-draft]").forEach(button => button.addEventListener("click", () => {
    state.currentDraft = Number(button.dataset.draft);
    area.querySelectorAll("[data-draft]").forEach(item => item.classList.toggle("active", item === button));
    document.getElementById("draft-content").textContent = drafts[state.currentDraft]?.text || "";
  }));
  area.querySelector("[data-action='copy-draft']")?.addEventListener("click", () => {
    const text = drafts[state.currentDraft]?.text || drafts[0]?.text || "";
    if (!text) return toast("There is no draft to copy.", "error");
    navigator.clipboard?.writeText(text).then(() => toast("Draft copied to clipboard.")).catch(() => toast("Clipboard access was blocked by the browser.", "error"));
  });
}

function renderRecords() {
  const root = document.getElementById("view-records");
  const filtered = state.complaints.filter(item => {
    const status = getCaseStatus(item);
    const matchesStatus = state.recordFilter === "all" || (state.recordFilter === "attention" ? status.tone === "warning" : state.recordFilter === "reviewed" ? status.tone === "good" : status.tone === "neutral");
    const haystack = `${getIssue(item)} ${item.facts?.city || ""} ${item.complaint_id || ""}`.toLowerCase();
    return matchesStatus && haystack.includes(state.recordSearch.toLowerCase());
  });
  root.innerHTML = `<div class="page-intro"><div><div class="eyebrow"><span class="eyebrow-line"></span> YOUR LOCAL RECORD / 03</div><h1>Case records.</h1><p>Every saved complaint, with its extracted details, research findings, generated drafts and review outcome.</p></div><button class="button button-primary" data-action="start-complaint">New complaint ${icon("plus",14)}</button></div><div class="toolbar-row"><label class="search-box">${icon("search",15)}<input id="record-search" type="search" placeholder="Search issue, city or case ID…" value="${esc(state.recordSearch)}"></label><select class="filter-select" id="record-filter"><option value="all" ${state.recordFilter === "all" ? "selected" : ""}>All records</option><option value="reviewed" ${state.recordFilter === "reviewed" ? "selected" : ""}>Reviewed</option><option value="attention" ${state.recordFilter === "attention" ? "selected" : ""}>Needs attention</option><option value="saved" ${state.recordFilter === "saved" ? "selected" : ""}>Saved</option></select></div><section class="panel records-panel"><div class="panel-head"><div><div class="panel-title">All complaint records</div><div class="panel-subtitle">${filtered.length} record(s) shown · Stored locally as JSON</div></div><span class="status-pill neutral">${state.complaints.length} TOTAL</span></div><div class="table-wrap"><table><thead><tr><th>COMPLAINT</th><th>LOCATION</th><th>AUTHORITY</th><th>STATUS</th><th>CREATED</th></tr></thead><tbody>${filtered.length ? filtered.map(item => { const status=getCaseStatus(item); return `<tr data-open="${esc(item.complaint_id)}"><td><div class="case-name"><span class="case-symbol">${icon("file",14)}</span><span><strong>${esc(getIssue(item))}</strong><small>${esc(String(item.complaint_id||"").slice(0,10).toUpperCase())}</small></span></div></td><td>${esc(item.facts?.city || "—")}</td><td>${esc(item.authority || "Not identified")}</td><td><span class="status-pill ${status.tone === "warning" ? "warning" : status.tone === "neutral" ? "neutral" : ""}">${status.label}</span></td><td>${shortDate(item.created_at)}</td></tr>`; }).join("") : `<tr><td colspan="5" class="empty-row">No records match this view.</td></tr>`}</tbody></table></div></section>`;
  document.getElementById("record-search")?.addEventListener("input", e => { state.recordSearch = e.target.value; const pos=e.target.selectionStart; renderRecords(); const input=document.getElementById("record-search"); input.focus(); input.setSelectionRange(pos,pos); });
  document.getElementById("record-filter")?.addEventListener("change", e => { state.recordFilter = e.target.value; renderRecords(); });
}

function renderContacts() {
  const root = document.getElementById("view-contacts");
  state.selectedContactIds = state.selectedContactIds || new Set();
  const cards = state.contacts.map(contact => {
    const source = contact.source_url || contact.url || "";
    const type = String(contact.type || "contact");
    const ico = type.includes("email") ? "mail" : type.includes("phone") ? "phone" : "globe";
    const id = contact.contact_id || "";
    const checked = state.selectedContactIds.has(id) ? "checked" : "";
    return `<article class="contact-card" data-search="${esc(`${contact.value||""} ${source} ${type}`.toLowerCase())}"><div class="contact-card-top"><label class="contact-select-label"><input class="contact-select" type="checkbox" value="${esc(id)}" ${checked} aria-label="Select ${esc(contact.value || "contact")}"><span class="contact-type">${icon(ico,13)} ${esc(type)}</span></label><span class="status-pill neutral">CANDIDATE</span></div><h3>${esc(contact.value || "No value recorded")}</h3><p>${esc(contact.evidence || "No additional evidence text stored.")}</p><div class="contact-card-foot"><span>${esc(contact.source_title || "Research source")}</span>${source ? `<a href="${esc(source)}" target="_blank" rel="noopener">Open source ${icon("external-link",10)}</a>` : "<span>No source URL</span>"}</div></article>`;
  }).join("");
  const selectedCount = state.selectedContactIds.size;
  root.innerHTML = `<div class="page-intro"><div><div class="eyebrow"><span class="eyebrow-line"></span> RESEARCH MEMORY / 04</div><h1>Contact library.</h1><p>Contact candidates collected from research runs. Each record keeps its source so you can inspect the evidence yourself.</p></div><div class="intro-aside"><span class="tiny-ring"></span>${state.contacts.length} STORED CANDIDATES</div></div><div class="toolbar-row contacts-toolbar"><label class="search-box">${icon("search",15)}<input id="contact-search" type="search" placeholder="Search contacts or source domains…" value="${esc(state.contactSearch)}"></label><label class="select-all-label"><input id="select-all-contacts" type="checkbox" ${state.contacts.length && selectedCount === state.contacts.length ? "checked" : ""}> Select all</label><button class="button button-light button-small" id="delete-selected" data-action="delete-selected" ${selectedCount ? "" : "disabled"}>${icon("trash",13)} Delete selected (${selectedCount})</button><button class="button button-danger button-small" data-action="delete-all" ${state.contacts.length ? "" : "disabled"}>Delete all</button></div><div class="contacts-grid" id="contacts-grid">${state.contacts.length ? cards : `<div class="panel" style="grid-column:1/-1"><div class="empty-state"><div class="empty-illustration">${icon("contact",26)}</div><h3>No contact candidates yet</h3><p>When a research run finds contact details, CitizenDesk stores the candidates here with their source URLs.</p><button class="button button-primary" data-action="start-complaint">Start a complaint ${icon("arrow",13)}</button></div></div>`}</div><p class="contact-retention-note">Deleting contacts removes them from the reusable contact library only. Copies already saved inside historical complaint records are retained.</p><p style="margin:14px 2px;color:#9aa49d;font-size:9px;line-height:1.6">Important: candidates in this library are not necessarily verified or live-tested. Verification is a preliminary evidence check, not confirmation that an office will respond.</p>`;
  document.getElementById("contact-search")?.addEventListener("input", e => { state.contactSearch = e.target.value; const term=e.target.value.toLowerCase(); document.querySelectorAll(".contact-card").forEach(card => { card.style.display=card.dataset.search.includes(term)?"":"none"; }); });
  document.querySelectorAll(".contact-select").forEach(input => input.addEventListener("change", () => {
    if (input.checked) state.selectedContactIds.add(input.value); else state.selectedContactIds.delete(input.value);
    renderContacts();
  }));
  document.getElementById("select-all-contacts")?.addEventListener("change", event => {
    state.selectedContactIds = event.target.checked ? new Set(state.contacts.map(item => item.contact_id).filter(Boolean)) : new Set();
    renderContacts();
  });
}

async function deleteSelectedContacts() {
  const ids = [...state.selectedContactIds];
  if (!ids.length) return;
  const confirmed = window.confirm(`Delete ${ids.length} selected contact candidate(s) from the reusable contact library? Historical complaint records will not be changed.`);
  if (!confirmed) return;
  try {
    const response = await fetch("/api/contacts/delete", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ contact_ids: ids }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Delete failed (${response.status})`);
    state.selectedContactIds.clear();
    await loadData();
    renderContacts();
    toast(`${data.deleted} contact(s) deleted.`);
  } catch (error) { toast(error.message || "Could not delete selected contacts.", "error"); }
}

function openDeleteAllContactsDialog() {
  showModal("Delete the entire contact library?", `<div class="delete-warning"><strong>This action cannot be undone.</strong><p>All ${state.contacts.length} reusable contact candidates will be removed from <code>data/contacts.json</code>. Historical complaint records remain unchanged.</p><p>To confirm, type <b>DELETE ALL CONTACTS</b> exactly.</p><input id="delete-all-confirmation" class="confirm-input" type="text" autocomplete="off" placeholder="DELETE ALL CONTACTS"><button class="button button-danger" data-action="confirm-delete-all">${icon("trash",13)} Permanently delete all contacts</button></div>`);
}

async function deleteAllContacts() {
  const phrase = document.getElementById("delete-all-confirmation")?.value.trim();
  if (phrase !== "DELETE ALL CONTACTS") return toast("The confirmation phrase does not match.", "error");
  try {
    const response = await fetch("/api/contacts", { method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ confirmation: phrase }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Delete failed (${response.status})`);
    state.selectedContactIds.clear();
    closeModal();
    await loadData();
    renderContacts();
    toast(`${data.deleted} contact(s) deleted. Contact library is now empty.`);
  } catch (error) { toast(error.message || "Could not clear the contact library.", "error"); }
}

function formatBytes(bytes) {
  const value = Number(bytes) || 0;
  if (value < 1024) return `${value} B`;
  if (value < 1024 ** 2) return `${(value / 1024).toFixed(1)} KB`;
  if (value < 1024 ** 3) return `${(value / 1024 ** 2).toFixed(2)} MB`;
  return `${(value / 1024 ** 3).toFixed(2)} GB`;
}

function renderSettings() {
  const root = document.getElementById("view-settings");
  const models = state.installedModels || [];
  const selected = state.currentModel || "";
  const modelOptions = models.map(model => {
    const name = model.name || "";
    const meta = [model.parameter_size, model.quantization_level, model.size ? formatBytes(model.size) : ""].filter(Boolean).join(" · ");
    return `<option value="${esc(name)}" ${name === selected ? "selected" : ""}>${esc(name)}${meta ? ` — ${esc(meta)}` : ""}</option>`;
  }).join("");
  const fileRows = state.ggufFiles.length ? state.ggufFiles.map((file, index) => {
    const defaultName = `citizendesk-${String(file.name || "local-model").replace(/\.gguf$/i, "").toLowerCase().replace(/[^a-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 48) || `local-${index + 1}`}`;
    return `<article class="model-file-row"><div class="model-file-icon">${icon("harddrive",17)}</div><div class="model-file-copy"><strong>${esc(file.name)}</strong><small>${esc(formatBytes(file.size))} · ${esc(file.path)}</small><label class="model-name-field">Ollama name <input type="text" value="${esc(defaultName)}" maxlength="64" data-gguf-name></label></div><button class="button button-light button-small" data-import-gguf="${esc(file.path)}">Import & use</button></article>`;
  }).join("") : `<div class="model-empty">${icon("folder",18)}<span>No standalone GGUF files scanned yet.</span></div>`;

  root.innerHTML = `
    <div class="page-intro"><div><div class="eyebrow"><span class="eyebrow-line"></span> LOCAL RUNTIME / 05</div><h1>Settings & models.</h1><p>Choose which local model CitizenDesk uses. Installed Ollama models are detected automatically; standalone GGUF files can be scanned and imported.</p></div><div class="intro-aside"><span class="tiny-ring"></span>LOCAL CONFIGURATION</div></div>
    <section class="settings-grid">
      <article class="panel settings-panel">
        <div class="panel-head settings-panel-head"><div><div class="panel-title">Active language model</div><div class="panel-subtitle">Used for intake extraction, drafting, and structured responses.</div></div><span class="status-pill ${state.ollamaOnline ? "" : "warning"}">${state.ollamaOnline ? "OLLAMA ONLINE" : "OLLAMA OFFLINE"}</span></div>
        <div class="settings-current"><div class="settings-model-mark">${icon("cpu",21)}</div><div><small>CURRENT MODEL</small><strong>${esc(selected || "Not selected")}</strong><span>${state.modelReady ? "Installed and ready to use" : (state.ollamaOnline ? "Not found in installed models" : "Ollama service is not reachable")}</span></div></div>
        <div class="settings-field"><label for="installed-model-select">Choose an installed model</label><select id="installed-model-select" class="settings-select" ${models.length ? "" : "disabled"}>${modelOptions || `<option value="">No Ollama models detected</option>`}</select><small>Models are read live from Ollama's local <code>/api/tags</code> endpoint. This list does not download or load them.</small></div>
        <div class="settings-actions"><button class="button button-primary" id="save-model-selection" ${models.length ? "" : "disabled"}>Save selected model ${icon("check",13)}</button><button class="button button-light button-small" id="refresh-models">Refresh model list ${icon("refresh-cw",12)}</button></div>
        ${!state.ollamaOnline ? `<div class="settings-help danger-help"><strong>Ollama connection problem</strong><p>${esc(state.ollamaStatus?.error || "Ollama is not reachable at localhost:11434.")}</p><p>Open the Ollama desktop app. If you run <code>ollama serve</code> and it reports that port 11434 is already in use, Ollama is already running; do not launch a second server.</p></div>` : ""}
      </article>
      <article class="panel settings-panel">
        <div class="panel-head settings-panel-head"><div><div class="panel-title">Find local GGUF files</div><div class="panel-subtitle">Browse a model folder on this computer and inspect model files.</div></div><span class="metric-icon">${icon("folder",14)}</span></div>
        <div class="settings-field"><label for="model-directory">Model folder</label><div class="path-picker"><input id="model-directory" type="text" value="${esc(state.modelDirectory)}" placeholder="D:\\Downloaded-GGUF-Models"><button class="button button-light button-small" id="browse-model-directory">Browse folder</button></div><small>Scan a folder containing downloaded <code>.gguf</code> files. Ollama’s own model store is detected automatically above; do not scan its internal blob folder.</small></div>
        <div class="settings-actions"><button class="button button-primary" id="scan-model-directory">Scan for GGUF files ${icon("search",13)}</button></div>
        <div class="model-file-list">${fileRows}</div>
        <div class="settings-help"><strong>How model files work</strong><p>Ollama-managed models are detected automatically above. A loose <code>.gguf</code> file must first be registered with Ollama; use <b>Import & use</b> to create it. A large model may not fit your available RAM, even if import succeeds.</p></div>
      </article>
    </section>
    <section class="settings-footnote"><strong>Local model tip</strong><span>Start with a small quantized model on an 8 GB machine. Selecting a model changes CitizenDesk's <code>MODEL_NAME</code> in your project <code>.env</code>; it does not download a model or start Ollama for you.</span></section>
  `;

  document.getElementById("save-model-selection")?.addEventListener("click", saveModelSelection);
  document.getElementById("refresh-models")?.addEventListener("click", async () => { await loadData(); renderSettings(); toast("Installed model list refreshed."); });
  document.getElementById("browse-model-directory")?.addEventListener("click", browseModelDirectory);
  document.getElementById("scan-model-directory")?.addEventListener("click", scanModelDirectory);
  root.querySelectorAll("[data-import-gguf]").forEach(button => button.addEventListener("click", () => importGGUF(button)));
}

async function saveModelSelection() {
  const modelName = document.getElementById("installed-model-select")?.value;
  if (!modelName) return toast("Select an installed model first.", "error");
  try {
    const response = await fetch("/api/settings/model", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ model_name: modelName }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Could not select model (${response.status})`);
    await loadData();
    renderSettings();
    toast(`CitizenDesk will now use ${data.selected_model}.`);
  } catch (error) { toast(error.message || "Could not save model selection.", "error"); }
}

async function browseModelDirectory() {
  try {
    const response = await fetch("/api/settings/browse-directory", { method: "POST" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Could not open the folder picker.");
    if (data.path) {
      state.modelDirectory = data.path;
      document.getElementById("model-directory").value = data.path;
    }
  } catch (error) { toast(error.message || "Folder browsing failed. Enter the folder path manually.", "error"); }
}

async function scanModelDirectory() {
  const path = document.getElementById("model-directory")?.value.trim();
  if (!path) return toast("Choose or enter a model folder first.", "error");
  state.modelDirectory = path;
  const button = document.getElementById("scan-model-directory");
  if (button) { button.disabled = true; button.textContent = "Scanning folder…"; }
  try {
    const response = await fetch("/api/settings/scan-directory", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Folder scan failed (${response.status})`);
    state.ggufFiles = data.items || [];
    renderSettings();
    toast(`${data.count} GGUF file(s) found.`);
  } catch (error) {
    toast(error.message || "Could not scan that folder.", "error");
    if (button) { button.disabled = false; button.textContent = "Scan for GGUF files"; }
  }
}

async function importGGUF(button) {
  const row = button.closest(".model-file-row");
  const name = row?.querySelector("[data-gguf-name]")?.value.trim();
  if (!name) return toast("Enter a short Ollama model name first.", "error");
  const confirmed = window.confirm(`Import this local GGUF file into Ollama as '${name}' and make it CitizenDesk's active model? This can take time and the model may require more RAM than your computer has.`);
  if (!confirmed) return;
  button.disabled = true;
  button.textContent = "Importing…";
  try {
    const response = await fetch("/api/settings/import-gguf", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ file_path: button.dataset.importGguf, model_name: name }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Model import failed (${response.status})`);
    await loadData();
    renderSettings();
    toast(`Imported and selected ${data.selected_model}. Test it before using a full complaint.`);
  } catch (error) {
    button.disabled = false;
    button.textContent = "Import & use";
    toast(error.message || "Could not import this GGUF model.", "error");
  }
}

function renderDetail() {
  const root = document.getElementById("view-detail");
  const item = state.activeCase;
  if (!item) { root.innerHTML = `<button class="detail-back" data-nav="records">${icon("chevron-left",14)} Back to records</button><div class="panel empty-state"><h3>No case selected</h3><p>Choose a saved record to see its details.</p></div>`; return; }
  const facts = item.facts || {};
  const drafts = item.drafts || item.draft || [];
  const review = item.review || {};
  const score = Math.round((Number(review.score)||0)*100);
  root.innerHTML = `<button class="detail-back" data-nav="records">${icon("chevron-left",14)} Back to records</button><div class="detail-heading"><div><div class="eyebrow"><span class="eyebrow-line"></span> CASE FILE / ${esc(String(item.complaint_id||"").slice(0,8).toUpperCase())}</div><h1>${esc(getIssue(item))}</h1><p>${esc(facts.city || "Location not recorded")}${facts.country ? `, ${esc(facts.country)}` : ""} · Saved ${shortDate(item.created_at)}</p></div><span class="status-pill ${getCaseStatus(item).tone === "warning" ? "warning" : ""}">${getCaseStatus(item).label}</span></div><div class="detail-facts">${[ ["CITY",facts.city], ["LOCATION",facts.location], ["DURATION",facts.duration], ["CATEGORY",facts.category], ["IMPACT",facts.impact], ["AUTHORITY",item.authority] ].map(([k,v])=>`<div class="fact-tile"><small>${k}</small><strong>${esc(v || "Not recorded")}</strong></div>`).join("")}</div><div class="result-grid"><section class="result-card"><h3>Contact candidates</h3><p>Research channels stored with this case.</p><div class="channel-list">${(item.channels || []).map(c=>`<div class="channel-item"><span class="channel-icon">${icon(c.type === "email" ? "mail" : c.type === "phone" ? "phone" : "globe",14)}</span><div><strong>${esc(c.value)}</strong><small>${esc(c.verification_status || "not assessed")}</small>${c.source_url ? `<a class="source-link" href="${esc(c.source_url)}" target="_blank" rel="noopener">Open source</a>` : ""}</div><span class="channel-score">${c.verification_score != null ? Math.round(c.verification_score*100)+"%" : "—"}</span></div>`).join("") || "<p>No contact candidates stored with this case.</p>"}</div></section><section class="result-card"><h3>Draft review</h3><p>Automated quality checks returned by the reviewer.</p><div class="review-score"><div class="score-ring" style="--score:${score*3.6}deg"><strong>${score}%</strong></div><div class="review-score-copy"><strong>${review.passed ? "Checks passed" : "Review needs attention"}</strong><small>${(review.failed||[]).length} failed check(s)</small></div></div>${(review.failed||[]).map(f=>`<div class="review-check fail"><span class="checkmark">!</span><span>${esc(f)}</span></div>`).join("")}</section></div><section class="result-card" style="margin-top:14px"><h3>Saved drafts</h3><p>Review before sending. CitizenDesk prepares material; it does not submit complaints on your behalf.</p>${drafts.map(d=>`<div style="margin-top:12px"><div class="contact-type">${esc(String(d.format||"draft").toUpperCase())}</div><pre class="draft-content">${esc(d.text||"")}</pre><button class="button button-light button-small" data-copy-text="${encodeURIComponent(d.text||"")}">${icon("copy",12)} Copy</button></div>`).join("") || "<p>No drafts saved.</p>"}</section>`;
}

async function openCase(id) {
  const local = state.complaints.find(item => String(item.complaint_id) === String(id));
  if (local) state.activeCase = local;
  try { state.activeCase = await apiGet(`/api/complaints/${encodeURIComponent(id)}`); } catch { /* Keep the item already loaded in the list. */ }
  navigate("detail");
}
function showModal(title, body) {
  document.getElementById("modal-content").innerHTML = `<div class="eyebrow"><span class="eyebrow-line"></span> CITIZENDESK / HELP</div><h2 id="modal-title" style="margin:10px 0 8px;font:700 21px var(--display)">${esc(title)}</h2><div style="color:#78867c;font-size:11px;line-height:1.75">${body}</div>`;
  document.getElementById("modal-backdrop").hidden = false;
}
function closeModal() { document.getElementById("modal-backdrop").hidden = true; }

// Delegated interactions keep the interface small and dependency-free.
document.addEventListener("click", event => {
  const nav = event.target.closest("[data-nav]");
  if (nav) { event.preventDefault(); navigate(nav.dataset.nav); return; }
  const row = event.target.closest("tr[data-open]");
  if (row) { openCase(row.dataset.open); return; }
  const copy = event.target.closest("[data-copy-text]");
  if (copy) { navigator.clipboard?.writeText(decodeURIComponent(copy.dataset.copyText)).then(()=>toast("Draft copied.")); return; }
  const action = event.target.closest("[data-action]")?.dataset.action;
  if (!action) return;
  if (action === "start-complaint") navigate("new");
  if (action === "refresh") { loadData().then(()=>{ navigate(state.view); toast("Workspace data refreshed."); }); }
  if (action === "retry-health") { loadData().then(()=>{ navigate(state.view); toast(state.modelReady ? "Ollama and the configured model are ready." : "Ollama is still unavailable. Check the service notice.", state.modelReady ? "success" : "error"); }); }
  if (action === "delete-selected") deleteSelectedContacts();
  if (action === "delete-all") openDeleteAllContactsDialog();
  if (action === "confirm-delete-all") deleteAllContacts();
  if (action === "help") showModal("A little guidance", "<p><b>Start with what you know.</b> Describe the issue and the place where it is happening. CitizenDesk will extract the details and ask for anything important that is missing.</p><p><b>Check the sources.</b> Contact candidates keep their source URLs. Verification is a preliminary evidence check — it does not test whether a phone line or email is currently active.</p><p><b>Review before sending.</b> Generated drafts are suggestions for you to review and submit yourself.</p>");
  if (action === "workspace-info") showModal("Private workspace", "<p>This interface runs from the local CitizenDesk FastAPI service. Complaints and contact candidates are stored in the project's JSON files.</p><p>The model and web-research services need to be available for the full workflow. The dashboard remains local and does not submit complaints to government offices.</p>");
  if (action === "close-modal") closeModal();
});
document.getElementById("modal-backdrop").addEventListener("click", e => { if (e.target.id === "modal-backdrop") closeModal(); });

function setDateLabel() {
  const now = new Date();
  document.getElementById("today-label").textContent = new Intl.DateTimeFormat(undefined,{weekday:"short",day:"2-digit",month:"short",year:"numeric"}).format(now).toUpperCase();
}
async function init() {
  setIconMarkup();
  setDateLabel();
  await loadData();
  navigate("dashboard");
}
init();
