# Architecture

```
Customer phone ──scan QR──▶ GET /b/{slug}  ──▶ FastAPI renders the public page (HTML)
                                                     │
Business owner ──▶ client (HTML/CSS/JS) ──▶ /api/*  ─┤──▶ SQLite (data.db)
                                                     └──▶ uploads/ (images, PDFs)
```

## Key idea
The QR code encodes `BASE_URL/b/{slug}`. The slug is fixed when the account is
created, so the printed code never changes. The page behind it is built from the
database on every request, so edits appear immediately.

## Components
- **client/**: static files served by FastAPI. `app.js` is a small single-page
  app (hash routes: `#/login`, `#/register`, `#/dashboard`, `#/editor/:id`).
  It only calls the JSON API.
- **functions/api/**: Python backend (FastAPI).
  - `main.py` wires routers, `/uploads` and the client.
  - `routes/auth.py` register and login (JWT).
  - `routes/business.py` profile and QR PNG.
  - `routes/content.py` create, edit, replace file, delete.
  - `routes/public.py` public page (`/b/{slug}`) and public JSON.
  - `security.py` password hashing, tokens, auth dependency.
  - `db.py`, `config.py` storage and settings.
- **database/**: schema reference.

## Security notes
- Passwords: PBKDF2-SHA256 with a random salt.
- Every content query is filtered by `business_id`, so owners only touch their own rows.
- Uploads: extension allow-list, 10 MB limit, random stored names.
- Public page escapes all owner text. Links must start with `http://` or `https://`.
- Set `SECRET_KEY` and `BASE_URL` in production and serve over HTTPS.
