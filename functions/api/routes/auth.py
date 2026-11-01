import re
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from catalyst_store import BUSINESSES, QR_CODES, all_rows, find_one, insert, now
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


def make_slug(request: Request, name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30] or "business"
    while True:
        slug = f"{base}-{secrets.token_hex(2)}"
        if not find_one(request, BUSINESSES, lambda r: r.get("SLUG") == slug):
            return slug


def make_qr_slug(request: Request, name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30] or "qr"
    while True:
        slug = f"{base}-{secrets.token_hex(3)}"
        if not find_one(request, QR_CODES, lambda r: r.get("SLUG") == slug):
            return slug


@router.post("/register", status_code=201)
def register(data: RegisterIn, request: Request):
    email = data.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(422, "Enter a valid email address")
    if find_one(request, BUSINESSES, lambda r: str(r.get("EMAIL", "")).lower() == email):
        raise HTTPException(409, "An account with this email already exists")

    name = data.business_name.strip()
    business = insert(request, BUSINESSES, {
        "BUSINESS_NAME": name, "EMAIL": email, "PASSWORD_HASH": hash_password(data.password),
        "SLUG": make_slug(request, name), "CREATED_AT": now(),
    })
    business_id = str(business.get("ROWID") or business.get("id"))
    insert(request, QR_CODES, {
        "BUSINESS_ID": business_id, "QR_NAME": "Main QR code",
        "SLUG": make_qr_slug(request, name),
    })
    return {"token": create_token(business_id), "business_name": name}


@router.post("/login")
def login(data: LoginIn, request: Request):
    row = find_one(request, BUSINESSES, lambda r: str(r.get("EMAIL", "")).lower() == data.email.strip().lower())
    if row is None or not verify_password(data.password, row["PASSWORD_HASH"]):
        raise HTTPException(401, "Email or password is incorrect")
    return {
        "token": create_token(str(row.get("ROWID") or row.get("id"))),
        "business_name": row["BUSINESS_NAME"],
    }
