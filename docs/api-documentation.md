# API documentation

Interactive docs are available at `/docs`.
Owner endpoints use `Authorization: Bearer <token>`.

## Auth
| Method | Path | Body |
|---|---|---|
| POST | `/api/auth/register` | JSON `business_name`, `email`, `password` |
| POST | `/api/auth/login` | JSON `email`, `password` |

## Business
| Method | Path | Notes |
|---|---|---|
| GET | `/api/business/me` | Current business |
| GET | `/api/business/qr-codes` | List owned QR codes |
| POST | `/api/business/qr-codes` | JSON `{name}` |
| GET | `/api/business/qr-codes/{id}/image` | QR PNG |
| DELETE | `/api/business/qr-codes/{id}` | Deletes QR and its destination |

## Content
Each QR code has one content record.

| Method | Path | Fields |
|---|---|---|
| GET | `/api/content?qr_code_id={id}` | |
| GET | `/api/content/{id}` | |
| POST | `/api/content` | `qr_code_id`, `type`, destination value/file |
| PUT | `/api/content/{id}` | `type` and updated destination value/file |
| PUT | `/api/content/{id}/file` | Replacement image/PDF |
| DELETE | `/api/content/{id}` | |

## Public
| Method | Path | Behavior |
|---|---|---|
| GET | `/q/{slug}` | Direct link redirect, text, image, or PDF |
| GET | `/api/public/{slug}` | QR metadata and current destination |
| GET | `/files/{file_id}` | File Store file response |
