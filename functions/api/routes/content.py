import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from config import MAX_UPLOAD_BYTES, UPLOAD_DIR
from db import get_db
from security import current_business

router = APIRouter(prefix="/api/content", tags=["content"])

TYPES = {"text", "link", "image", "pdf"}
ALLOWED_EXT = {
    "image": {".png", ".jpg", ".jpeg", ".webp", ".gif"},
    "pdf": {".pdf"},
}
IMAGE_SIGNATURES = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"RIFF")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def serialize(row) -> dict:
    d = dict(row)
    d["file_url"] = f"/uploads/{d['file_name']}" if d.get("file_name") else None
    return d


def get_owned(db, content_id: int, business_id: int):
    row = db.execute(
        "SELECT * FROM contents WHERE id = ? AND business_id = ?", (content_id, business_id)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Content not found")
    return row


def clean_url(value: Optional[str]) -> str:
    value = (value or "").strip()
    if not value.lower().startswith(("http://", "https://")):
        raise HTTPException(422, "Links must start with http:// or https://")
    return value


def save_upload(file: UploadFile, ctype: str):
    """Validates and stores the file. Returns (stored_name, original_name)."""
    original = os.path.basename(file.filename or "")
    ext = os.path.splitext(original)[1].lower()
    if ext not in ALLOWED_EXT.get(ctype, set()):
        allowed = ", ".join(sorted(ALLOWED_EXT[ctype]))
        raise HTTPException(422, f"This content type accepts only: {allowed}")
    expected_types = {
        "image": {"image/png", "image/jpeg", "image/webp", "image/gif"},
        "pdf": {"application/pdf"},
    }
    if file.content_type and file.content_type not in expected_types[ctype]:
        raise HTTPException(422, "The uploaded file type does not match the selected content type")
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"File is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB")
    if ctype == "pdf" and not data.startswith(b"%PDF-"):
        raise HTTPException(422, "The uploaded file is not a valid PDF")
    if ctype == "image" and not data.startswith(IMAGE_SIGNATURES):
        raise HTTPException(422, "The uploaded file is not a supported image")
    stored = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(UPLOAD_DIR, stored), "wb") as fh:
        fh.write(data)
    return stored, original


def remove_file(stored_name: Optional[str]) -> None:
    if not stored_name:
        return
    try:
        os.remove(os.path.join(UPLOAD_DIR, stored_name))
    except OSError:
        pass


def has_file(file: Optional[UploadFile]) -> bool:
    return file is not None and bool(file.filename)


@router.get("")
def list_content(biz=Depends(current_business), db=Depends(get_db)):
    rows = db.execute(
        "SELECT * FROM contents WHERE business_id = ? ORDER BY id DESC", (biz["id"],)
    ).fetchall()
    return [serialize(r) for r in rows]


@router.get("/{content_id}")
def get_content(content_id: int, biz=Depends(current_business), db=Depends(get_db)):
    return serialize(get_owned(db, content_id, biz["id"]))


@router.post("", status_code=201)
def create_content(
    title: str = Form(..., min_length=1, max_length=120),
    type: str = Form(...),
    text_value: Optional[str] = Form(None),
    url_value: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    biz=Depends(current_business),
    db=Depends(get_db),
):
    if type not in TYPES:
        raise HTTPException(422, "Choose a content type")
    text, url, stored, original = None, None, None, None

    if type == "text":
        text = (text_value or "").strip()
        if not text:
            raise HTTPException(422, "Enter the text to show")
    elif type == "link":
        url = clean_url(url_value)
    else:
        if not has_file(file):
            raise HTTPException(422, "Choose a file to upload")
        stored, original = save_upload(file, type)

    cur = db.execute(
        "INSERT INTO contents (business_id, title, type, text_value, url_value, "
        "file_name, original_name, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (biz["id"], title.strip(), type, text, url, stored, original, now(), now()),
    )
    db.commit()
    return serialize(get_owned(db, cur.lastrowid, biz["id"]))


@router.put("/{content_id}")
def update_content(
    content_id: int,
    title: str = Form(..., min_length=1, max_length=120),
    text_value: Optional[str] = Form(None),
    url_value: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    biz=Depends(current_business),
    db=Depends(get_db),
):
    row = get_owned(db, content_id, biz["id"])
    ctype = row["type"]
    text, url = row["text_value"], row["url_value"]
    stored, original = row["file_name"], row["original_name"]
    old_file = None

    if ctype == "text":
        text = (text_value or "").strip()
        if not text:
            raise HTTPException(422, "Enter the text to show")
    elif ctype == "link":
        url = clean_url(url_value)
    elif has_file(file):
        old_file = stored
        stored, original = save_upload(file, ctype)

    db.execute(
        "UPDATE contents SET title=?, text_value=?, url_value=?, file_name=?, "
        "original_name=?, updated_at=? WHERE id=?",
        (title.strip(), text, url, stored, original, now(), content_id),
    )
    db.commit()
    remove_file(old_file)
    return serialize(get_owned(db, content_id, biz["id"]))


@router.put("/{content_id}/file")
def replace_file(
    content_id: int,
    file: UploadFile = File(...),
    biz=Depends(current_business),
    db=Depends(get_db),
):
    row = get_owned(db, content_id, biz["id"])
    if row["type"] not in ALLOWED_EXT:
        raise HTTPException(400, "Only image and PDF content has a file")
    stored, original = save_upload(file, row["type"])
    db.execute(
        "UPDATE contents SET file_name=?, original_name=?, updated_at=? WHERE id=?",
        (stored, original, now(), content_id),
    )
    db.commit()
    remove_file(row["file_name"])
    return serialize(get_owned(db, content_id, biz["id"]))


@router.delete("/{content_id}", status_code=204)
def delete_content(content_id: int, biz=Depends(current_business), db=Depends(get_db)):
    row = get_owned(db, content_id, biz["id"])
    db.execute("DELETE FROM contents WHERE id = ?", (content_id,))
    db.commit()
    remove_file(row["file_name"])
