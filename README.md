# Dynamic QR Code Generator for Businesses

A business can create multiple permanent QR codes. Customers scan a code and
open its destination directly. The owner can change that code's text, offers, images,
PDFs and links at any time without reprinting it. Each QR code has one destination, such as a link or
menu image, and its stable URL always serves the latest destination.

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

## Settings (environment variables)
| Name | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Signs login tokens. Set a long random value | dev value |
| `BASE_URL` | Public address put in the QR code, e.g. `https://menu.example.com` | request host |
| `DB_PATH` | SQLite file | `functions/api/data.db` |
| `UPLOAD_DIR` | Where files are stored | `functions/api/uploads` |
| `MAX_UPLOAD_MB` | Upload limit | `10` |

Set `BASE_URL` before printing a QR code. The code contains this address.

## Deploy to Zoho Catalyst AppSail

This FastAPI app is deployed as a Catalyst-managed AppSail Python service.
From the repository root, install and authenticate the Catalyst CLI, then
initialize the project:

```bash
npm install -g zcatalyst-cli
catalyst auth:login
catalyst init
```

Choose the existing Catalyst project (or create one), select **AppSail**,
choose the **Catalyst-managed runtime**, and select **Python**. Set the
AppSail source directory to `functions/api`, then deploy:

```bash
catalyst deploy appsail
```

Configure these production environment variables in the Catalyst AppSail
settings before going live:

| Name | Required value |
|---|---|
| `SECRET_KEY` | Long random secret, at least 32 characters |
| `BASE_URL` | The public AppSail URL or your custom domain |
| `DB_PATH` | A persistent path if SQLite storage is used |
| `UPLOAD_DIR` | A persistent path for uploaded images/PDFs |

SQLite and local uploads must use persistent storage in production. If the
AppSail runtime does not provide persistent paths for these files, move the
database and uploads to a managed database and object storage before launch;
otherwise a restart can lose accounts or uploaded content.

## Docs
- `docs/architecture.md`
- `docs/api-documentation.md`
- `database/schema.md`
