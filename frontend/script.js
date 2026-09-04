// GDC Production Manager — shared frontend logic

let CURRENT_THEME = localStorage.getItem("gdc_theme") || "dark";

function applyTheme(theme) {
  CURRENT_THEME = theme === "light" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", CURRENT_THEME);
  localStorage.setItem("gdc_theme", CURRENT_THEME);
}

applyTheme(CURRENT_THEME);

const API = {
  async _call(method, url, body) {
    const opts = {
      method,
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
    };
    if (body !== undefined) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    let data = null;
    try {
      data = await res.json();
    } catch (e) {
      data = null;
    }
    if (!res.ok) {
      if (res.status === 403 && data && data.error === "trial_expired" && !location.pathname.endsWith("/activate.html")) {
        window.location.href = "activate.html";
        return new Promise(() => {}); // navigare in curs — nu mai continua fluxul curent
      }
      const err = new Error((data && data.error) || "request_failed");
      err.status = res.status;
      err.payload = data;
      throw err;
    }
    return data;
  },
  get(url) { return this._call("GET", url); },
  post(url, body) { return this._call("POST", url, body); },
  put(url, body) { return this._call("PUT", url, body); },
  del(url) { return this._call("DELETE", url); },
};

// --- Iconite line-art minimale pentru pagina de Ajutor -----------------
function helpSvgIcon(path) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${path}</svg>`;
}
const HELP_ICONS = {
  folder: helpSvgIcon('<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>'),
  steps: helpSvgIcon('<path d="M5 20V13"/><path d="M12 20V9"/><path d="M19 20V5"/>'),
  note: helpSvgIcon('<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/>'),
  coins: helpSvgIcon('<circle cx="8" cy="10" r="5"/><circle cx="15" cy="15" r="5"/>'),
  users: helpSvgIcon('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16.5 8.5a3.2 3.2 0 0 1 0 6.2"/><path d="M18.5 20a5.8 5.8 0 0 0-3.3-5.3"/>'),
  book: helpSvgIcon('<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>'),
  package: helpSvgIcon('<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/>'),
  checklist: helpSvgIcon('<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M7 9l1.5 1.5L11 7"/><path d="M13 8.5h5"/><path d="M7 15l1.5 1.5L11 13"/><path d="M13 14.5h5"/>'),
  bell: helpSvgIcon('<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>'),
  calendar: helpSvgIcon('<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>'),
  fileText: helpSvgIcon('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6"/><path d="M9 17h6"/>'),
  download: helpSvgIcon('<path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M4 19h16"/>'),
  refresh: helpSvgIcon('<path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"/><path d="M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>'),
  key: helpSvgIcon('<circle cx="8" cy="15" r="4"/><path d="M10.5 12.5L20 3"/><path d="M17 6l3 3"/><path d="M14 9l2.5 2.5"/>'),
  shield: helpSvgIcon('<path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z"/><path d="M9 12l2 2 4-4"/>'),
  fingerprint: helpSvgIcon('<path d="M12 3a7 7 0 0 1 7 7c0 3.5-1 6-1 9"/><path d="M12 3a7 7 0 0 0-7 7c0 2 .3 3.5.8 5"/><path d="M12 7a3 3 0 0 1 3 3c0 4-1.5 6-1.5 8"/><path d="M9.5 10a2.5 2.5 0 0 1 5 0c0 4.5-1.8 7-1.8 9"/><path d="M7 10c0 5 1 7.5 2.5 9.5"/>'),
  tag: helpSvgIcon('<path d="M20.6 12.4L12.4 20.6a2 2 0 0 1-2.8 0l-7-7a2 2 0 0 1 0-2.8L10.8 2.6a2 2 0 0 1 1.4-.6H19a2 2 0 0 1 2 2v6.6a2 2 0 0 1-.4 1.4z"/><circle cx="15.5" cy="7.5" r="1.5"/>'),
  globe: helpSvgIcon('<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15 15 0 0 1 0 20a15 15 0 0 1 0-20z"/>'),
  moon: helpSvgIcon('<path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/>'),
  database: helpSvgIcon('<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.66 3.58 3 8 3s8-1.34 8-3V5"/><path d="M4 11v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6"/>'),
};

// --- WebAuthn (Touch ID / Windows Hello) helpers -----------------------
// Codeaza/decodeaza intre ArrayBuffer (ce foloseste navigator.credentials)
// si base64url (ce trimite/primeste backend-ul in JSON), exact schema
// pe care py_webauthn o asteapta: id/rawId/response.* ca stringuri base64url.

function bufToBase64url(buf) {
  const bytes = new Uint8Array(buf);
  let str = "";
  for (const b of bytes) str += String.fromCharCode(b);
  return btoa(str).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function base64urlToBuf(str) {
  const b64 = str.replace(/-/g, "+").replace(/_/g, "/").padEnd(str.length + (4 - str.length % 4) % 4, "=");
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes.buffer;
}

function webauthnSupported() {
  return !!(window.PublicKeyCredential && navigator.credentials);
}

async function webauthnRegister() {
  const options = await API.get("/api/auth/webauthn/register-options");
  options.challenge = base64urlToBuf(options.challenge);
  options.user.id = base64urlToBuf(options.user.id);
  if (options.excludeCredentials) {
    options.excludeCredentials = options.excludeCredentials.map(c => ({ ...c, id: base64urlToBuf(c.id) }));
  }
  const credential = await navigator.credentials.create({ publicKey: options });
  const payload = {
    id: credential.id,
    rawId: bufToBase64url(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufToBase64url(credential.response.clientDataJSON),
      attestationObject: bufToBase64url(credential.response.attestationObject),
    },
  };
  await API.post("/api/auth/webauthn/register", payload);
}

async function webauthnLogin(username) {
  const options = await API.post("/api/auth/webauthn/login-options", { username });
  options.challenge = base64urlToBuf(options.challenge);
  if (options.allowCredentials) {
    options.allowCredentials = options.allowCredentials.map(c => ({ ...c, id: base64urlToBuf(c.id) }));
  }
  const credential = await navigator.credentials.get({ publicKey: options });
  const payload = {
    id: credential.id,
    rawId: bufToBase64url(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufToBase64url(credential.response.clientDataJSON),
      authenticatorData: bufToBase64url(credential.response.authenticatorData),
      signature: bufToBase64url(credential.response.signature),
      userHandle: credential.response.userHandle ? bufToBase64url(credential.response.userHandle) : null,
    },
  };
  return API.post("/api/auth/webauthn/login", payload);
}

function showToast(message, type = "success") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2600);
}

function errorMessage(err) {
  const code = err && err.message;
  const key = "error_" + code;
  const dict = TRANSLATIONS[CURRENT_LANG] || TRANSLATIONS.ro;
  if (code && dict["error_" + code]) return t("error_" + code);
  return t("error_generic");
}

const CURRENCY_SYMBOLS = { EUR: "€", RON: "lei" };

function fmtMoney(value, currency) {
  const n = Number(value || 0);
  const formatted = n.toLocaleString(CURRENT_LANG === "en" ? "en-US" : CURRENT_LANG === "es" ? "es-ES" : "ro-RO", {
    maximumFractionDigits: 0,
  });
  if (!currency) return formatted;
  const symbol = CURRENCY_SYMBOLS[currency] || currency;
  return currency === "RON" ? `${formatted} ${symbol}` : `${symbol}${formatted}`;
}

function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso + "T00:00:00");
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(CURRENT_LANG === "en" ? "en-US" : CURRENT_LANG === "es" ? "es-ES" : "ro-RO", {
    year: "numeric", month: "short", day: "numeric",
  });
}

function statusPillHtml(status) {
  return `<span class="status-pill st-${status}"><span class="dot"></span>${stageLabel(status)}</span>`;
}

/// Payment-status badge (red/amber/green) - same .status-pill visual
/// language as statusPillHtml, just a different color set (pay-*
/// modifiers in style.css). `status` can be null (no projects yet, no
/// badge to show) - callers should check before calling this.
/// v2.0.0: `isOverdue` (only meaningful for a Project, which has a
/// delivery_date) swaps the pill to a distinct "overdue" look, computed
/// server-side (Project.to_dict()'s is_overdue) - never a 5th stored
/// payment_status value, see models.py PAYMENT_STATUSES.
function payStatusPillHtml(status, isOverdue) {
  if (!status) return "";
  if (isOverdue) {
    return `<span class="status-pill pay-overdue"><span class="dot"></span>${t("overdue_badge")}</span>`;
  }
  return `<span class="status-pill pay-${status}"><span class="dot"></span>${t("pay_" + status)}</span>`;
}

/// v2.0.0: the persistent attention badge - shown wherever a flagged
/// client/project appears (list rows, previews). Returns "" when not
/// flagged, so callers can inline it unconditionally.
function flagBadgeHtml(isFlagged) {
  return isFlagged ? `<span class="flag-badge">${t("flag_badge")}</span>` : "";
}

/// Opens Google Maps at an address - no API key, just a plain search URL.
function mapsUrl(address) {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
}

function equipStatusPillHtml(status) {
  return `<span class="status-pill eq-${status}"><span class="dot"></span>${t("eq_" + status)}</span>`;
}

/// Opens the OS's own native folder picker (via /api/pick-folder, which
/// runs server-side since a browser can't show a real native dialog) and
/// fills the given text input with whatever the user chose. A cancelled
/// dialog leaves the field untouched - never clears it.
async function pickFolderInto(inputId) {
  try {
    const result = await API.post("/api/pick-folder");
    if (result.path) {
      document.getElementById(inputId).value = result.path;
    }
  } catch (e) {
    showToast(errorMessage(e), "error");
  }
}

/// v2.0.0: "Deschide folderul" - reveals the path currently in the given
/// input in Finder (Mac) / Explorer (Windows), via /api/open-folder. A
/// 404 (path moved/deleted since it was saved) shows a clear message
/// instead of doing nothing silently.
async function openFolderFrom(inputId) {
  const path = (document.getElementById(inputId).value || "").trim();
  if (!path) return;
  try {
    await API.post("/api/open-folder", { path });
  } catch (e) {
    if (e.status === 404) {
      showToast(t("open_folder_missing"), "error");
    } else {
      showToast(errorMessage(e), "error");
    }
  }
}

function miniPipelineHtml(status) {
  const idx = STATUS_ORDER.indexOf(status);
  return `<div class="mini-pipeline" title="${stageLabel(status)}">` +
    STATUS_ORDER.map((s, i) => {
      let cls = "dot";
      if (i < idx) cls += " done";
      else if (i === idx) cls += " current";
      return `<span class="${cls}"></span>`;
    }).join("") + `</div>`;
}

function pipelineHtml(byStatus) {
  const total = STATUS_ORDER.reduce((sum, s) => sum + (byStatus[s] || 0), 0) || 1;
  return `
    <div class="pipeline">
      ${STATUS_ORDER.map(s => {
        const count = byStatus[s] || 0;
        const width = Math.max((count / total) * 100, count > 0 ? 6 : 100 / STATUS_ORDER.length);
        return `<div class="seg ${count > 0 ? "done" : ""}" style="flex: ${count > 0 ? count : 0.4}"></div>`;
      }).join("")}
    </div>
    <div class="pipeline-labels">
      ${STATUS_ORDER.map(s => `<span>${stageLabel(s)} (${byStatus[s] || 0})</span>`).join("")}
    </div>
  `;
}

/// v2.0.0: the real interactive pipeline stepper - every stage is a
/// clickable node (jumps directly there, forward or backward), not just
/// a "next" arrow. Caller wires [data-jump-stage] after inserting this;
/// `currentStatus` may be a deactivated/unknown key (falls back to "no
/// stage reached yet" rendering, current index -1) rather than crashing.
function stageStepperHtml(projectId, currentStatus) {
  const curIdx = STATUS_ORDER.indexOf(currentStatus);
  return `
    <div class="stage-stepper">
      ${STATUS_ORDER.map((s, i) => {
        let cls = "stage-node";
        if (i < curIdx) cls += " done";
        else if (i === curIdx) cls += " current";
        return `
          ${i > 0 ? `<span class="stage-connector ${i <= curIdx ? "done" : ""}"></span>` : ""}
          <button type="button" class="${cls}" data-jump-stage="${projectId}:${s}" title="${escapeHtmlShared(stageLabel(s))}">
            <span class="stage-dot"></span>
            <span class="stage-label">${escapeHtmlShared(stageLabel(s))}</span>
          </button>
        `;
      }).join("")}
    </div>
    <button type="button" class="btn btn-ghost btn-sm" data-stage-history="${projectId}" style="margin-top:10px;">🕘 ${t("stage_history_btn")}</button>
    <div id="stage-history-panel-${projectId}"></div>
  `;
}

/// Renders the read-only audit trail fetched from
/// GET /api/projects/:id/stage-history into the panel stageStepperHtml
/// already left in the DOM for this project - toggles open/closed on
/// repeated clicks rather than re-fetching every time.
function stageHistoryListHtml(events) {
  if (!events.length) {
    return `<p class="stage-history-empty">${t("stage_history_empty")}</p>`;
  }
  return `<div class="stage-history-list">` +
    events.map(e => `
      <div class="stage-history-row">
        <span class="stage-history-label">${escapeHtmlShared(stageLabel(e.stage_key))}</span>
        <span class="stage-history-date mono">${fmtDate(e.entered_at ? e.entered_at.slice(0, 10) : null)}</span>
        ${e.note_snapshot ? `<span class="stage-history-note">${escapeHtmlShared(e.note_snapshot)}</span>` : ""}
      </div>
    `).join("") + `</div>`;
}

function renderNotifItem(n) {
  let cls = "notif-item", icon = "ℹ️", text = "";
  if (n.type === "deadline_overdue") {
    cls += " notif-overdue"; icon = "⚠️";
    text = `<strong>${escapeHtmlShared(n.project_title)}</strong> — ${tf("notif_deadline_overdue", { days: n.days })}`;
  } else if (n.type === "deadline_soon") {
    cls += " notif-soon"; icon = "⏰";
    const label = n.days === 0 ? t("notif_deadline_today") : tf("notif_deadline_soon", { days: n.days });
    text = `<strong>${escapeHtmlShared(n.project_title)}</strong> — ${label}`;
  } else if (n.type === "payment_outstanding") {
    cls += " notif-payment"; icon = "💶";
    text = `<strong>${escapeHtmlShared(n.project_title)}</strong> — ${tf("notif_payment_outstanding", { amount: fmtMoney(n.amount) })}`;
  }
  return `<div class="${cls}"><span class="notif-icon">${icon}</span><span class="notif-text">${text}</span></div>`;
}

function escapeHtmlShared(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

async function fetchNotificationCount() {
  try {
    const data = await API.get("/api/notifications");
    return (data.notifications || []).length;
  } catch (e) {
    return 0;
  }
}

// ------------------------------------------------- pop-up notifications ----
// Checks on load and every 15 minutes for deadlines, overdue invoices, and
// reminders due soon. Shows an in-app toast always, plus a native browser
// notification when permission has been granted (best available option
// since the app runs as a local page in the system browser).

function notifBodyText(n) {
  if (n.type === "deadline_overdue") return tf("notif_deadline_overdue", { days: n.days });
  if (n.type === "deadline_soon") return n.days === 0 ? t("notif_deadline_today") : tf("notif_deadline_soon", { days: n.days });
  if (n.type === "payment_outstanding") return tf("notif_payment_outstanding", { amount: fmtMoney(n.amount) });
  return "";
}

async function checkAndPopupNotifications() {
  const todayKey = "gdc_notified_" + new Date().toISOString().slice(0, 10);
  let shown = [];
  try { shown = JSON.parse(localStorage.getItem(todayKey) || "[]"); } catch (e) { shown = []; }

  try {
    const [notifData, reminders] = await Promise.all([
      API.get("/api/notifications"),
      API.get("/api/reminders/upcoming"),
    ]);

    const items = [];
    (notifData.notifications || []).forEach(n => {
      items.push({ key: `notif-${n.type}-${n.project_id}`, title: n.project_title, body: notifBodyText(n) });
    });
    (reminders || []).forEach(r => {
      const due = new Date(r.due_date + "T00:00:00");
      const today = new Date(); today.setHours(0, 0, 0, 0);
      const daysLeft = Math.round((due - today) / 86400000);
      if (daysLeft <= 3) {
        items.push({ key: `reminder-${r.id}`, title: r.title, body: fmtDate(r.due_date) + (r.due_time ? " · " + r.due_time : "") });
      }
    });

    let changed = false;
    items.forEach(item => {
      if (shown.includes(item.key)) return;
      shown.push(item.key);
      changed = true;
      showToast(`${item.title} — ${item.body}`);
      if (window.Notification && Notification.permission === "granted") {
        try { new Notification(item.title, { body: item.body, icon: "icon.png" }); } catch (e) {}
      }
    });
    if (changed) localStorage.setItem(todayKey, JSON.stringify(shown));
  } catch (e) {
    // Silent — polling shouldn't interrupt normal use if the check fails.
  }
}

function initNotificationPolling() {
  if (window.__gdcPollingStarted) return;
  window.__gdcPollingStarted = true;

  if (window.Notification && Notification.permission === "default") {
    Notification.requestPermission().catch(() => {});
  }

  checkAndPopupNotifications();
  setInterval(checkAndPopupNotifications, 15 * 60 * 1000);
}

// ---------------------------------------------------------- app shell ----

const NAV_ITEMS = [
  { href: "index.html", key: "nav_dashboard", icon: "M3 13h4v7H3zM10 4h4v16h-4zM17 9h4v11h-4z" },
  { href: "projects.html", key: "nav_projects", icon: "M4 5h16v3H4zM4 10h16v9H4z" },
  { href: "clients.html", key: "nav_clients", icon: "M12 12a4 4 0 100-8 4 4 0 000 8zM4 20a8 8 0 0116 0" },
  { href: "courses.html", key: "nav_courses", icon: "M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5A2.5 2.5 0 006.5 22H20V4H6.5A2.5 2.5 0 004 6.5v13z" },
  { href: "products.html", key: "nav_products", icon: "M21 8l-9-5-9 5 9 5 9-5zM3 8v8l9 5 9-5V8M12 13v8" },
  { href: "equipment.html", key: "nav_equipment", icon: "M3 7h3l2-3h8l2 3h3v13H3zM12 17a4 4 0 100-8 4 4 0 000 8z" },
  { href: "reminders.html", key: "nav_reminders", icon: "M12 8v4l3 3M12 22a2 2 0 002-2h-4a2 2 0 002 2zM18 8a6 6 0 10-12 0c0 6-2 8-2 8h16s-2-2-2-8z" },
  { href: "calendar.html", key: "nav_calendar", icon: "M4 6h16v14H4zM4 10h16M8 3v4M16 3v4" },
  { href: "help.html", key: "nav_help", icon: "M2 12a10 10 0 1 0 20 0 10 10 0 1 0 -20 0M9.09 9a3 3 0 015.83 1c0 2-3 2-3 3M12 17h.01" },
  { href: "settings.html", key: "nav_settings", icon: "M12 15a3 3 0 100-6 3 3 0 000 6zM4 12h2m12 0h2M12 4v2m0 12v2M6.3 6.3l1.4 1.4m8.6 8.6l1.4 1.4M6.3 17.7l1.4-1.4m8.6-8.6l1.4-1.4" },
];

/// Checks for a newer version automatically on every page load (not
/// just the manual button in Settings) and shows a dismissible banner
/// spanning the full app width, PLUS a one-time modal pop-up (same
/// dismissal state - closing either one hides both, so they never
/// stack/duplicate). Dismissal is per-version (same
/// gdcpm_dismissed_update_version convention as the sibling GDC Swift
/// apps) - dismissing v1.5.0's notice doesn't hide a real v1.6.0 later.
/// BUG FIX 2026-08-27 (CLAUDE.md Partea 1, Regula 20): butonul deschidea
/// download_url intr-un tab nou de browser (catre GitHub) - inlocuit cu
/// un apel la /api/update/install, care descarca+instaleaza direct din
/// server, fara niciun tab nou. Vezi self_updater.py/update_routes.py.
async function checkUpdateBanner() {
  const slot = document.getElementById("update-banner-slot");
  if (!slot) return;
  try {
    const result = await API.get("/api/update/check");
    if (!result.update_available) return;
    const dismissed = localStorage.getItem("gdcpm_dismissed_update_version");
    if (dismissed === result.latest_version) return;

    const platform = navigator.platform.toLowerCase().includes("mac") ? "mac" : "windows";
    const url = result.download_url[platform] || result.download_url.mac;

    const dismissAll = () => {
      localStorage.setItem("gdcpm_dismissed_update_version", result.latest_version);
      slot.innerHTML = "";
      const modal = document.getElementById("update-modal-overlay");
      if (modal) modal.remove();
    };

    slot.innerHTML = `
      <div class="update-banner">
        <span class="msg">${tf("update_available", { version: result.latest_version })}${result.changes ? " — " + escapeHtmlShared(result.changes) : ""}</span>
        <button class="btn btn-primary btn-sm" id="update-banner-install">${t("update_download_btn")}</button>
        <button class="btn btn-ghost btn-sm" id="dismiss-update-banner">${t("dismiss")}</button>
      </div>
    `;
    document.getElementById("update-banner-install").addEventListener("click", () => startSelfUpdate(result));
    document.getElementById("dismiss-update-banner").addEventListener("click", dismissAll);

    const overlay = document.createElement("div");
    overlay.id = "update-modal-overlay";
    overlay.className = "update-modal-overlay";
    overlay.innerHTML = `
      <div class="update-modal" role="dialog" aria-modal="true" aria-labelledby="update-modal-title">
        <h2 id="update-modal-title">${t("update_modal_title")}</h2>
        <p>${tf("update_modal_body", { version: result.latest_version })}${result.changes ? " — " + escapeHtmlShared(result.changes) : ""}</p>
        <div class="update-modal-actions">
          <button class="btn btn-ghost" id="update-modal-later">${t("update_modal_later")}</button>
          <button class="btn btn-primary" id="update-modal-download">${t("update_download_btn")}</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
    document.getElementById("update-modal-later").addEventListener("click", dismissAll);
    document.getElementById("update-modal-download").addEventListener("click", () => { dismissAll(); startSelfUpdate(result); });
    overlay.addEventListener("click", (e) => { if (e.target === overlay) dismissAll(); });
  } catch (e) {
    // silent - a failed update check should never block using the app
  }
}

