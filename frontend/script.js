// GDC Production Manager — shared frontend logic

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

function fmtMoney(value) {
  const n = Number(value || 0);
  return n.toLocaleString(CURRENT_LANG === "en" ? "en-US" : CURRENT_LANG === "es" ? "es-ES" : "ro-RO", {
    maximumFractionDigits: 0,
  });
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

// ---------------------------------------------------------- app shell ----

const NAV_ITEMS = [
  { href: "index.html", key: "nav_dashboard", icon: "M3 13h4v7H3zM10 4h4v16h-4zM17 9h4v11h-4z" },
  { href: "projects.html", key: "nav_projects", icon: "M4 5h16v3H4zM4 10h16v9H4z" },
  { href: "clients.html", key: "nav_clients", icon: "M12 12a4 4 0 100-8 4 4 0 000 8zM4 20a8 8 0 0116 0" },
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
