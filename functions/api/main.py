from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config import CLIENT_DIR
from routes import auth, business, content, public


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Dynamic QR Code Generator", lifespan=lifespan)


@app.middleware("http")
async def catalyst_request_context(request, call_next):
    path = request.scope["path"]
    is_api_or_public = path.startswith(("/api/", "/q/", "/b/", "/files/"))
    is_static_asset = os.path.splitext(path.rsplit("/", 1)[-1])[1] != ""
    if not is_api_or_public and not is_static_asset and path != "/":
        request.scope["path"] = "/"

    # Catalyst injects this port only in AppSail. Avoid initializing the SDK
    # during ordinary local development, where Catalyst credentials are absent.
    if os.getenv("X_ZOHO_CATALYST_LISTEN_PORT"):
        import zcatalyst_sdk
        request.state.catalyst = zcatalyst_sdk.initialize(req=request)
    else:
        request.state.catalyst = None
    return await call_next(request)

app.include_router(auth.router)
app.include_router(business.router)
app.include_router(content.router)
app.include_router(public.router)

# Mounted last: serves client/index.html, styles.css, app.js, assets/
app.mount("/", StaticFiles(directory=CLIENT_DIR, html=True), name="client")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("X_ZOHO_CATALYST_LISTEN_PORT", os.getenv("PORT", "8000"))),
    )
