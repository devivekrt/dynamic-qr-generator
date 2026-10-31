from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_Q
from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from config import BASE_URL
from security import current_business

router = APIRouter(prefix="/api/business", tags=["business"])


def public_url(request: Request, slug: str) -> str:
    base = BASE_URL or str(request.base_url).rstrip("/")
    return f"{base}/b/{slug}"


@router.get("/me")
def me(request: Request, biz=Depends(current_business)):
    return {
        "id": biz["id"],
        "name": biz["name"],
        "email": biz["email"],
        "slug": biz["slug"],
        "public_url": public_url(request, biz["slug"]),
    }


@router.get("/qr")
def qr_code(request: Request, download: bool = False, biz=Depends(current_business)):
    """PNG QR code that points to the permanent public page URL."""
    img = qrcode.make(
        public_url(request, biz["slug"]),
        error_correction=ERROR_CORRECT_Q,
        box_size=12,
        border=3,
    )
    buf = BytesIO()
    img.save(buf, format="PNG")
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="qr-{biz["slug"]}.png"'
    return Response(buf.getvalue(), media_type="image/png", headers=headers)
