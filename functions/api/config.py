import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILT_CLIENT_DIR = os.path.join(BASE_DIR, "client")
SOURCE_CLIENT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "client"))
CLIENT_DIR = BUILT_CLIENT_DIR if os.path.isfile(os.path.join(BUILT_CLIENT_DIR, "index.html")) else SOURCE_CLIENT_DIR

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
TOKEN_DAYS = int(os.getenv("TOKEN_DAYS", "7"))

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024

# Set this to your real domain (e.g. https://menu.example.com) so the QR code
# never changes, even if the app is reached through a proxy or another host name.
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
