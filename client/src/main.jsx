import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const TYPES = { text: "Text", link: "Link", image: "Image", pdf: "PDF" };
const DESIGN_LABELS = {
  basic: "Basic square",
  "basic-soft": "Basic soft",
  "basic-contrast": "Basic contrast",
  "prime-rounded": "Prime rounded",
  "prime-dots": "Prime dots",
  "prime-frame": "Prime frame",
  "business-rounded": "Business rounded",
  "business-gradient": "Business gradient",
  "business-frame": "Business frame",
};
const landingFeatures = [
  ["↗", "Dynamic links", "Change your destination URL whenever you need. Your printed QR code stays the same."],
  ["▤", "Editable text", "Share announcements, instructions, and information that you can update anytime."],
  ["▧", "Images & PDFs", "Replace menus, brochures, catalogs, and documents without reprinting."],
  ["◉", "Permanent QR codes", "Create one QR code and keep using it for your business over time."],
];
const landingSteps = [
  ["01", "Sign up", "Create an account and log in."],
  ["02", "Create QR code", "Generate a new QR code."],
  ["03", "Set destination", "Choose a link, text, image, or PDF."],
  ["04", "Download & print", "Use your QR code anywhere."],
  ["05", "Update anytime", "Change content without changing the code."],
];
const useCases = [
  ["⌂", "Businesses", "Update menus, offers, or announcements anytime."],
  ["□", "Events", "Change event details, schedules, or brochures."],
  ["◇", "Education", "Share and update study materials or notices."],
  ["◈", "Marketing", "Run flexible campaigns with one QR code."],
  ["▤", "Documents", "Share and replace PDFs like catalogs or forms."],
];

function usePath() {
  const [path, setPath] = useState(`${window.location.pathname}${window.location.search}`);
  useEffect(() => {
    const change = () => setPath(`${window.location.pathname}${window.location.search}`);
    window.addEventListener("popstate", change);
    return () => window.removeEventListener("popstate", change);
  }, []);
  return path;
}

