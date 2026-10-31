// Thin browser client. All business logic, storage and the public page live in the Python API.
const root = document.getElementById("app");

// Opening index.html by double-click (file://) cannot reach the Python API.
if (location.protocol === "file:") {
  root.innerHTML = `<main class="shell"><div class="panel">
    <h1>Start the server first</h1>
    <p class="lead">This page must be opened through the Python server, not as a file.</p>
    <p><code>cd functions/api<br>pip install -r requirements.txt<br>uvicorn main:app --reload</code></p>
    <p class="lead">Then open <strong>http://127.0.0.1:8000</strong></p>
  </div></main>`;
  throw new Error("Open through the server: http://127.0.0.1:8000");
}
const state = {
  token: localStorage.getItem("token"),
  qrUrl: null,
  items: [],
  filter: "all",
  query: "",
};

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const go = (path) => { location.hash = path; };

function logout() {
  localStorage.removeItem("token");
  state.token = null;
  go("/login");
}

function notify(message, type = "success") {
  const existing = document.querySelector(".toast");
  existing?.remove();
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.append(toast);
  setTimeout(() => toast.remove(), 3200);
}

async function api(path, { method = "GET", body, form, blob } = {}) {
  const headers = {};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  let payload;
  if (form) payload = form;
  else if (body) { headers["Content-Type"] = "application/json"; payload = JSON.stringify(body); }

  const res = await fetch(`/api${path}`, { method, headers, body: payload });
  if (res.status === 401 && state.token) { logout(); throw new Error("Session expired. Log in again"); }
  if (!res.ok) {
    let msg = "Something went wrong. Try again";
    try {
      const data = await res.json();
      if (typeof data.detail === "string") msg = data.detail;
      else if (Array.isArray(data.detail)) msg = data.detail.map((d) => d.msg).join(". ");
    } catch (_) {}
    throw new Error(msg);
  }
  if (blob) return res.blob();
  return res.status === 204 ? null : res.json();
}

function saveSession(data) {
  state.token = data.token;
  localStorage.setItem("token", data.token);
  go("/dashboard");
}

/* ---------------- Register / Login ---------------- */
function authView(mode) {
  const isReg = mode === "register";
  root.innerHTML = `
    <main class="shell">
      <form class="panel" id="auth-form">
        <h1>${isReg ? "Create your account" : "Log in"}</h1>
        <p class="lead">${isReg ? "One QR code. Update your menu and offers any time." : "Manage your business page."}</p>
        ${isReg ? `<label for="name">Business name</label><input id="name" required minlength="2" maxlength="80" autocomplete="organization">` : ""}
        <label for="email">Email</label>
        <input id="email" type="email" required autocomplete="email">
        <label for="password">Password</label>
        <input id="password" type="password" required minlength="${isReg ? 8 : 1}" autocomplete="${isReg ? "new-password" : "current-password"}">
        ${isReg ? `<p class="hint">Use at least 8 characters.</p>` : ""}
        <p class="error" id="err"></p>
        <button class="btn primary" type="submit">${isReg ? "Create account" : "Log in"}</button>
        <p class="switch">${isReg ? `Have an account? <a href="#/login">Log in</a>` : `New here? <a href="#/register">Create an account</a>`}</p>
      </form>
    </main>`;

  document.getElementById("auth-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const err = document.getElementById("err");
    err.textContent = "";
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    try {
      const data = isReg
        ? await api("/auth/register", { method: "POST", body: { business_name: document.getElementById("name").value, email, password } })
        : await api("/auth/login", { method: "POST", body: { email, password } });
      saveSession(data);
    } catch (ex) { err.textContent = ex.message; }
  });
}

/* ---------------- Dashboard ---------------- */
const TYPE_LABEL = { text: "Text", link: "Link", image: "Image", pdf: "PDF" };

