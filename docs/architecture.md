# Architecture

```
Customer phone ──scan QR──▶ GET /q/{slug}  ──▶ latest link redirect or current file
                                                     │
Business owner ──▶ client (HTML/CSS/JS) ──▶ /api/*  ─┤──▶ SQLite (data.db)
                                                     └──▶ uploads/ (images, PDFs)
```

## Key idea
Each QR code encodes `BASE_URL/q/{slug}`. The slug is generated once and never
changes. A business can create many QR codes, each with its own content. The
Each QR has exactly one destination. Link QR codes redirect directly, while
image/PDF QR codes serve the current file. Updating that destination changes
what customers receive without reprinting.

## Components
- **client/**: static files served by FastAPI. `app.js` is a small single-page
  app (hash routes: `#/login`, `#/register`, `#/dashboard`, `#/editor/:id`).
  It only calls the JSON API.
- **functions/api/**: Python backend (FastAPI).
  - `main.py` wires routers, `/uploads` and the client.
  - `routes/auth.py` register and login (JWT).
  - `routes/business.py` profile, QR CRUD and QR PNG.
  - `routes/content.py` create, edit, replace file, delete.
  - `routes/public.py` direct QR destination responses (`/q/{slug}`).
  - `security.py` password hashing, tokens, auth dependency.
  - `db.py`, `config.py` storage and settings.
- **database/**: schema reference.

## Security notes
- Passwords: PBKDF2-SHA256 with a random salt.
- Every content query is filtered by `business_id`, so owners only touch their own rows.
- Uploads: extension allow-list, 10 MB limit, random stored names.
- Public page escapes all owner text. Links must start with `http://` or `https://`.
- Set `SECRET_KEY` and `BASE_URL` in production and serve over HTTPS.