function go(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function Landing() {
  return <div className="landing">
    <header className="landing-nav">
      <a className="landing-logo" href="/"><span className="landing-mark">Q</span> QRevive</a>
      <nav><a href="#landing-features">Features</a><a href="#landing-how">How It Works</a><a href="#landing-use-cases">Use Cases</a><a href="#landing-pricing">Pricing</a></nav>
      <div className="landing-actions"><a href="/login">Log in</a><a className="landing-button small" href="/register">Get started free <span>↗</span></a></div>
    </header>
    <main>
      <section className="landing-hero">
        <div className="landing-hero-copy">
          <span className="landing-eyebrow"><i /> SMART QR CODES FOR YOUR BUSINESS</span>
          <h1>One QR Code.<br />Update <em>Anytime.</em></h1>
          <p>Create permanent QR codes and change their destination anytime — links, text, images, or PDFs — without printing a new one.</p>
          <div className="landing-hero-actions"><a className="landing-button" href="/register">Create your QR code <span>→</span></a><a className="landing-button outline" href="#landing-how">▷ &nbsp; Watch demo</a></div>
          <div className="landing-checks"><span>✓ Permanent QR Codes</span><span>✓ Update Anytime</span><span>✓ Multiple Content Types</span></div>
        </div>
        <div className="landing-visual"><div className="landing-glow" /><div className="demo-qr-card">
          <div className="demo-qr-top"><strong><span className="landing-mark mini">Q</span> QRevive</strong><span>● Dynamic</span></div>
          <div className="demo-qr-pattern">{Array.from({ length: 121 }, (_, index) => <i key={index} className={(index % 7 === 0 || index % 11 === 0 || [0, 1, 2, 10, 11, 12, 108, 109, 110, 118, 119, 120].includes(index)) ? "on" : ""} />)}</div>
          <div className="demo-qr-bottom"><strong>Your QR code is ready<small>Scan to see your destination</small></strong><b>✓</b></div>
          <span className="demo-badge one">↻ &nbsp; Update anytime</span><span className="demo-badge two">✓ &nbsp; Never reprint</span>
        </div></div>
      </section>
      <div className="landing-trust"><strong>ONE QR CODE. ENDLESS POSSIBILITIES.</strong><div><span>↗ Website links</span><span>▤ Text content</span><span>▧ Images</span><span>▣ PDF documents</span></div></div>
      <section id="landing-features" className="landing-section"><div className="landing-heading"><label>WHY QREVIVE</label><h2>Your QR code stays.<br /><em>Your content evolves.</em></h2><p>Stop wasting time and money printing new QR codes. Keep your content fresh with one simple dashboard.</p></div><div className="landing-feature-grid">{landingFeatures.map(([icon, title, description]) => <article key={title}><b>{icon}</b><h3>{title}</h3><p>{description}</p><a href="/register">Learn more →</a></article>)}</div></section>
      <section id="landing-how" className="landing-section tinted"><div className="landing-heading"><label>SIMPLE BY DESIGN</label><h2>How It <em>Works</em></h2><p>Create and manage dynamic QR codes in just a few simple steps.</p></div><div className="landing-steps">{landingSteps.map(([number, title, description], index) => <article key={number}><strong>{number}</strong>{index < 4 && <i>→</i>}<h3>{title}</h3><p>{description}</p></article>)}</div></section>
      <section id="landing-use-cases" className="landing-section"><div className="landing-heading"><label>BUILT FOR EVERY BUSINESS</label><h2>Use <em>Cases</em></h2><p>A simple solution for many real-world needs.</p></div><div className="landing-use-grid">{useCases.map(([icon, title, description]) => <article key={title}><b>{icon}</b><h3>{title}</h3><p>{description}</p></article>)}</div></section>
      <section id="landing-pricing" className="landing-section tinted"><div className="landing-heading"><label>SIMPLE PRICING</label><h2>Simple, Flexible <em>Pricing</em></h2><p>Choose a plan that fits your needs and make every QR code look your way.</p></div><div className="landing-pricing-grid"><Price title="Free" price="₹0" detail="Get started at no cost." features={["Up to 5 dynamic QR codes", "2–3 basic pattern templates", "Basic destination updates"]} /><Price title="Prime" price="₹299" detail="For growing businesses." popular features={["Up to 50 dynamic QR codes", "3 designed templates with 5–10 pattern styles", "Analytics & scan insights", "Custom branding", "Priority support"]} /><Price title="Business" price="₹799" detail="For teams and larger needs." features={["Up to 250 dynamic QR codes", "Advanced templates & logo support", "Team access", "Advanced analytics", "Priority support"]} /><Price title="Custom Enterprise" price="Custom" detail="For larger organizations." features={["Custom QR code limits", "Bespoke templates and branding", "Team access and advanced analytics", "Dedicated priority support"]} /></div></section>
      <section className="landing-cta"><div><h2>Create Your <em>Dynamic QR Code</em> Today</h2><p>Update content anytime and keep the same QR code forever.</p></div><a className="landing-button white" href="/register">Get started free →</a></section>
    </main>
    <footer className="landing-footer"><a className="landing-logo" href="/"><span className="landing-mark">Q</span> QRevive</a><p>Change the content, not the code.</p><div><a href="#landing-features">Features</a><a href="#landing-pricing">Pricing</a><a href="/login">Login</a><a href="/register">Get started</a></div><small>© {new Date().getFullYear()} QRevive. All rights reserved.</small></footer>
  </div>;
}

function Price({ title, price, detail, features, popular }) {
  const action = popular ? "Upgrade to Prime" : title === "Business" || title === "Custom Enterprise" ? "Contact sales" : "Get started";
  return <article className={`landing-price ${popular ? "popular" : ""}`}>{popular && <span className="popular-label">Most Popular</span>}<h3>{title}</h3><p>{detail}</p><strong>{price}{price !== "Custom" && <small>/month</small>}</strong><ul>{features.map((feature) => <li key={feature}>✓ {feature}</li>)}</ul><a className="landing-button outline" href="/register">{action}</a></article>;
}

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
      const data = JSON.parse(await response.text());
      if (typeof data.detail === "string") message = data.detail;
      if (Array.isArray(data.detail)) message = data.detail.map((item) => item.msg).join(". ");
    } catch {}
    throw new Error(message);
  }
  if (blob) return response.blob();
  if (response.status === 204) return null;
  const text = await response.text();
  if (!text.trim()) return null;
  try {
    return JSON.parse(text);
  } catch {
    throw new Error("The server completed the request but returned an invalid response.");
  }
}