function itemRow(it) {
  const thumb = it.type === "image" && it.file_url
    ? `<img class="thumb" src="${esc(it.file_url)}" alt="">`
    : `<div class="thumb">${TYPE_LABEL[it.type]}</div>`;
  const detail = it.type === "link" ? it.url_value : it.type === "text" ? it.text_value : it.original_name;
  const hasFile = it.type === "image" || it.type === "pdf";
  return `
    <article class="item" data-id="${it.id}">
      ${thumb}
      <div class="meta"><strong>${esc(it.title)}</strong><span>${TYPE_LABEL[it.type]} · ${esc((detail || "").slice(0, 70))}</span></div>
      <div class="ops">
        <a class="btn small" href="#/editor/${it.id}">Edit</a>
        ${hasFile ? `<button class="btn small" data-act="replace">Replace file</button>
        <input type="file" class="hidden" data-file accept="${it.type === "pdf" ? ".pdf" : "image/*"}">` : ""}
        <button class="btn small danger" data-act="delete">Delete</button>
      </div>
    </article>`;
}

function filteredItems() {
  const query = state.query.trim().toLowerCase();
  return state.items.filter((item) => {
    const matchesType = state.filter === "all" || item.type === state.filter;
    const searchable = `${item.title} ${item.text_value || ""} ${item.url_value || ""} ${item.original_name || ""}`.toLowerCase();
    return matchesType && (!query || searchable.includes(query));
  });
}

function renderDashboardItems() {
  const container = document.querySelector(".items");
  if (!container) return;
  const items = filteredItems();
  container.innerHTML = items.length
    ? items.map(itemRow).join("")
    : `<div class="empty-state"><strong>No matching content</strong><p>Try a different search or filter.</p></div>`;
  bindItemActions();
}

function bindItemActions() {
  const err = document.getElementById("err");
  document.querySelectorAll(".item").forEach((el) => {
    const id = el.dataset.id;
    el.addEventListener("click", async (e) => {
      const act = e.target.dataset.act;
      if (act === "delete") {
        if (!confirm("Delete this content? Customers will no longer see it.")) return;
        try {
          await api(`/content/${id}`, { method: "DELETE" });
          notify("Content deleted");
          dashboardView();
        } catch (ex) { err.textContent = ex.message; }
      }
      if (act === "replace") el.querySelector("[data-file]").click();
    });
    const input = el.querySelector("[data-file]");
    if (input) input.addEventListener("change", async () => {
      if (!input.files.length) return;
      const form = new FormData();
      form.append("file", input.files[0]);
      try {
        await api(`/content/${id}/file`, { method: "PUT", form });
        notify("File replaced");
        dashboardView();
      } catch (ex) { err.textContent = ex.message; }
    });
  });
}

async function dashboardView() {
  root.innerHTML = `<main class="shell"><p>Loading…</p></main>`;
  let biz, items;
  try { [biz, items] = await Promise.all([api("/business/me"), api("/content")]); }
  catch (ex) { return; }
  state.items = items;

  root.innerHTML = `
    <header class="topbar">
      <h1>${esc(biz.name)}</h1>
      <div class="actions">
        <a class="btn" href="${esc(biz.public_url)}" target="_blank" rel="noopener">View public page</a>
        <button class="btn" id="logout">Log out</button>
      </div>
    </header>
    <div class="dash">
      <aside class="qr-card">
        <h2>Your QR code</h2>
        <img id="qr" alt="QR code for your public page">
        <div class="row">
          <button class="btn primary small" id="dl">Download QR code</button>
        </div>
        <p class="url">${esc(biz.public_url)}</p>
        <p class="hint">This code never changes. Print it once.</p>
      </aside>
      <section>
        <div class="list-head"><div><h2>Page content</h2><p class="muted" id="content-summary"></p></div><a class="btn primary" href="#/editor/new">Add content</a></div>
        <div class="toolbar">
          <label class="search"><span class="sr-only">Search content</span><input id="content-search" type="search" placeholder="Search title, text or file…" autocomplete="off"></label>
          <select id="content-filter" aria-label="Filter content">
            <option value="all">All types</option><option value="text">Text</option><option value="link">Links</option><option value="image">Images</option><option value="pdf">PDFs</option>
          </select>
        </div>
        <p class="error" id="err"></p>
        <div class="items"></div>
      </section>
    </div>`;

  document.getElementById("logout").onclick = logout;
  state.filter = "all";
  state.query = "";
  const search = document.getElementById("content-search");
  const filter = document.getElementById("content-filter");
  const summary = document.getElementById("content-summary");
  const updateItems = () => {
    state.query = search.value;
    state.filter = filter.value;
    summary.textContent = `${filteredItems().length} of ${state.items.length} published item${state.items.length === 1 ? "" : "s"}`;
    renderDashboardItems();
  };
  search.addEventListener("input", updateItems);
  filter.addEventListener("change", updateItems);
  updateItems();

  // QR image needs the auth header, so fetch it as a blob.
  try {
    const blob = await api("/business/qr", { blob: true });
    if (state.qrUrl) URL.revokeObjectURL(state.qrUrl);
    state.qrUrl = URL.createObjectURL(blob);
    document.getElementById("qr").src = state.qrUrl;
    document.getElementById("dl").onclick = () => {
      const a = document.createElement("a");
      a.href = state.qrUrl;
      a.download = `qr-${biz.slug}.png`;
      a.click();
      notify("QR code download started");
    };
  } catch (_) {}
}

/* ---------------- Content editor ---------------- */
async function editorView(id) {
  const isNew = id === "new";
  let item = { title: "", type: "text", text_value: "", url_value: "" };
  if (!isNew) {
    try { item = await api(`/content/${id}`); } catch (ex) { return go("/dashboard"); }
  }

  root.innerHTML = `
    <main class="shell wide">
      <form class="panel" id="editor">
        <h1>${isNew ? "Add content" : "Edit content"}</h1>
        <label for="title">Title</label>
        <input id="title" required maxlength="120" value="${esc(item.title)}">

        <label for="type">Content type</label>
        <select id="type" ${isNew ? "" : "disabled"}>
          ${Object.entries(TYPE_LABEL).map(([v, l]) => `<option value="${v}" ${item.type === v ? "selected" : ""}>${l === "Image" ? "Image (menu or offer)" : l === "PDF" ? "PDF file" : l === "Link" ? "External link" : "Text"}</option>`).join("")}
        </select>

        <div id="f-text"><label for="text">Text</label><textarea id="text">${esc(item.text_value)}</textarea></div>
        <div id="f-link"><label for="url">Link address</label><input id="url" type="url" placeholder="https://" value="${esc(item.url_value)}"></div>
        <div id="f-file">
          <label for="file">File</label>
          <input id="file" type="file">
          <p class="hint" id="file-hint"></p>
        </div>

        <p class="error" id="err"></p>
        <button class="btn primary" type="submit">${isNew ? "Save content" : "Save changes"}</button>
        <p class="switch"><a href="#/dashboard">Back to dashboard</a></p>
      </form>
    </main>`;

  const typeEl = document.getElementById("type");
  const fileEl = document.getElementById("file");
  const sync = () => {
    const t = typeEl.value;
    document.getElementById("f-text").classList.toggle("hidden", t !== "text");
    document.getElementById("f-link").classList.toggle("hidden", t !== "link");
    document.getElementById("f-file").classList.toggle("hidden", t !== "image" && t !== "pdf");
    fileEl.accept = t === "pdf" ? ".pdf" : "image/*";
    document.getElementById("file-hint").textContent = isNew
      ? (t === "pdf" ? "PDF, up to 10 MB." : "PNG, JPG, WebP or GIF, up to 10 MB.")
      : `Current file: ${item.original_name || "none"}. Choose a new file only to replace it.`;
  };
  typeEl.addEventListener("change", sync);
  sync();

  document.getElementById("editor").addEventListener("submit", async (e) => {
    e.preventDefault();
    const err = document.getElementById("err");
    err.textContent = "";
    const t = typeEl.value;
    const form = new FormData();
    form.append("title", document.getElementById("title").value);
    if (isNew) form.append("type", t);
    if (t === "text") form.append("text_value", document.getElementById("text").value);
    if (t === "link") form.append("url_value", document.getElementById("url").value);
    if ((t === "image" || t === "pdf") && fileEl.files.length) form.append("file", fileEl.files[0]);
    try {
      await api(isNew ? "/content" : `/content/${id}`, { method: isNew ? "POST" : "PUT", form });
      notify(isNew ? "Content published" : "Changes saved");
      go("/dashboard");
    } catch (ex) { err.textContent = ex.message; }
  });
}

/* ---------------- Router ---------------- */
function route() {
  const [, page, id] = (location.hash.slice(1) || "/").split("/");
  const open = page === "login" || page === "register";
  if (!state.token && !open) return go("/login");
  if (state.token && (open || !page)) return go("/dashboard");

  if (page === "register") return authView("register");
  if (page === "login") return authView("login");
  if (page === "editor" && id) return editorView(id);
  return dashboardView();
}

window.addEventListener("hashchange", route);
route();
