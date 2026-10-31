import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "client"))

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
SECRET_KEY = os.getenv("SECRET_KEY", "")
TOKEN_DAYS = max(1, min(int(os.getenv("TOKEN_DAYS", "7")), 30))

DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "data.db"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024

# Set this to your real domain (e.g. https://menu.example.com) so the QR code
# never changes, even if the app is reached through a proxy or another host name.
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")

if ENVIRONMENT == "production":
    if len(SECRET_KEY) < 32:
        raise RuntimeError("SECRET_KEY must be at least 32 characters in production")
    if not BASE_URL.startswith("https://"):
        raise RuntimeError("BASE_URL must be an HTTPS URL in production")
elif not SECRET_KEY:
    SECRET_KEY = "local-development-only-change-me"

os.makedirs(UPLOAD_DIR, exist_ok=True)
