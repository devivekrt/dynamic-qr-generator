from io import BytesIO
from datetime import datetime, timezone

import qrcode
from qrcode.constants import ERROR_CORRECT_Q
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from catalyst_store import BUSINESSES, CONTENTS, QR_CODES, all_rows, delete, find_one, get_owned_qr, insert, remove_file, row_id
from config import BASE_URL
from security import current_business

router = APIRouter(prefix="/api/business", tags=["business"])


def public_url(request: Request, slug: str) -> str:
    base = BASE_URL or str(request.base_url).rstrip("/")
    return f"{base}/q/{slug}"


def unique_slug(request: Request, name: str) -> str:
    import re
    import secrets
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30] or "qr"
    while True:
        slug = f"{base}-{secrets.token_hex(3)}"
        if not find_one(request, QR_CODES, lambda r: r.get("SLUG") == slug):
            return slug


@router.get("/me")
def me(biz=Depends(current_business)):
    return {
        "id": biz.get("ROWID"),
        "name": biz["BUSINESS_NAME"],
        "email": biz["EMAIL"],
        "slug": biz["SLUG"],
    }


@router.get("/qr-codes")
def list_qr_codes(request: Request, biz=Depends(current_business)):
    rows = [r for r in all_rows(request, QR_CODES) if str(r.get("BUSINESS_ID")) == str(biz.get("ROWID"))]
    contents = all_rows(request, CONTENTS)
    return [
        {
            "id": row.get("ROWID"),
            "name": row["QR_NAME"],
            "slug": row["SLUG"],
            "content_count": int(any(str(c.get("QR_CODE_ID")) == str(row.get("ROWID")) for c in contents)),
            "public_url": public_url(request, row["SLUG"]),
        }
        for row in reversed(rows)
    ]


@router.post("/qr-codes", status_code=201)
def create_qr_code(data: dict, request: Request, biz=Depends(current_business)):
    name = str(data.get("name", "")).strip()
    if not 1 <= len(name) <= 120:
        raise HTTPException(422, "Enter a QR code name")
    slug = unique_slug(request, name)
    inserted = insert(request, QR_CODES, {
        "BUSINESS_ID": str(biz.get("ROWID")), "QR_NAME": name,
        "SLUG": slug,
    })
    row = find_one(request, QR_CODES, lambda item: item.get("SLUG") == slug) or inserted
    identifier = row_id(row)
    if not identifier or identifier == "None":
        raise HTTPException(500, "QR code was saved but could not be loaded")
    return {
        "id": identifier,
        "name": row.get("QR_NAME") or name,
        "slug": row.get("SLUG") or slug,
        "content_count": 0,
        "public_url": public_url(request, row.get("SLUG") or slug),
    }


@router.delete("/qr-codes/{qr_id}", status_code=204)
def delete_qr_code(qr_id: str, request: Request, biz=Depends(current_business)):
    row = get_owned_qr(request, qr_id, str(biz.get("ROWID")))
    qrs = [r for r in all_rows(request, QR_CODES) if str(r.get("BUSINESS_ID")) == str(biz.get("ROWID"))]
    if len(qrs) <= 1:
        raise HTTPException(422, "Keep at least one QR code")
    for content in all_rows(request, CONTENTS):
        if str(content.get("QR_CODE_ID")) == qr_id:
            remove_file(request, content.get("FILE_ID"))
            delete(request, CONTENTS, str(content["ROWID"]))
    delete(request, QR_CODES, str(row["ROWID"]))


@router.get("/qr-codes/{qr_id}/image")
def qr_code(qr_id: str, request: Request, download: bool = False, biz=Depends(current_business)):
    row = get_owned_qr(request, qr_id, str(biz.get("ROWID")))
    img = qrcode.make(public_url(request, row["SLUG"]), error_correction=ERROR_CORRECT_Q, box_size=12, border=3)
    buf = BytesIO()
    img.save(buf, format="PNG")
    headers = {"Content-Disposition": f'attachment; filename="qr-{row["SLUG"]}.png"'} if download else {}
    return Response(buf.getvalue(), media_type="image/png", headers=headers)
