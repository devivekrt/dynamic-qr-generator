from html import escape

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from db import get_db

router = APIRouter(tags=["public"])
NO_CACHE = {"Cache-Control": "no-cache"}


def load_page(db, slug: str):
    biz = db.execute(
        """SELECT b.id, b.name, q.name AS qr_name, q.slug
           FROM qr_codes q JOIN businesses b ON b.id = q.business_id
           WHERE q.slug = ?""",
        (slug,),
    ).fetchone()
    if biz is None:
        raise HTTPException(404, "This page does not exist")
    items = db.execute(
        "SELECT * FROM contents WHERE qr_code_id = "
        "(SELECT id FROM qr_codes WHERE slug = ?) ORDER BY id DESC",
        (slug,),
    ).fetchall()
    return biz, items


def render_item(item) -> str:
    title = escape(item["title"])
    kind = item["type"]
    file_url = f"/uploads/{escape(item['file_name'])}" if item["file_name"] else ""

    if kind == "text":
        body = escape(item["text_value"] or "").replace("\n", "<br>")
        return f'<section class="block"><h2>{title}</h2><p>{body}</p></section>'
    if kind == "image":
        return (
            f'<figure class="block"><img src="{file_url}" alt="{title}" loading="lazy">'
            f"<figcaption>{title}</figcaption></figure>"
        )
    if kind == "pdf":
        return (
            f'<a class="block link" href="{file_url}" target="_blank" rel="noopener">'
            f'<span>{title}</span><small>PDF</small></a>'
        )
    url = escape(item["url_value"] or "", quote=True)
    return (
        f'<a class="block link" href="{url}" target="_blank" rel="noopener noreferrer">'
        f"<span>{title}</span><small>Open link</small></a>"
    )


def render_page(biz, items) -> str:
    name = escape(biz["qr_name"] or biz["name"])
    body = "".join(render_item(i) for i in items) or (
        '<p class="empty">Nothing is posted yet. Check back soon.</p>'
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
</head>
<body class="public">
<main class="public-wrap">
<header class="public-head"><p class="hint">{escape(biz["name"])}</p><h1>{name}</h1></header>
{body}
</main>
</body>
</html>"""


@router.get("/q/{slug}", response_class=HTMLResponse)
@router.get("/b/{slug}", response_class=HTMLResponse)
def public_page(slug: str, db=Depends(get_db)):
    biz, items = load_page(db, slug)
    return HTMLResponse(render_page(biz, items), headers=NO_CACHE)


@router.get("/api/public/{slug}")
def public_json(slug: str, db=Depends(get_db)):
    biz, items = load_page(db, slug)
    return {
        "business_name": biz["name"],
        "items": [
            {
                "id": i["id"],
                "title": i["title"],
                "type": i["type"],
                "text": i["text_value"],
                "url": i["url_value"],
                "file_url": f"/uploads/{i['file_name']}" if i["file_name"] else None,
                "updated_at": i["updated_at"],
            }
            for i in items
        ],
    }
