from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles

from config import CLIENT_DIR, ENVIRONMENT, UPLOAD_DIR
from db import connect, init_db
from routes import auth, business, content, public


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Dynamic QR Code Generator",
    lifespan=lifespan,
    docs_url=None if ENVIRONMENT == "production" else "/docs",
    redoc_url=None if ENVIRONMENT == "production" else "/redoc",
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        if request.url.scheme == "https":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.include_router(auth.router)
app.include_router(business.router)
app.include_router(content.router)
app.include_router(public.router)

@app.get("/api/health", tags=["system"])
def health():
    db = connect()
    try:
        db.execute("SELECT 1")
    finally:
        db.close()
    return {"status": "ok", "service": "dynamic-qr-generator"}

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
# Mounted last: serves client/index.html, styles.css, app.js, assets/
app.mount("/", StaticFiles(directory=CLIENT_DIR, html=True), name="client")
