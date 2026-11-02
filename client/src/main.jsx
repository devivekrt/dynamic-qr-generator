import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const TYPES = { text: "Text", link: "Link", image: "Image", pdf: "PDF" };

function useHash() {
  const [hash, setHash] = useState(window.location.hash || "#/dashboard");
  useEffect(() => {
    const change = () => setHash(window.location.hash || "#/dashboard");
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
  return hash;
}

function go(path) { window.location.hash = path; }

async function api(path, { method = "GET", body, form, blob = false } = {}) {
  const headers = {};
  const token = localStorage.getItem("token");
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload = body ? JSON.stringify(body) : undefined;
  if (body) headers["Content-Type"] = "application/json";
  if (form) payload = form;
  const response = await fetch(`/api${path}`, { method, headers, body: payload });
  if (response.status === 401 && token) {
    localStorage.removeItem("token");
    go("/login");
  }
  if (!response.ok) {
    let message = "Something went wrong. Try again.";
    try {
      const data = await response.json();
      if (typeof data.detail === "string") message = data.detail;
      if (Array.isArray(data.detail)) message = data.detail.map((item) => item.msg).join(". ");
    } catch {}
    throw new Error(message);
  }
  return blob ? response.blob() : response.status === 204 ? null : response.json();
}

function Layout({ children, onLogout }) {
  return <div className="app-shell"><header className="topbar">
    <a className="brand" href="#/dashboard"><span className="brand-mark">▦</span> QRevive</a>
    <span className="brand-tagline">Change the content, not the code.</span>
    <button className="button ghost" onClick={onLogout}>Log out</button>
  </header>{children}</div>;
}

function Field({ label, name, ...props }) {
  return <label className="field"><span>{label}</span><input name={name} {...props} /></label>;
}

function Auth({ register = false }) {
  const [error, setError] = useState("");
  const submit = async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const body = { email: form.get("email"), password: form.get("password") };
    if (register) body.business_name = form.get("business_name");
    try {
      const result = await api(`/auth/${register ? "register" : "login"}`, { method: "POST", body });
      localStorage.setItem("token", result.token);
      go("/dashboard");
    } catch (exception) { setError(exception.message); }
  };
  return <main className="auth-page"><form className="auth-card" onSubmit={submit}>
    <div className="auth-brand">QRevive</div><p className="auth-tagline">Change the content, not the code.</p>
    <span className="eyebrow">PERMANENT QR MANAGEMENT</span><h1>{register ? "Create your workspace" : "Welcome back"}</h1>
    <p className="muted">{register ? "Create QR codes that stay useful after you update them." : "Manage every destination from one place."}</p>
    {register && <Field label="Business name" name="business_name" minLength="2" required />}
    <Field label="Email" name="email" type="email" required /><Field label="Password" name="password" type="password" minLength={register ? 8 : 1} required />
    {error && <p className="error">{error}</p>}<button className="button primary wide" type="submit">{register ? "Create account" : "Log in"}</button>
    <p className="switch">{register ? "Already have an account?" : "New here?"} <a href={register ? "#/login" : "#/register"}>{register ? "Log in" : "Create an account"}</a></p>
  </form></main>;
}

function QrCard({ code, onDelete, onReplaceFile }) {
  const content = code.content;
  const action = content ? `#/editor/${content.id}` : `#/editor/new?qr=${code.id}`;
  const fileInputId = `replace-${code.id}`;
  return <article className="qr-card">
    <div className="card-heading"><div><h2>{code.name}</h2><span className="badge">{content ? TYPES[content.type] : "No destination"}</span></div>
      <button className="icon-button" title="Download QR" onClick={() => { const link = document.createElement("a"); link.href = code.image; link.download = `qr-${code.slug}.png`; link.click(); }}>↓</button>
    </div>
    <img className="qr-image" src={code.image} alt={`QR code for ${code.name}`} /><p className="url">{code.public_url}</p>
    <div className="card-actions"><a className="button ghost" href={code.public_url} target="_blank" rel="noreferrer">View</a><a className="button primary destination-button" href={action}>{content ? "Update destination" : "Set destination"}</a></div>
    {content ? <div className="content-row"><span className="type-icon">{content.type.toUpperCase()}</span><strong>{TYPES[content.type]}</strong>
      <div className="content-actions">
        {content.type === "text" && <a className="text-button" href={action}>Edit text</a>}
        {content.type === "link" && <a className="text-button" href={action}>Edit link</a>}
        {(content.type === "image" || content.type === "pdf") && <>
          <label className="text-button" htmlFor={fileInputId}>Replace file</label>
          <input id={fileInputId} className="visually-hidden" type="file" accept={content.type === "pdf" ? ".pdf" : "image/*"} onChange={(event) => event.target.files[0] && onReplaceFile(content.id, event.target.files[0])} />
        </>}
        <button className="text-button danger-text" onClick={() => onDelete(content.id)}>Delete</button>
      </div>
    </div> : <div className="empty-content">No content assigned yet.</div>}
  </article>;
}

function Dashboard({ onLogout }) {
  const [codes, setCodes] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const load = async () => {
    try {
      const result = await api("/business/qr-codes");
      const withContent = await Promise.all(result.map(async (code) => ({
        ...code,
        content: await api(`/content?qr_code_id=${code.id}`),
        image: URL.createObjectURL(await api(`/business/qr-codes/${code.id}/image`, { blob: true })),
      })));
      setCodes(withContent);
    } catch (exception) { setError(exception.message); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);
  const create = async (event) => {
    event.preventDefault();
    try { await api("/business/qr-codes", { method: "POST", body: { name: new FormData(event.currentTarget).get("name") } }); event.currentTarget.reset(); setLoading(true); await load(); }
    catch (exception) { setError(exception.message); }
  };
  const removeContent = async (id) => {
    if (!window.confirm("Delete this content? The QR code will remain available.")) return;
    try { await api(`/content/${id}`, { method: "DELETE" }); setLoading(true); await load(); }
    catch (exception) { setError(exception.message); }
  };
  const replaceFile = async (id, file) => {
    const form = new FormData();
    form.append("file", file);
    try { await api(`/content/${id}/file`, { method: "PUT", form }); setLoading(true); await load(); }
    catch (exception) { setError(exception.message); }
  };
  return <Layout onLogout={onLogout}><main className="dashboard">
    <section className="hero"><div><span className="eyebrow">WORKSPACE</span><h1>Your QR codes</h1><p className="muted">Print once. Update the destination whenever your business changes.</p></div>
      <form className="create-form" onSubmit={create}><input name="name" placeholder="QR name, e.g. Table 1" required maxLength="120" /><button className="button primary">Create QR</button></form>
    </section>
    {error && <p className="error banner">{error}</p>}
    {loading ? <div className="empty-state">Loading your QR codes…</div> : codes.length === 0 ? <div className="empty-state"><h2>Create your first QR code</h2><p>Each code gets a permanent address that you can update later.</p></div> :
      <section className="qr-grid">{codes.map((code) => <QrCard key={code.id} code={code} onDelete={removeContent} onReplaceFile={replaceFile} />)}</section>}
  </main></Layout>;
}

function Editor({ id, onLogout }) {
  const isNew = id === "new";
  const qrId = new URLSearchParams(window.location.hash.split("?")[1] || "").get("qr");
  const [item, setItem] = useState({ type: "text", text_value: "", url_value: "" });
  const [error, setError] = useState("");
  useEffect(() => { if (!isNew) api(`/content/${id}`).then(setItem).catch(() => go("/dashboard")); }, [id, isNew]);
  const submit = async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    if (isNew) form.append("qr_code_id", qrId);
    try { await api(isNew ? "/content" : `/content/${id}`, { method: isNew ? "POST" : "PUT", form }); go("/dashboard"); }
    catch (exception) { setError(exception.message); }
  };
  return <Layout onLogout={onLogout}><main className="editor-page"><form className="editor-card" onSubmit={submit}>
    <span className="eyebrow">{isNew ? "NEW DESTINATION" : "EDIT DESTINATION"}</span><h1>{isNew ? "Set destination" : "Update destination"}</h1><p className="muted">Your QR code stays the same while this destination changes.</p>
    <label className="field"><span>Content type</span><select name="type" value={item.type} onChange={(event) => setItem({ ...item, type: event.target.value })}>{Object.entries(TYPES).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
    {item.type === "text" && <label className="field"><span>Text</span><textarea name="text_value" value={item.text_value || ""} onChange={(event) => setItem({ ...item, text_value: event.target.value })} required /></label>}
    {item.type === "link" && <Field label="Link address" name="url_value" type="url" value={item.url_value || ""} onChange={(event) => setItem({ ...item, url_value: event.target.value })} placeholder="https://" required />}
    {(item.type === "image" || item.type === "pdf") && <label className="field"><span>{isNew ? "Choose file" : "Replace file"}</span><input name="file" type="file" accept={item.type === "pdf" ? ".pdf" : "image/*"} required={isNew} /></label>}
    {error && <p className="error">{error}</p>}<button className="button primary wide" type="submit">{isNew ? "Set destination" : "Update destination"}</button><a className="back-link" href="#/dashboard">Back to dashboard</a>
  </form></main></Layout>;
}

function App() {
  const hash = useHash();
  const [, page, id] = hash.replace(/^#/, "").split("/");
  const loggedIn = Boolean(localStorage.getItem("token"));
  const logout = () => { localStorage.removeItem("token"); go("/login"); };
  if (page === "login") return <Auth />;
  if (page === "register") return <Auth register />;
  if (!loggedIn) { go("/login"); return null; }
  if (page === "editor" && id) return <Editor id={id} onLogout={logout} />;
  return <Dashboard onLogout={logout} />;
}

createRoot(document.getElementById("root")).render(<App />);
