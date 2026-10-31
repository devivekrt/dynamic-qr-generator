from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config import CLIENT_DIR, UPLOAD_DIR
from db import init_db
from routes import auth, business, content, public


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Dynamic QR Code Generator", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(business.router)
app.include_router(content.router)
app.include_router(public.router)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
# Mounted last: serves client/index.html, styles.css, app.js, assets/
app.mount("/", StaticFiles(directory=CLIENT_DIR, html=True), name="client")
