from html import escape

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse

from db import get_db
from config import UPLOAD_DIR

router = APIRouter(tags=["public"])
NO_CACHE = {"Cache-Control": "no-cache"}


def load_content(db, slug: str):
    biz = db.execute(
        """SELECT b.id, b.name, q.name AS qr_name, q.slug
           FROM qr_codes q JOIN businesses b ON b.id = q.business_id
           WHERE q.slug = ?""",
        (slug,),
    ).fetchone()
    if biz is None:
        raise HTTPException(404, "This QR code does not exist")
    item = db.execute(
        "SELECT * FROM contents WHERE qr_code_id = (SELECT id FROM qr_codes WHERE slug = ?)",
        (slug,),
    ).fetchone()
    return biz, item


@router.get("/q/{slug}")
@router.get("/b/{slug}")
def public_content(slug: str, db=Depends(get_db)):
    _, item = load_content(db, slug)
    if item is None:
        raise HTTPException(404, "This QR code has no content yet")
    if item["type"] == "link":
        return RedirectResponse(item["url_value"], status_code=307, headers=NO_CACHE)
    if item["type"] in {"image", "pdf"}:
        return FileResponse(
            f"{UPLOAD_DIR}/{item['file_name']}",
            media_type="image/*" if item["type"] == "image" else "application/pdf",
            headers=NO_CACHE,
        )
    return PlainTextResponse(item["text_value"] or "", headers=NO_CACHE)


@router.get("/api/public/{slug}")
def public_json(slug: str, db=Depends(get_db)):
    biz, item = load_content(db, slug)
    return {
        "business_name": biz["name"],
        "content": {
            "id": item["id"], "title": item["title"], "type": item["type"],
            "text": item["text_value"], "url": item["url_value"],
            "file_url": f"/uploads/{item['file_name']}" if item["file_name"] else None,
            "updated_at": item["updated_at"],
        } if item else None,
    }
