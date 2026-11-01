from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, RedirectResponse, Response

from catalyst_store import CONTENTS, download_file, find_one, row_id
from fastapi import status

router = APIRouter(tags=["public"])
NO_CACHE = {"Cache-Control": "no-cache"}


def load_content(request: Request, slug: str):
    qr = find_one(request, "QrCodes", lambda r: r.get("slug") == slug)
    if qr is None:
        raise HTTPException(404, "This QR code does not exist")
    item = find_one(request, CONTENTS, lambda r: str(r.get("qr_code_id")) == row_id(qr))
    return qr, item


@router.get("/q/{slug}")
@router.get("/b/{slug}")
def public_content(slug: str, request: Request):
    _, item = load_content(request, slug)
    if item is None:
        raise HTTPException(404, "This QR code has no content yet")
    if item["type"] == "link":
        return RedirectResponse(item["url_value"], status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers=NO_CACHE)
    if item["type"] in {"image", "pdf"}:
        media_type = "image/*" if item["type"] == "image" else "application/pdf"
        return Response(download_file(request, item["file_id"]), media_type=media_type, headers=NO_CACHE)
    return PlainTextResponse(item.get("text_value") or "", headers=NO_CACHE)


@router.get("/api/public/{slug}")
def public_json(slug: str, request: Request):
    qr, item = load_content(request, slug)
    return {"qr_name": qr["name"], "content": {
        "id": row_id(item), "title": item["title"], "type": item["type"],
        "text": item.get("text_value"), "url": item.get("url_value"),
        "file_id": item.get("file_id"), "updated_at": item["updated_at"],
    } if item else None}


@router.get("/files/{file_id}")
def public_file(file_id: str, request: Request):
    item = find_one(request, CONTENTS, lambda r: str(r.get("file_id")) == file_id)
    if item is None:
        raise HTTPException(404, "File not found")
    media_type = "image/*" if item["type"] == "image" else "application/pdf"
    return Response(download_file(request, file_id), media_type=media_type, headers=NO_CACHE)
