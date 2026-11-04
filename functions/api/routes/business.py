from io import BytesIO
import re

import qrcode
from PIL import Image, ImageDraw
from qrcode.constants import ERROR_CORRECT_H
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response

from catalyst_store import BUSINESSES, CONTENTS, QR_CODES, all_rows, delete, download_file, find_one, get_owned_qr, insert, remove_file, row_id, update, upload_file
from config import BASE_URL
from plans import plan_for, require_template
from security import current_business

router = APIRouter(prefix="/api/business", tags=["business"])
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
DEFAULT_DESIGN = {
    "DESIGN_TEMPLATE": "classic",
    "FOREGROUND_COLOR": "#111827",
    "BACKGROUND_COLOR": "#FFFFFF",
    "EYE_STYLE": "square",
    "FRAME_STYLE": "none",
}


def design_for(row: dict) -> dict:
    return {key: row.get(key) or value for key, value in DEFAULT_DESIGN.items()} | {
        "LOGO_FILE_ID": row.get("LOGO_FILE_ID"),
        "LOGO_FILE_NAME": row.get("LOGO_FILE_NAME"),
    }


def serialize_qr(request: Request, row: dict, content_count: int = 0) -> dict:
    design = design_for(row)
    return {
        "id": row_id(row),
        "name": row["QR_NAME"],
        "slug": row["SLUG"],
        "content_count": content_count,
        "public_url": public_url(request, row["SLUG"]),
        "design": design,
    }


def validate_color(value: str, field: str) -> str:
    if not COLOR_RE.match(value):
        raise HTTPException(422, f"{field} must be a six-digit hex color")
    return value.upper()