function escapeHtmlShared(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

/// Descarca+instaleaza direct din server (POST /api/update/install), apoi
/// face polling pe /api/update/install-status pana la "done"/"failed" -
/// NICIODATA un tab nou de browser catre GitHub. Vezi self_updater.py.
async function startSelfUpdate(result) {
  const overlay = document.createElement("div");
  overlay.className = "update-modal-overlay";
  overlay.innerHTML = `
    <div class="update-modal" role="dialog" aria-modal="true">
      <h2>${t("app_title") || "GDC Production Manager"} ${result.latest_version}</h2>
      <p id="self-update-status">Se descarcă actualizarea…</p>
    </div>
  `;
  document.body.appendChild(overlay);
  const statusEl = overlay.querySelector("#self-update-status");

  try {
    await API.post("/api/update/install", { version: result.latest_version, download_url: result.download_url });
  } catch (e) {
    statusEl.textContent = "Nu am putut porni actualizarea. Încearcă din nou.";
    return;
  }

  const poll = setInterval(async () => {
    try {
      const status = await API.get("/api/update/install-status");
      if (status.stage === "downloading") statusEl.textContent = "Se descarcă actualizarea…";
      else if (status.stage === "installing") statusEl.textContent = "Se instalează…";
      else if (status.stage === "done") {
        statusEl.textContent = "Instalat! Aplicația repornește…";
        clearInterval(poll);
      } else if (status.stage === "failed") {
        statusEl.textContent = `Actualizarea a eșuat: ${status.error || "eroare necunoscută"}`;
        clearInterval(poll);
      }
    } catch (e) {
      // Serverul s-a inchis deja (update instalat cu succes) - normal.
      statusEl.textContent = "Instalat! Aplicația repornește…";
      clearInterval(poll);
    }
  }, 1000);
}

function renderShell(activeHref, user) {
  const shell = document.getElementById("app-shell");
  if (!shell) return;

  const nav = NAV_ITEMS.map(item => `
    <a class="nav-link ${item.href === activeHref ? "active" : ""}" href="${item.href}">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${item.icon}"/></svg>
      <span>${t(item.key)}</span>
    </a>
  `).join("");

  shell.innerHTML = `
    <div id="update-banner-slot"></div>
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">G</div>
        <div class="brand-text">
          <div class="name">GDC</div>
          <div class="sub">PRODUCTION MGR</div>
        </div>
      </div>
      <nav>${nav}</nav>
      <div class="sidebar-footer">
        <div id="license-badge-slot"></div>
        <button class="theme-toggle" id="theme-toggle-btn">
          <span id="theme-toggle-label">${CURRENT_THEME === "light" ? t("theme_light") : t("theme_dark")}</span>
          <span>${CURRENT_THEME === "light" ? "☀️" : "🌙"}</span>
        </button>
        <div class="lang-switch">
          ${["ro", "en", "es"].map(l => `<button class="lang-btn ${CURRENT_LANG === l ? "active" : ""}" data-lang="${l}">${l.toUpperCase()}</button>`).join("")}
        </div>
        <div class="user-chip user-chip-profile">
          <div class="user-chip-row">
            <span>${escapeHtmlShared((user && (user.display_name || user.username)) || t("profile_anonymous"))}</span>
            <button id="logout-btn">${t("logout")}</button>
          </div>
          <div class="sidebar-hwid-row" id="sidebar-hwid-row" title="${t("machine_id_label")}">
            <span class="mono" id="sidebar-hwid-value">…</span>
            <button type="button" id="sidebar-copy-hwid" title="${t("copy_btn")}">⧉</button>
          </div>
        </div>
        <button class="btn btn-ghost btn-sm btn-block" id="quit-btn">${t("quit")}</button>
      </div>
    </aside>
    <main class="main" id="main-content"></main>
  `;

  checkUpdateBanner();

  document.getElementById("theme-toggle-btn").addEventListener("click", async () => {
    const next = CURRENT_THEME === "light" ? "dark" : "light";
    applyTheme(next);
    document.getElementById("theme-toggle-label").textContent = next === "light" ? t("theme_light") : t("theme_dark");
    document.getElementById("theme-toggle-btn").querySelector("span:last-child").textContent = next === "light" ? "☀️" : "🌙";
    try { await API.post("/api/auth/theme", { theme: next }); } catch (e) {}
  });

  shell.querySelectorAll(".lang-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      setLang(btn.dataset.lang);
      try { await API.post("/api/auth/language", { language: btn.dataset.lang }); } catch (e) {}
      window.location.reload();
    });
  });

  document.getElementById("logout-btn").addEventListener("click", async () => {
    await API.post("/api/auth/logout");
    window.location.href = "login.html";
  });

  document.getElementById("quit-btn").addEventListener("click", async () => {
    try { await API.post("/api/quit"); } catch (e) {}
    document.getElementById("main-content").innerHTML =
      `<div class="empty-state"><div class="icon">⏻</div><p>Poți închide această fereastră / You can close this window.</p></div>`;
  });

  initNotificationPolling();
  renderLicenseBadge();
}

