const root = document.getElementById("app");
if (location.protocol === "file:") {
  root.innerHTML = `<main class="shell"><div class="panel"><h1>Start the server first</h1>
    <p class="lead">Open this app through the Python server at <strong>http://127.0.0.1:8000</strong>.</p></div></main>`;
  throw new Error("Open through the server");
}

const state = { token: localStorage.getItem("token"), qrUrls: new Map() };
const TYPE_LABEL = { text: "Text", link: "Link", image: "Image", pdf: "PDF" };
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const go = (path) => { location.hash = path; };

function logout() {
  localStorage.removeItem("token");
  state.token = null;
  go("/login");
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

function authView(mode) {
  const register = mode === "register";
  root.innerHTML = `<main class="shell"><form class="panel" id="auth-form">
    <h1>${register ? "Create your account" : "Log in"}</h1>
    <p class="lead">${register ? "Create permanent QR codes for your business." : "Manage your QR codes and content."}</p>
    ${register ? '<label for="name">Business name</label><input id="name" required minlength="2" maxlength="80">' : ""}
    <label for="email">Email</label><input id="email" type="email" required>
    <label for="password">Password</label><input id="password" type="password" required minlength="${register ? 8 : 1}">
    <p class="error" id="err"></p><button class="btn primary" type="submit">${register ? "Create account" : "Log in"}</button>
    <p class="switch">${register ? 'Have an account? <a href="#/login">Log in</a>' : 'New here? <a href="#/register">Create an account</a>'}</p>
  </form></main>`;
  document.getElementById("auth-form").onsubmit = async (e) => {
    e.preventDefault();
    const err = document.getElementById("err"); err.textContent = "";
    try {
      const data = await api(`/auth/${register ? "register" : "login"}`, {
        method: "POST",
        body: { business_name: register ? document.getElementById("name").value : undefined,
          email: document.getElementById("email").value, password: document.getElementById("password").value },
      });
      saveSession(data);
    } catch (ex) { err.textContent = ex.message; }
  };
}

function itemRow(it) {
  const thumb = it.type === "image" && it.file_url ? `<img class="thumb" src="${esc(it.file_url)}" alt="">` :
    `<div class="thumb">${TYPE_LABEL[it.type]}</div>`;
  return `<article class="item" data-id="${it.id}">${thumb}<div class="meta">
    <span>${TYPE_LABEL[it.type]}</span></div><div class="ops">
    ${it.type === "text" ? `<a class="btn small" href="#/editor/${it.id}">Edit text</a>` : ""}
    ${it.type === "link" ? `<a class="btn small" href="#/editor/${it.id}">Edit link</a>` : ""}
    ${it.type === "image" || it.type === "pdf" ? `<button class="btn small" data-act="replace">Replace file</button><input type="file" class="hidden" data-file accept="${it.type === "pdf" ? ".pdf" : "image/*"}">` : ""}
    </div></article>`;
}

async function dashboardView() {
  root.innerHTML = `<main class="shell"><p>Loading…</p></main>`;
  let codes;
  try { [, codes] = await Promise.all([api("/business/me"), api("/business/qr-codes")]); }
  catch (_) { return; }
  root.innerHTML = `<header class="topbar"><h1>QR code manager</h1><button class="btn" id="logout">Log out</button></header>
    <main class="dashboard"><section class="intro"><div><h2>Your QR codes</h2>
      <p class="lead">Every code has a permanent link. Update its content without reprinting the code.</p></div>
      <form id="qr-form" class="new-qr"><input id="qr-name" required maxlength="120" placeholder="New QR name, e.g. Table 1">
      <button class="btn primary" type="submit">Create QR code</button></form></section>
      <p class="error" id="err"></p><div class="qr-grid">${codes.map((code) => `<article class="qr-card" data-qr="${code.id}">
        <div class="qr-card-head"><div><h3>${esc(code.name)}</h3><span class="hint">One permanent destination</span></div>
        <button class="btn small danger" data-act="delete-qr">Delete</button></div>
        <img class="qr-image" data-qr-image alt="QR code for ${esc(code.name)}"><p class="url">${esc(code.public_url)}</p>
        <div class="row"><a class="btn small" href="${esc(code.public_url)}" target="_blank" rel="noopener">View page</a>
        <button class="btn small" data-act="download-qr">Download</button><a class="btn primary small" data-act="destination" href="#/editor/new?qr=${code.id}">Set destination</a></div>
        <div class="qr-items"><p class="hint">Loading destination…</p></div></article>`).join("")}</div></main>`;
  document.getElementById("logout").onclick = logout;
  const err = document.getElementById("err");
  document.getElementById("qr-form").onsubmit = async (e) => {
    e.preventDefault();
    try { await api("/business/qr-codes", { method: "POST", body: { name: document.getElementById("qr-name").value } }); dashboardView(); }
    catch (ex) { err.textContent = ex.message; }
  };
  for (const code of codes) {
    const card = root.querySelector(`[data-qr="${code.id}"]`);
    try {
      const [blob, item] = await Promise.all([api(`/business/qr-codes/${code.id}/image`, { blob: true }), api(`/content?qr_code_id=${code.id}`)]);
      const url = URL.createObjectURL(blob); state.qrUrls.set(code.id, url);
      card.querySelector("[data-qr-image]").src = url;
      card.querySelector(".qr-items").innerHTML = item
        ? `<div class="items">${itemRow(item)}</div>`
        : `<p class="hint">No destination yet. Add one link or image.</p>`;
      const destination = card.querySelector("[data-act='destination']");
      if (item) {
        destination.textContent = "Update destination";
        destination.href = `#/editor/${item.id}`;
      }
      card.querySelector("[data-act='download-qr']").onclick = () => { const a = document.createElement("a"); a.href = url; a.download = `qr-${code.slug}.png`; a.click(); };
      card.querySelector("[data-act='delete-qr']").onclick = async () => {
        if (!confirm("Delete this QR code and its content? Its printed code will stop working.")) return;
        try { await api(`/business/qr-codes/${code.id}`, { method: "DELETE" }); dashboardView(); } catch (ex) { err.textContent = ex.message; }
      };
      card.querySelectorAll(".item").forEach((el) => {
        const id = el.dataset.id, input = el.querySelector("[data-file]");
        const replace = el.querySelector("[data-act='replace']");
        if (replace) { replace.onclick = () => input.click(); input.onchange = async () => {
          if (!input.files.length) return; const form = new FormData(); form.append("file", input.files[0]);
          try { await api(`/content/${id}/file`, { method: "PUT", form }); dashboardView(); } catch (ex) { err.textContent = ex.message; }
        }; }
      });
    } catch (ex) { card.querySelector(".qr-items").innerHTML = `<p class="error">${esc(ex.message)}</p>`; }
  }
}

async function editorView(id) {
  const isNew = id === "new", params = new URLSearchParams(location.hash.split("?")[1] || "");
  const qrId = params.get("qr");
  let item = { type: "text", text_value: "", url_value: "" };
  if (!isNew) { try { item = await api(`/content/${id}`); } catch (_) { return go("/dashboard"); } }
  root.innerHTML = `<main class="shell wide"><form class="panel" id="editor"><h1>${isNew ? "Set destination" : "Update destination"}</h1>
    <label for="type">Content type</label><select id="type">${Object.entries(TYPE_LABEL).map(([v, l]) =>
      `<option value="${v}" ${item.type === v ? "selected" : ""}>${l}</option>`).join("")}</select>
    <div id="f-text"><label for="text">Text</label><textarea id="text">${esc(item.text_value)}</textarea></div>
    <div id="f-link"><label for="url">Link address</label><input id="url" type="url" placeholder="https://" value="${esc(item.url_value)}"></div>
    <div id="f-file"><label for="file">File</label><input id="file" type="file"><p class="hint" id="file-hint"></p></div>
    <p class="error" id="err"></p><button class="btn primary" type="submit">${isNew ? "Set destination" : "Update destination"}</button>
    <p class="switch"><a href="#/dashboard">Back to dashboard</a></p></form></main>`;
  const typeEl = document.getElementById("type"), fileEl = document.getElementById("file");
  const sync = () => { const t = typeEl.value;
    document.getElementById("f-text").classList.toggle("hidden", t !== "text"); document.getElementById("f-link").classList.toggle("hidden", t !== "link");
    document.getElementById("f-file").classList.toggle("hidden", t !== "image" && t !== "pdf"); fileEl.accept = t === "pdf" ? ".pdf" : "image/*";
    document.getElementById("file-hint").textContent = "Choose a file up to 10 MB.";
  };
  typeEl.onchange = sync; sync();
  document.getElementById("editor").onsubmit = async (e) => {
    e.preventDefault(); const err = document.getElementById("err"); err.textContent = "";
    const t = typeEl.value, form = new FormData();
    form.append("type", t);
    if (isNew) form.append("qr_code_id", qrId);
    if (t === "text") form.append("text_value", document.getElementById("text").value);
    if (t === "link") form.append("url_value", document.getElementById("url").value);
    if ((t === "image" || t === "pdf") && fileEl.files.length) form.append("file", fileEl.files[0]);
    try { await api(isNew ? "/content" : `/content/${id}`, { method: isNew ? "POST" : "PUT", form }); go("/dashboard"); }
    catch (ex) { err.textContent = ex.message; }
  };
}

function route() {
  const [path] = (location.hash.slice(1) || "/").split("?");
  const [, page, id] = path.split("/");
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