def draw_finder(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str, background: str, style: str) -> None:
    draw.rectangle((x, y, x + size * 7 - 1, y + size * 7 - 1), fill=color)
    inset = size if style != "rounded" else max(1, size // 2)
    draw.rectangle((x + inset, y + inset, x + size * 6 - 1, y + size * 6 - 1), fill=background)
    draw.rectangle((x + size * 2, y + size * 2, x + size * 5 - 1, y + size * 5 - 1), fill=color)


def qr_image(request: Request, row: dict) -> Image.Image:
    design = design_for(row)
    # The quiet zone is added below so the custom finder patterns align with
    # the matrix instead of being drawn a second time at a shifted position.
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H, box_size=10, border=0)
    qr.add_data(public_url(request, row["SLUG"]))
    qr.make(fit=True)
    matrix = qr.get_matrix()
    module = 12
    quiet = 4
    size = (len(matrix) + quiet * 2) * module
    foreground = design["FOREGROUND_COLOR"]
    background = design["BACKGROUND_COLOR"]
    image = Image.new("RGB", (size, size), background)
    draw = ImageDraw.Draw(image)
    template = design["DESIGN_TEMPLATE"]
    for row_index, values in enumerate(matrix):
        for column_index, enabled in enumerate(values):
            if not enabled:
                continue
            x = (column_index + quiet) * module
            y = (row_index + quiet) * module
            box = (x, y, x + module - 1, y + module - 1)
            if template in {"rounded", "gradient", "fluid"}:
                draw.rounded_rectangle(box, radius=module // 3, fill=foreground)
            elif template == "dotted":
                draw.ellipse(box, fill=foreground)
            elif template == "star":
                draw.regular_polygon((x + module // 2, y + module // 2, module // 2), 5, rotation=0, fill=foreground)
            elif template == "heart":
                draw.ellipse((x, y + module // 4, x + module // 2, y + module - 1), fill=foreground)
                draw.ellipse((x + module // 2 - 1, y + module // 4, x + module - 1, y + module - 1), fill=foreground)
            else:
                draw.rectangle(box, fill=foreground)
    finder_offset = quiet * module
    finder_span = (len(matrix) - 7) * module + finder_offset
    style = design["EYE_STYLE"]
    draw_finder(draw, finder_offset, finder_offset, module, foreground, background, style)
    draw_finder(draw, finder_span, finder_offset, module, foreground, background, style)
    draw_finder(draw, finder_offset, finder_span, module, foreground, background, style)
    if design["FRAME_STYLE"] == "label":
        draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=module, outline=foreground, width=module)
    if design.get("LOGO_FILE_ID"):
        try:
            from io import BytesIO
            logo = Image.open(BytesIO(download_file(request, str(design["LOGO_FILE_ID"])))).convert("RGBA")
            logo_size = max(module * 5, size // 6)
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            padding = module
            badge = Image.new("RGBA", (logo.width + padding * 2, logo.height + padding * 2), "white")
            badge.alpha_composite(logo, (padding, padding))
            image.paste(badge, ((size - badge.width) // 2, (size - badge.height) // 2), badge)
        except (OSError, ValueError):
            pass
    return image


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
    plan_name, plan = plan_for(biz)
    return {
        "id": biz.get("ROWID"),
        "name": biz["BUSINESS_NAME"],
        "email": biz["EMAIL"],
        "slug": biz["SLUG"],
        "plan": plan_name,
        "plan_label": plan["label"],
        "qr_limit": plan["qr_limit"],
        "design_templates": sorted(plan["templates"]),
        "allow_custom_colors": plan["allow_custom_colors"],
        "allow_logo": plan["allow_logo"],
    }


@router.get("/qr-codes")
def list_qr_codes(request: Request, biz=Depends(current_business)):
    rows = [r for r in all_rows(request, QR_CODES) if str(r.get("BUSINESS_ID")) == str(biz.get("ROWID"))]
    contents = all_rows(request, CONTENTS)
    return [
        serialize_qr(request, row, int(any(str(c.get("QR_CODE_ID")) == str(row.get("ROWID")) for c in contents)))
        for row in reversed(rows)
    ]


@router.post("/qr-codes", status_code=201)
def create_qr_code(data: dict, request: Request, biz=Depends(current_business)):
    name = str(data.get("name", "")).strip()
    if not 1 <= len(name) <= 120:
        raise HTTPException(422, "Enter a QR code name")
    _, plan = plan_for(biz)
    existing = [row for row in all_rows(request, QR_CODES) if str(row.get("BUSINESS_ID")) == str(biz.get("ROWID"))]
    if len(existing) >= plan["qr_limit"]:
        raise HTTPException(403, f"Your {plan['label']} plan allows up to {plan['qr_limit']} QR codes")
    slug = unique_slug(request, name)
    inserted = insert(request, QR_CODES, {
        "BUSINESS_ID": str(biz.get("ROWID")), "QR_NAME": name,
        "SLUG": slug,
    })
    row = find_one(request, QR_CODES, lambda item: item.get("SLUG") == slug) or inserted
    identifier = row_id(row)
    if not identifier or identifier == "None":
        raise HTTPException(500, "QR code was saved but could not be loaded")
    return serialize_qr(request, {**row, "ROWID": identifier, "QR_NAME": row.get("QR_NAME") or name, "SLUG": row.get("SLUG") or slug})


@router.put("/qr-codes/{qr_id}/design")
async def update_design(
    qr_id: str,
    request: Request,
    template: str = Form("classic"),
    foreground_color: str = Form("#111827"),
    background_color: str = Form("#FFFFFF"),
    eye_style: str = Form("square"),
    frame_style: str = Form("none"),
    logo: UploadFile | None = File(None),
    biz=Depends(current_business),
):
    row = get_owned_qr(request, qr_id, str(biz.get("ROWID")))
    _, plan = require_template(biz, template)
    if eye_style not in {"square", "rounded"} or frame_style not in {"none", "label"}:
        raise HTTPException(422, "Choose a supported QR style")
    if not plan["allow_custom_colors"] and (foreground_color.upper() != DEFAULT_DESIGN["FOREGROUND_COLOR"] or background_color.upper() != DEFAULT_DESIGN["BACKGROUND_COLOR"]):
        raise HTTPException(403, "Custom colors require the Prime plan or higher")
    foreground_color = validate_color(foreground_color, "Foreground color")
    background_color = validate_color(background_color, "Background color")
    old_logo = row.get("LOGO_FILE_ID")
    values = {**row, **{
        "DESIGN_TEMPLATE": template,
        "FOREGROUND_COLOR": foreground_color,
        "BACKGROUND_COLOR": background_color,
        "EYE_STYLE": eye_style,
        "FRAME_STYLE": frame_style,
    }}
    if logo is not None and logo.filename:
        if not plan["allow_logo"]:
            raise HTTPException(403, "Logo branding requires the Business plan or higher")
        data = await logo.read()
        if len(data) > 2 * 1024 * 1024:
            raise HTTPException(413, "Logo must be 2 MB or smaller")
        if logo.content_type not in {"image/png", "image/jpeg", "image/webp"}:
            raise HTTPException(422, "Logo must be a PNG, JPEG, or WebP image")
        values["LOGO_FILE_ID"] = upload_file(request, f"qr-logo-{row_id(row)}", data)
        values["LOGO_FILE_NAME"] = logo.filename
    try:
        updated = update(request, QR_CODES, {
            "ROWID": row_id(row),
            "DESIGN_TEMPLATE": template,
            "FOREGROUND_COLOR": foreground_color,
            "BACKGROUND_COLOR": background_color,
            "EYE_STYLE": eye_style,
            "FRAME_STYLE": frame_style,
            **({"LOGO_FILE_ID": values["LOGO_FILE_ID"], "LOGO_FILE_NAME": values["LOGO_FILE_NAME"]} if "LOGO_FILE_ID" in values else {}),
        })
    except Exception as exc:
        raise HTTPException(500, "Design could not be saved. Verify the QR design columns are present in Catalyst.") from exc
    if old_logo and values.get("LOGO_FILE_ID") != old_logo:
        remove_file(request, old_logo)
    return serialize_qr(request, {**row, **values, **(updated or {})})


@router.post("/qr-codes/{qr_id}/design/preview")
async def preview_design(
    qr_id: str,
    request: Request,
    template: str = Form("classic"),
    foreground_color: str = Form("#111827"),
    background_color: str = Form("#FFFFFF"),
    eye_style: str = Form("square"),
    frame_style: str = Form("none"),
    biz=Depends(current_business),
):
    row = get_owned_qr(request, qr_id, str(biz.get("ROWID")))
    require_template(biz, template)
    if eye_style not in {"square", "rounded"} or frame_style not in {"none", "label"}:
        raise HTTPException(422, "Choose a supported QR style")
    foreground_color = validate_color(foreground_color, "Foreground color")
    background_color = validate_color(background_color, "Background color")
    preview_row = {**row, "DESIGN_TEMPLATE": template, "FOREGROUND_COLOR": foreground_color,
                   "BACKGROUND_COLOR": background_color, "EYE_STYLE": eye_style, "FRAME_STYLE": frame_style}
    image = qr_image(request, preview_row)
    output = BytesIO()
    image.save(output, format="PNG")
    return Response(output.getvalue(), media_type="image/png")


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
    img = qr_image(request, row)
    buf = BytesIO()
    img.save(buf, format="PNG")
    headers = {"Content-Disposition": f'attachment; filename="qr-{row["SLUG"]}.png"'} if download else {}
    return Response(buf.getvalue(), media_type="image/png", headers=headers)
