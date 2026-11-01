from io import BytesIO
from datetime import datetime, timezone
import os

import qrcode
from qrcode.constants import ERROR_CORRECT_Q
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import Response

from config import BASE_URL
from config import UPLOAD_DIR
from db import get_db
from security import current_business

router = APIRouter(prefix="/api/business", tags=["business"])


def public_url(request: Request, slug: str) -> str:
    base = BASE_URL or str(request.base_url).rstrip("/")
    return f"{base}/q/{slug}"


def qr_slug(db, name: str) -> str:
    import re
    import secrets
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30] or "qr"
    while True:
        slug = f"{base}-{secrets.token_hex(3)}"
        if db.execute("SELECT 1 FROM qr_codes WHERE slug = ?", (slug,)).fetchone() is None:
            return slug


@router.get("/me")
def me(request: Request, biz=Depends(current_business)):
    return {
        "id": biz["id"],
        "name": biz["name"],
        "email": biz["email"],
        "slug": biz["slug"],
    }


@router.get("/qr-codes")
def list_qr_codes(request: Request, biz=Depends(current_business), db=Depends(get_db)):
    rows = db.execute(
        """SELECT q.*, COUNT(c.id) AS content_count
           FROM qr_codes q LEFT JOIN contents c ON c.qr_code_id = q.id
           WHERE q.business_id = ? GROUP BY q.id ORDER BY q.id DESC""",
        (biz["id"],),
    ).fetchall()
    return [
        {**dict(row), "public_url": public_url(request, row["slug"])}
        for row in rows
    ]


@router.post("/qr-codes", status_code=201)
def create_qr_code(data: dict, request: Request, biz=Depends(current_business), db=Depends(get_db)):
    name = str(data.get("name", "")).strip()
    if not 1 <= len(name) <= 120:
        raise HTTPException(422, "Enter a QR code name")
    slug = qr_slug(db, name)
    now = datetime.now(timezone.utc).isoformat()
    cur = db.execute(
        "INSERT INTO qr_codes (business_id, name, slug, created_at) VALUES (?, ?, ?, ?)",
        (biz["id"], name, slug, now),
    )
    db.commit()
    row = db.execute("SELECT * FROM qr_codes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return {**dict(row), "content_count": 0, "public_url": public_url(request, slug)}


@router.delete("/qr-codes/{qr_id}", status_code=204)
def delete_qr_code(qr_id: int, biz=Depends(current_business), db=Depends(get_db)):
    row = db.execute(
        "SELECT * FROM qr_codes WHERE id = ? AND business_id = ?", (qr_id, biz["id"])
    ).fetchone()
    if row is None:
        raise HTTPException(404, "QR code not found")
    count = db.execute(
        "SELECT COUNT(*) AS count FROM qr_codes WHERE business_id = ?", (biz["id"],)
    ).fetchone()["count"]
    if count <= 1:
        raise HTTPException(422, "Keep at least one QR code")
    files = db.execute(
        "SELECT file_name FROM contents WHERE qr_code_id = ? AND file_name IS NOT NULL",
        (qr_id,),
    ).fetchall()
    db.execute("DELETE FROM contents WHERE qr_code_id = ?", (qr_id,))
    db.execute("DELETE FROM qr_codes WHERE id = ?", (qr_id,))
    db.commit()
    for file in files:
        try:
            os.remove(os.path.join(UPLOAD_DIR, file["file_name"]))
        except OSError:
            pass


@router.get("/qr-codes/{qr_id}/image")
def qr_code(qr_id: int, request: Request, download: bool = False,
            biz=Depends(current_business), db=Depends(get_db)):
    row = db.execute(
        "SELECT * FROM qr_codes WHERE id = ? AND business_id = ?", (qr_id, biz["id"])
    ).fetchone()
    if row is None:
        raise HTTPException(404, "QR code not found")
    img = qrcode.make(
        public_url(request, row["slug"]),
        error_correction=ERROR_CORRECT_Q,
        box_size=12,
        border=3,
    )
    buf = BytesIO()
    img.save(buf, format="PNG")
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="qr-{row["slug"]}.png"'
    return Response(buf.getvalue(), media_type="image/png", headers=headers)
