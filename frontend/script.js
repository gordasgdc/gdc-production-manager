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
  return `<span class="status-pill st-${status}"><span class="dot"></span>${t("status_" + status)}</span>`;
}

function miniPipelineHtml(status) {
  const idx = STATUS_ORDER.indexOf(status);
  return `<div class="mini-pipeline" title="${t("status_" + status)}">` +
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
      ${STATUS_ORDER.map(s => `<span>${t("status_" + s)} (${byStatus[s] || 0})</span>`).join("")}
    </div>
  `;
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

// ---------------------------------------------------------- app shell ----

const NAV_ITEMS = [
  { href: "index.html", key: "nav_dashboard", icon: "M3 13h4v7H3zM10 4h4v16h-4zM17 9h4v11h-4z" },
  { href: "projects.html", key: "nav_projects", icon: "M4 5h16v3H4zM4 10h16v9H4z" },
  { href: "clients.html", key: "nav_clients", icon: "M12 12a4 4 0 100-8 4 4 0 000 8zM4 20a8 8 0 0116 0" },
  { href: "courses.html", key: "nav_courses", icon: "M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5A2.5 2.5 0 006.5 22H20V4H6.5A2.5 2.5 0 004 6.5v13z" },
  { href: "products.html", key: "nav_products", icon: "M21 8l-9-5-9 5 9 5 9-5zM3 8v8l9 5 9-5V8M12 13v8" },
  { href: "reminders.html", key: "nav_reminders", icon: "M12 8v4l3 3M12 22a2 2 0 002-2h-4a2 2 0 002 2zM18 8a6 6 0 10-12 0c0 6-2 8-2 8h16s-2-2-2-8z" },
  { href: "calendar.html", key: "nav_calendar", icon: "M4 6h16v14H4zM4 10h16M8 3v4M16 3v4" },
  { href: "settings.html", key: "nav_settings", icon: "M12 15a3 3 0 100-6 3 3 0 000 6zM4 12h2m12 0h2M12 4v2m0 12v2M6.3 6.3l1.4 1.4m8.6 8.6l1.4 1.4M6.3 17.7l1.4-1.4m8.6-8.6l1.4-1.4" },
];

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
        <button class="theme-toggle" id="theme-toggle-btn">
          <span id="theme-toggle-label">${CURRENT_THEME === "light" ? t("theme_light") : t("theme_dark")}</span>
          <span>${CURRENT_THEME === "light" ? "☀️" : "🌙"}</span>
        </button>
        <div class="lang-switch">
          ${["ro", "en", "es"].map(l => `<button class="lang-btn ${CURRENT_LANG === l ? "active" : ""}" data-lang="${l}">${l.toUpperCase()}</button>`).join("")}
        </div>
        <div class="user-chip">
          <span>${(user && (user.display_name || user.username)) || ""}</span>
          <button id="logout-btn">${t("logout")}</button>
        </div>
        <button class="btn btn-ghost btn-sm btn-block" id="quit-btn">${t("quit")}</button>
      </div>
    </aside>
    <main class="main" id="main-content"></main>
  `;

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
