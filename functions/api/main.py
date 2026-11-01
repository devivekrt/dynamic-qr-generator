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
    import zcatalyst_sdk
    request.state.catalyst = zcatalyst_sdk.initialize(req=request)
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