function Layout({ children, onLogout }) {
  return <div className="app-shell"><header className="topbar">
    <a className="brand" href="/dashboard"><span className="brand-mark">▦</span> QRevive</a>
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
      let result = await api(`/auth/${register ? "register" : "login"}`, { method: "POST", body });
      if (register && !result?.token) {
        result = await api("/auth/login", {
          method: "POST",
          body: { email: body.email, password: body.password },
        });
      }
      if (!result?.token) throw new Error("Account was created, but the session could not be started. Please log in.");
      localStorage.setItem("token", result.token);
      go("/dashboard");
    } catch (exception) {
      if (register) {
        try {
          const result = await api("/auth/login", {
            method: "POST",
            body: { email: body.email, password: body.password },
          });
          if (result?.token) {
            localStorage.setItem("token", result.token);
            go("/dashboard");
            return;
          }
        } catch {}
      }
      setError(exception.message);
    }
  };
  return <main className="auth-page"><form className="auth-card" onSubmit={submit}>
    <div className="auth-brand">QRevive</div><p className="auth-tagline">Change the content, not the code.</p>
    <span className="eyebrow">PERMANENT QR MANAGEMENT</span><h1>{register ? "Create your workspace" : "Welcome back"}</h1>
    <p className="muted">{register ? "Create QR codes that stay useful after you update them." : "Manage every destination from one place."}</p>
    {register && <Field label="Business name" name="business_name" minLength="2" required />}
    <Field label="Email" name="email" type="email" required /><Field label="Password" name="password" type="password" minLength={register ? 8 : 1} required />
    {error && <p className="error">{error}</p>}<button className="button primary wide" type="submit">{register ? "Create account" : "Log in"}</button>
    <p className="switch">{register ? "Already have an account?" : "New here?"} <a href={register ? "/login" : "/register"}>{register ? "Log in" : "Create an account"}</a></p>
  </form></main>;
}

function DesignPanel({ code, business, onSaved, onCancel }) {
  const [template, setTemplate] = useState(code.design?.DESIGN_TEMPLATE || "basic");
  const [foreground, setForeground] = useState(code.design?.FOREGROUND_COLOR || "#111827");
  const [background, setBackground] = useState(code.design?.BACKGROUND_COLOR || "#FFFFFF");
  const [eyeStyle, setEyeStyle] = useState(code.design?.EYE_STYLE || "square");
  const [frameStyle, setFrameStyle] = useState(code.design?.FRAME_STYLE || "none");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const save = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api(`/business/qr-codes/${code.id}/design`, { method: "PUT", form: new FormData(event.currentTarget) });
      await onSaved();
    } catch (exception) {
      setError(exception.message);
    } finally {
      setSaving(false);
    }
  };
  return <form className="design-panel" onSubmit={save}>
    <div className="design-panel-heading"><strong>Design QR code</strong><button type="button" className="text-button" onClick={onCancel}>Close</button></div>
    <label className="field"><span>Template</span><select name="template" value={template} onChange={(event) => setTemplate(event.target.value)}>{(business?.design_templates || ["basic"]).map((value) => <option key={value} value={value}>{DESIGN_LABELS[value] || value}</option>)}</select></label>
    <div className="design-colors">
      <label className="field"><span>Foreground</span><input name="foreground_color" type="color" value={foreground} disabled={!business?.allow_custom_colors} onChange={(event) => setForeground(event.target.value)} /></label>
      <label className="field"><span>Background</span><input name="background_color" type="color" value={background} disabled={!business?.allow_custom_colors} onChange={(event) => setBackground(event.target.value)} /></label>
    </div>
    <label className="field"><span>Corner style</span><select name="eye_style" value={eyeStyle} onChange={(event) => setEyeStyle(event.target.value)}><option value="square">Square</option><option value="rounded">Rounded</option></select></label>
    <label className="field"><span>Frame</span><select name="frame_style" value={frameStyle} onChange={(event) => setFrameStyle(event.target.value)}><option value="none">None</option><option value="label">Border frame</option></select></label>
    <label className="field"><span>Logo {business?.allow_logo ? "(optional)" : "(Business plan)"}</span><input name="logo" type="file" accept="image/png,image/jpeg,image/webp" disabled={!business?.allow_logo} /></label>
    {!business?.allow_custom_colors && <p className="design-note">Upgrade to Prime to unlock custom colors.</p>}
    {!business?.allow_logo && <p className="design-note">Upgrade to Business to add a logo.</p>}
    {error && <p className="error">{error}</p>}
    <button className="button primary wide" type="submit" disabled={saving}>{saving ? "Saving design…" : "Save design"}</button>
  </form>;
}

