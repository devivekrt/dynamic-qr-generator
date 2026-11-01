# Dynamic QR Code Generator — Catalyst Data Store schema

The backend uses the exact uppercase column names below.

## Businesses

| Column | Type |
|---|---|
| `EMAIL` | text |
| `CREATED_AT` | text |
| `BUSINESS_NAME` | varchar |
| `PASSWORD_HASH` | encrypted text |
| `SLUG` | varchar |

Catalyst system columns such as `ROWID`, `CREATORID`, `CREATEDTIME`, and
`MODIFIEDTIME` are generated automatically.

## QrCodes

| Column | Type |
|---|---|
| `BUSINESS_ID` | foreign key to Businesses |
| `QR_NAME` | varchar |
| `SLUG` | varchar |

## Contents

Each QR code has one destination record.

| Column | Type |
|---|---|
| `QR_CODE_ID` | foreign key to QrCodes |
| `TITLE` | varchar |
| `TYPE` | varchar |
| `TEXT_VALUE` | text |
| `URL_VALUE` | varchar |
| `FILE_NAME` | varchar |
| `FILE_ID` | varchar |

For `TYPE=link`, `URL_VALUE` is used. For `TYPE=image` or `TYPE=pdf`,
`FILE_ID` and `FILE_NAME` identify the Catalyst File Store object. For
`TYPE=text`, `TEXT_VALUE` is used.
