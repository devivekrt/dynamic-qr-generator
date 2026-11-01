# Database schema (SQLite)

The tables are created automatically on startup by `functions/api/db.py`.

## businesses
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | One row per QR code |
| name | TEXT | Business name shown on the public page |
| email | TEXT UNIQUE | Stored lower-case |
| password_hash | TEXT | PBKDF2-SHA256, `salt$hash` |
| slug | TEXT UNIQUE | Permanent public id, e.g. `blue-cafe-3fa9` |
| created_at | TEXT | ISO 8601 UTC |

## contents
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| business_id | INTEGER FK | `ON DELETE CASCADE` |
| title | TEXT | |
| type | TEXT | `text`, `link`, `image`, `pdf` |
| text_value | TEXT | Used by `text` |
| url_value | TEXT | Used by `link` (http/https only) |
| file_name | TEXT | Stored name in `uploads/` (image, pdf) |
| original_name | TEXT | Name the owner uploaded |
| created_at / updated_at | TEXT | ISO 8601 UTC |

## qr_codes
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| business_id | INTEGER FK | `ON DELETE CASCADE` |
| name | TEXT | Owner-facing QR name |
| slug | TEXT UNIQUE | Permanent public id used by the printed QR |
| created_at | TEXT | ISO 8601 UTC |

Each content item belongs to one `qr_codes.id` through `contents.qr_code_id`.
Only one content item is allowed for each QR code. Link QR codes redirect
directly to their current URL; image and PDF QR codes serve their current file.
