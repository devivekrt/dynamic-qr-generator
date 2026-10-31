import re
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from db import get_db
from security import create_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterIn(BaseModel):
    business_name: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=120)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: str
    password: str


def make_slug(db, name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30] or "business"
    while True:
        slug = f"{base}-{secrets.token_hex(2)}"
        if db.execute("SELECT 1 FROM businesses WHERE slug = ?", (slug,)).fetchone() is None:
            return slug


@router.post("/register", status_code=201)
def register(data: RegisterIn, db=Depends(get_db)):
    email = data.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(422, "Enter a valid email address")
    if db.execute("SELECT 1 FROM businesses WHERE email = ?", (email,)).fetchone():
        raise HTTPException(409, "An account with this email already exists")

    name = data.business_name.strip()
    if not name:
        raise HTTPException(422, "Business name is required")
    cur = db.execute(
        "INSERT INTO businesses (name, email, password_hash, slug, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            name,
            email,
            hash_password(data.password),
            make_slug(db, name),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    db.commit()
    return {"token": create_token(cur.lastrowid), "business_name": name}


@router.post("/login")
def login(data: LoginIn, db=Depends(get_db)):
    row = db.execute(
        "SELECT * FROM businesses WHERE email = ?", (data.email.strip().lower(),)
    ).fetchone()
    if row is None or not verify_password(data.password, row["password_hash"]):
        raise HTTPException(401, "Email or password is incorrect")
    return {"token": create_token(row["id"]), "business_name": row["name"]}
