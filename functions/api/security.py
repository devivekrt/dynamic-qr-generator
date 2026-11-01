import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import SECRET_KEY, TOKEN_DAYS
from catalyst_store import BUSINESSES, find_one

_ITERATIONS = 200_000
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$")
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), _ITERATIONS
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except ValueError:
        return False


def create_token(business_id: int) -> str:
    payload = {
        "sub": str(business_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def current_business(
    request: Request, creds: HTTPAuthorizationCredentials = Depends(bearer)
):
    """Returns the logged-in business row or raises 401."""
    if creds is None:
        raise HTTPException(401, "Log in to continue")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=["HS256"])
        business_id = str(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(401, "Session expired. Log in again")
    row = find_one(request, BUSINESSES, lambda r: str(r.get("ROWID") or r.get("id")) == business_id)
    if row is None:
        raise HTTPException(401, "Account not found")
    return row
