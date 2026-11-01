# API documentation

Interactive docs are also available at `/docs` when the server runs.
Owner endpoints need the header `Authorization: Bearer <token>`.

## Auth
| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/api/auth/register` | JSON `business_name`, `email`, `password` (8+ chars) | `201 {token, business_name}` |
| POST | `/api/auth/login` | JSON `email`, `password` | `{token, business_name}` |

## Business (auth)
| Method | Path | Response |
|---|---|---|
| GET | `/api/business/me` | `{id, name, email, slug}` |
| GET | `/api/business/qr-codes` | List the owner's QR codes and permanent public URLs |
| POST | `/api/business/qr-codes` | JSON `{name}` | Create a QR code |
| GET | `/api/business/qr-codes/{id}/image` | PNG image. Add `?download=1` to force a download |
| DELETE | `/api/business/qr-codes/{id}` | Deletes the QR and its content |

## Content (auth, form-data)
| Method | Path | Fields | Notes |
|---|---|---|---|
| GET | `/api/content?qr_code_id={id}` | | List content for one QR code |
| GET | `/api/content/{id}` | | One item |
| POST | `/api/content` | `qr_code_id`, `title`, `type`, `text_value` or `url_value` or `file` | `201` |
| PUT | `/api/content/{id}` | `title`, `text_value` / `url_value`, optional `file` | Type cannot change |
| PUT | `/api/content/{id}/file` | `file` | Replace image or PDF |
| DELETE | `/api/content/{id}` | | `204`, removes the stored file |

## Public (no login)
| Method | Path | Response |
|---|---|---|
| GET | `/q/{slug}` | HTML page for customers (the QR target) |
| GET | `/api/public/{slug}` | `{business_name, content}` |
| GET | `/uploads/{file}` | Uploaded image or PDF |

## Errors
Errors return `{"detail": "message"}` with status 401, 404, 409, 413 or 422.