function QrCard({ code, business, onDelete, onDeleteQr, onReplaceFile, onDesignSaved }) {
  const content = code.content;
  const action = content ? `/editor/${content.id}` : `/editor/new?qr=${code.id}`;
  const fileInputId = `replace-${code.id}`;
  const [designing, setDesigning] = useState(false);
  return <article className="qr-card">
    <div className="card-heading"><div><h2>{code.name}</h2><span className="badge">{content ? TYPES[content.type] : "No destination"}</span></div>
      <button className="icon-button" title="Download QR" onClick={() => { const link = document.createElement("a"); link.href = code.image; link.download = `qr-${code.slug}.png`; link.click(); }}>↓</button>
    </div>
    <img className="qr-image" src={code.image} alt={`QR code for ${code.name}`} /><p className="url">{code.public_url}</p>
    <div className="card-actions"><a className="button ghost" href={code.public_url} target="_blank" rel="noreferrer">View</a><a className="button primary destination-button" href={action}>{content ? "Update destination" : "Set destination"}</a></div>
    <button className="text-button design-button" onClick={() => setDesigning((value) => !value)}>{designing ? "Close design" : "Design QR"}</button>
    {designing && <DesignPanel code={code} business={business} onCancel={() => setDesigning(false)} onSaved={async () => { setDesigning(false); await onDesignSaved(); }} />}
    <button className="text-button danger-text qr-delete-button" onClick={() => onDeleteQr(code.id, code.name)}>Delete QR code</button>
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
  const [business, setBusiness] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const load = async () => {
    try {
      const [profile, result] = await Promise.all([api("/business/me"), api("/business/qr-codes")]);
      setBusiness(profile);
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
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    try { await api("/business/qr-codes", { method: "POST", body: { name: form.get("name") } }); formElement.reset(); setLoading(true); await load(); }
    catch (exception) { setError(exception.message); }
  };
  const removeContent = async (id) => {
    if (!window.confirm("Delete this content? The QR code will remain available.")) return;
    try { await api(`/content/${id}`, { method: "DELETE" }); setLoading(true); await load(); }
    catch (exception) { setError(exception.message); }
  };
  const removeQr = async (id, name) => {
    if (!window.confirm(`Delete "${name}" and its destination? This cannot be undone.`)) return;
    try { await api(`/business/qr-codes/${id}`, { method: "DELETE" }); setLoading(true); await load(); }
    catch (exception) { setError(exception.message); }
  };
  const replaceFile = async (id, file) => {
    const form = new FormData();
    form.append("file", file);
    try { await api(`/content/${id}/file`, { method: "PUT", form }); setLoading(true); await load(); }
    catch (exception) { setError(exception.message); }
  };
  const reload = async () => { setLoading(true); await load(); };
  return <Layout onLogout={onLogout}><main className="dashboard">
    <section className="hero"><div><span className="eyebrow">WORKSPACE · {business?.plan_label || "Free"} PLAN</span><h1>Your QR codes</h1><p className="muted">Print once. Update the destination whenever your business changes.</p>{business && <p className="plan-meter">{codes.length} of {business.qr_limit} QR codes used</p>}</div>
      <form className="create-form" onSubmit={create}><input name="name" placeholder="QR name, e.g. Table 1" required maxLength="120" /><button className="button primary">Create QR</button></form>
    </section>
    {error && <p className="error banner">{error}</p>}
    {loading ? <div className="empty-state">Loading your QR codes…</div> : codes.length === 0 ? <div className="empty-state"><h2>Create your first QR code</h2><p>Each code gets a permanent address that you can update later.</p></div> :
      <section className="qr-grid">{codes.map((code) => <QrCard key={code.id} code={code} business={business} onDelete={removeContent} onDeleteQr={removeQr} onReplaceFile={replaceFile} onDesignSaved={reload} />)}</section>}
  </main></Layout>;
}

function Editor({ id, onLogout }) {
  const isNew = id === "new";
  const qrId = new URLSearchParams(window.location.search).get("qr");
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
    {error && <p className="error">{error}</p>}<button className="button primary wide" type="submit">{isNew ? "Set destination" : "Update destination"}</button><a className="back-link" href="/dashboard">Back to dashboard</a>
  </form></main></Layout>;
}

function App() {
  const path = usePath();
  const [, page, id] = path.split(/[/?]/);
  const loggedIn = Boolean(localStorage.getItem("token"));
  const logout = () => { localStorage.removeItem("token"); go("/login"); };
  const landingRoute = !page || page === "";
  if (landingRoute) return <Landing />;
  if (page === "login") return <Auth />;
  if (page === "register") return <Auth register />;
  if (!loggedIn) { go("/login"); return null; }
  if (page === "editor" && id) return <Editor id={id} onLogout={logout} />;
  return <Dashboard onLogout={logout} />;
}

const root = window.__qreviveRoot || createRoot(document.getElementById("root"));
window.__qreviveRoot = root;
root.render(<App />);
