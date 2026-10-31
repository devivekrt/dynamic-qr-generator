# Dynamic QR Code Generator for Businesses

A business creates one permanent QR code. Customers scan it and open a public
page. The owner can change menus, offers, images, PDFs and links at any time
without reprinting the code.

Backend: Python (FastAPI + SQLite). Frontend: static HTML, CSS and a small
`app.js` (browsers cannot run Python, so the client script stays JavaScript).

## Run locally
```bash
cd functions/api
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Open http://127.0.0.1:8000, create an account, add content, download the QR code.

## Test locally
```bash
cd functions/api
pytest -q
```

The health endpoint is available at `GET /api/health` and returns a small JSON
response suitable for deployment checks.

## Settings (environment variables)
| Name | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Signs login tokens. Set a long random value | dev value |
| `BASE_URL` | Public address put in the QR code, e.g. `https://menu.example.com` | request host |
| `DB_PATH` | SQLite file | `functions/api/data.db` |
| `UPLOAD_DIR` | Where files are stored | `functions/api/uploads` |
| `MAX_UPLOAD_MB` | Upload limit | `10` |

Set `BASE_URL` before printing a QR code. The code contains this address.

## Docs
- `docs/architecture.md`
- `docs/api-documentation.md`
- `database/schema.md`