async function renderLicenseBadge() {
  const slot = document.getElementById("license-badge-slot");
  const hwidValue = document.getElementById("sidebar-hwid-value");
  try {
    const status = await API.get("/api/license/status");

    // v2.0.0 (Regula 12 - profil + HWID vizibil în sidebar, nu doar în
    // Settings): populates regardless of license state, unlike the badge
    // below which only shows during trial.
    if (hwidValue) hwidValue.textContent = status.machine_id;

    if (slot && !status.licensed) {
      const warn = status.trial_days_remaining <= 2;
      slot.innerHTML = `
        <a href="settings.html#license" class="license-badge ${warn ? "warn" : ""}" style="text-decoration:none; margin-bottom:10px; justify-content:center;">
          ⏰ ${tf("license_status_trial", { days: status.trial_days_remaining })}
        </a>
      `;
    }

    const copyBtn = document.getElementById("sidebar-copy-hwid");
    if (copyBtn) {
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(status.machine_id).then(() => showToast(t("copied_toast")));
      };
    }
  } catch (e) {}
}

// Ensures the user is authenticated, then calls onReady(user).
// Redirects to login.html if not.
async function requireAuth(onReady) {
  try {
    const data = await API.get("/api/auth/status");
    if (!data.authenticated) {
      window.location.href = "login.html";
      return;
    }
    setLang(data.user.language || CURRENT_LANG);
    applyTheme(data.user.theme || CURRENT_THEME);
    await loadPipelineDefs();
    onReady(data.user);
  } catch (e) {
    window.location.href = "login.html";
  }
}

function applyStaticTranslations() {
  document.querySelectorAll("[data-t]").forEach(el => {
    el.textContent = t(el.getAttribute("data-t"));
  });
  document.querySelectorAll("[data-t-placeholder]").forEach(el => {
    el.setAttribute("placeholder", t(el.getAttribute("data-t-placeholder")));
  });
}
