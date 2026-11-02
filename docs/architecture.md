# Architecture

```
Customer phone ──scan QR──▶ GET /q/{slug}  ──▶ latest link redirect or current file
                                                     │
Business owner ──▶ React/Vite client ──▶ /api/*  ────┤──▶ Catalyst Data Store
                                                     └──▶ Catalyst File Store (images, PDFs)
```

## Key idea
Each QR code encodes `BASE_URL/q/{slug}`. The slug is generated once and never
changes. A business can create many QR codes, each with its own content. The
Each QR has exactly one destination. Link QR codes redirect directly, while
image/PDF QR codes serve the current file. Updating that destination changes
what customers receive without reprinting.

## Components
- **client/**: React/Vite source application. `npm run build` writes the
  production bundle to `functions/api/client`, which FastAPI serves.
  Hash routes include `#/login`, `#/register`, `#/dashboard`, and
  `#/editor/:id`.
- **functions/api/**: Python backend (FastAPI).
  - `main.py` wires routers and the client.
  - `routes/auth.py` register and login (JWT).
  - `routes/business.py` profile, QR CRUD and QR PNG.
  - `routes/content.py` create, edit, replace file, delete.
  - `routes/public.py` direct QR destination responses (`/q/{slug}`).
  - `security.py` password hashing, tokens, auth dependency.
  - `catalyst_store.py`, `config.py` Catalyst storage and settings.
- **database/**: Catalyst Data Store schema reference.

## Security notes
- Passwords: PBKDF2-SHA256 with a random salt.
- Every content query is filtered by `business_id`, so owners only touch their own rows.
- Uploads: extension allow-list, 10 MB limit, random stored names.
- Public page escapes all owner text. Links must start with `http://` or `https://`.
- Set `SECRET_KEY` and `BASE_URL` in production and serve over HTTPS.
