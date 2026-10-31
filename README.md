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

## Deploy with Zoho Catalyst AppSail

This project is a Python FastAPI web application, so deploy the `functions/api`
directory as an **AppSail** service. The included
`functions/api/app-config.json` starts Uvicorn on Catalyst's assigned port.

```bash
npm install -g zcatalyst-cli
catalyst login
cd functions/api
pip install -r requirements.txt
catalyst deploy
```

After deployment, open the AppSail service URL and verify:

1. `/api/health` returns `{"status":"ok","service":"dynamic-qr-generator"}`.
2. The home page loads.
3. You can register, log in, add text content, and open the public page.

Set these AppSail environment variables before using a production QR code:

```text
SECRET_KEY=<long-random-secret>
BASE_URL=https://<your-appsail-domain>
ENVIRONMENT=production
```

SQLite and local uploads are suitable for a test deployment. For production,
use a managed database and object storage; local AppSail disk is not a durable
storage layer. Production startup fails unless `SECRET_KEY` is at least 32
characters and `BASE_URL` uses HTTPS.

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
