# Dynamic QR Code Generator — Catalyst Data Store schema

The backend uses the exact uppercase column names below.

For the production design and plan features, add the new nullable columns to the
existing Catalyst tables before deploying the updated AppSail service. Existing
businesses without `PLAN` are treated as Free accounts, and existing QR codes
without design values use the default basic design.

## Businesses

| Column | Type |
|---|---|
| `EMAIL` | text |
| `CREATED_AT` | text |
| `BUSINESS_NAME` | varchar |
| `PASSWORD_HASH` | text (not encrypted; stores the PBKDF2 hash only) |
| `SLUG` | varchar |
| `PLAN` | varchar (`free`, `prime`, `business`, or `enterprise`; defaults to `free` in the app) |

Catalyst system columns such as `ROWID`, `CREATORID`, `CREATEDTIME`, and
`MODIFIEDTIME` are generated automatically.

## QrCodes

| Column | Type |
|---|---|
| `BUSINESS_ID` | foreign key to Businesses |
| `QR_NAME` | varchar |
| `SLUG` | varchar |
| `DESIGN_TEMPLATE` | varchar |
| `FOREGROUND_COLOR` | varchar |
| `BACKGROUND_COLOR` | varchar |
| `EYE_STYLE` | varchar |
| `FRAME_STYLE` | varchar |
| `LOGO_FILE_ID` | varchar |
| `LOGO_FILE_NAME` | varchar |

## Contents

Each QR code has one destination record.

| Column | Type |
|---|---|
| `QR_CODE_ID` | foreign key to QrCodes |
| `TYPE` | varchar |
| `TEXT_VALUE` | text |
| `URL_VALUE` | varchar |
| `FILE_NAME` | varchar |
| `FILE_ID` | varchar |

For `TYPE=link`, `URL_VALUE` is used. For `TYPE=image` or `TYPE=pdf`,
`FILE_ID` and `FILE_NAME` identify the Catalyst File Store object. For
`TYPE=text`, `TEXT_VALUE` is used.
