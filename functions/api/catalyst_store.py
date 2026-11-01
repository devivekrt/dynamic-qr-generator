import io
import os
from datetime import datetime, timezone
from typing import Optional

import zcatalyst_sdk

from fastapi import HTTPException, Request

BUSINESSES = os.getenv("APP_BUSINESSES_TABLE", "Businesses")
QR_CODES = os.getenv("APP_QR_CODES_TABLE", "QrCodes")
CONTENTS = os.getenv("APP_CONTENTS_TABLE", "Contents")
FOLDER_ID = os.getenv("FILESTORE_FOLDER_ID", "")


def app_for(request: Request):
    catalyst = getattr(request.state, "catalyst", None)
    if catalyst is None:
        if not os.getenv("X_ZOHO_CATALYST_LISTEN_PORT"):
            raise RuntimeError(
                "Catalyst storage is available only in AppSail. "
                "Deploy this service to Catalyst or provide valid Catalyst credentials."
            )
        catalyst = zcatalyst_sdk.initialize(req=request)
        request.state.catalyst = catalyst
    return catalyst


def table(request: Request, name: str):
    return app_for(request).datastore().table(name)


def all_rows(request: Request, name: str) -> list[dict]:
    service = table(request, name)
    rows = []
    token = None
    while True:
        result = service.get_paged_rows(token, max_rows=100)
        rows.extend(result.get("rows", []))
        if not result.get("more_records"):
            return rows
        token = result.get("next_token")


def row_id(row: dict) -> str:
    return str(row.get("ROWID") or row.get("rowid") or row.get("id"))


def find_one(request: Request, name: str, predicate) -> Optional[dict]:
    return next((row for row in all_rows(request, name) if predicate(row)), None)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert(request: Request, name: str, values: dict) -> dict:
    return table(request, name).insert_row(values)


def update(request: Request, name: str, values: dict) -> dict:
    return table(request, name).update_row(values)


def delete(request: Request, name: str, identifier: str) -> None:
    table(request, name).delete_row(identifier)


def get_owned_qr(request: Request, qr_id: str, business_id: str) -> dict:
    row = find_one(request, QR_CODES, lambda r: row_id(r) == qr_id and str(r.get("business_id")) == business_id)
    if row is None:
        raise HTTPException(404, "QR code not found")
    return row


def get_owned_content(request: Request, content_id: str, business_id: str) -> dict:
    row = find_one(request, CONTENTS, lambda r: row_id(r) == content_id and str(r.get("business_id")) == business_id)
    if row is None:
        raise HTTPException(404, "Content not found")
    return row


def upload_file(request: Request, filename: str, data: bytes) -> str:
    if not FOLDER_ID:
        raise RuntimeError("FILESTORE_FOLDER_ID is not configured")
    folder = app_for(request).filestore().folder(FOLDER_ID)
    stream = io.BytesIO(data)
    stream.name = filename
    result = folder.upload_file(stream)
    details = result.get("file_details", result)
    return str(details.get("id") or details.get("file_id"))


def download_file(request: Request, file_id: str) -> bytes:
    folder = app_for(request).filestore().folder(FOLDER_ID)
    return folder.file(file_id).download_file()


def remove_file(request: Request, file_id: Optional[str]) -> None:
    if file_id and FOLDER_ID:
        app_for(request).filestore().folder(FOLDER_ID).delete_file(file_id)
