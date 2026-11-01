import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, Query

from catalyst_store import CONTENTS, all_rows, delete, find_one, get_owned_content, get_owned_qr, insert, now, remove_file, update, upload_file
from security import current_business

router = APIRouter(prefix="/api/content", tags=["content"])
TYPES = {"text", "link", "image", "pdf"}
ALLOWED_EXT = {"image": {".png", ".jpg", ".jpeg", ".webp", ".gif"}, "pdf": {".pdf"}}


def serialize(row: Optional[dict]) -> Optional[dict]:
    if row is None:
        return None
    return {
        "id": row.get("ROWID"),
        "qr_code_id": row.get("QR_CODE_ID"),
        "title": row.get("TITLE"),
        "type": row.get("TYPE"),
        "text_value": row.get("TEXT_VALUE"),
        "url_value": row.get("URL_VALUE"),
        "file_name": row.get("FILE_NAME"),
        "file_id": row.get("FILE_ID"),
        "original_name": row.get("FILE_NAME"),
        "file_url": f"/files/{row['FILE_ID']}" if row.get("FILE_ID") else None,
    }


def clean_url(value: Optional[str]) -> str:
    value = (value or "").strip()
    if not value.lower().startswith(("http://", "https://")):
        raise HTTPException(422, "Links must start with http:// or https://")
    return value


async def upload_value(request: Request, file: UploadFile, ctype: str):
    original = os.path.basename(file.filename or "")
    ext = os.path.splitext(original)[1].lower()
    if ext not in ALLOWED_EXT[ctype]:
        raise HTTPException(422, f"This content type accepts only: {', '.join(sorted(ALLOWED_EXT[ctype]))}")
    data = await file.read()
    if len(data) > int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024:
        raise HTTPException(413, "File is too large")
    return upload_file(request, f"{uuid.uuid4().hex}{ext}", data), original


@router.get("")
def list_content(request: Request, qr_code_id: str = Query(...), biz=Depends(current_business)):
    get_owned_qr(request, qr_code_id, str(biz.get("ROWID")))
    row = find_one(request, CONTENTS, lambda r: str(r.get("QR_CODE_ID")) == qr_code_id)
    return serialize(row)


@router.get("/{content_id}")
def get_content(content_id: str, request: Request, biz=Depends(current_business)):
    return serialize(get_owned_content(request, content_id, str(biz.get("ROWID"))))


@router.post("", status_code=201)
async def create_content(
    request: Request, title: str = Form(..., min_length=1, max_length=120), type: str = Form(...),
    text_value: Optional[str] = Form(None), url_value: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None), qr_code_id: str = Form(...),
    biz=Depends(current_business),
):
    get_owned_qr(request, qr_code_id, str(biz.get("ROWID")))
    if find_one(request, CONTENTS, lambda r: str(r.get("QR_CODE_ID")) == qr_code_id):
        raise HTTPException(409, "This QR code already has content. Edit it instead.")
    if type not in TYPES:
        raise HTTPException(422, "Choose a content type")
    values = {"QR_CODE_ID": qr_code_id, "TITLE": title.strip(), "TYPE": type}
    if type == "text":
        values["TEXT_VALUE"] = (text_value or "").strip()
        if not values["TEXT_VALUE"]:
            raise HTTPException(422, "Enter the text to show")
    elif type == "link":
        values["URL_VALUE"] = clean_url(url_value)
    else:
        if file is None or not file.filename:
            raise HTTPException(422, "Choose a file to upload")
        values["FILE_ID"], values["FILE_NAME"] = await upload_value(request, file, type)
    return serialize(insert(request, CONTENTS, values))


@router.put("/{content_id}")
async def update_content(
    content_id: str, request: Request, title: str = Form(..., min_length=1, max_length=120),
    text_value: Optional[str] = Form(None), url_value: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None), biz=Depends(current_business),
):
    row = get_owned_content(request, content_id, str(biz.get("ROWID")))
    values = dict(row)
    values["TITLE"] = title.strip()
    if row["TYPE"] == "text":
        values["TEXT_VALUE"] = (text_value or "").strip()
        if not values["TEXT_VALUE"]:
            raise HTTPException(422, "Enter the text to show")
    elif row["TYPE"] == "link":
        values["URL_VALUE"] = clean_url(url_value)
    elif file is not None and file.filename:
        new_id, original = await upload_value(request, file, row["TYPE"])
        values["FILE_ID"], values["FILE_NAME"] = new_id, original
    updated = update(request, CONTENTS, values)
    remove_file(request, row.get("FILE_ID") if values.get("FILE_ID") != row.get("FILE_ID") else None)
    return serialize(updated)


@router.put("/{content_id}/file")
async def replace_file(content_id: str, request: Request, file: UploadFile = File(...), biz=Depends(current_business)):
    row = get_owned_content(request, content_id, str(biz.get("ROWID")))
    if row["TYPE"] not in ALLOWED_EXT:
        raise HTTPException(400, "Only image and PDF content has a file")
    new_id, original = await upload_value(request, file, row["TYPE"])
    updated = update(request, CONTENTS, {**row, "FILE_ID": new_id, "FILE_NAME": original})
    remove_file(request, row.get("FILE_ID"))
    return serialize(updated)


@router.delete("/{content_id}", status_code=204)
def delete_content(content_id: str, request: Request, biz=Depends(current_business)):
    row = get_owned_content(request, content_id, str(biz.get("ROWID")))
    delete(request, CONTENTS, content_id)
    remove_file(request, row.get("FILE_ID"))
