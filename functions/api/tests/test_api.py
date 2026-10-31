import os

os.environ["DB_PATH"] = "/tmp/dynamic-qr-generator-test.db"
os.environ["SECRET_KEY"] = "test-secret-012345678901234567890123"

from fastapi.testclient import TestClient

from db import init_db
from main import app


def setup_function():
    try:
        os.remove(os.environ["DB_PATH"])
    except FileNotFoundError:
        pass
    init_db()


def test_health():
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_login_and_public_page():
    client = TestClient(app)
    registration = client.post(
        "/api/auth/register",
        json={
            "business_name": "Test Cafe",
            "email": "owner@example.com",
            "password": "password123",
        },
    )
    assert registration.status_code == 201
    token = registration.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile = client.get("/api/business/me", headers=headers)
    assert profile.status_code == 200
    slug = profile.json()["slug"]

    content = client.post(
        "/api/content",
        headers=headers,
        data={"title": "Welcome", "type": "text", "text_value": "Open daily"},
    )
    assert content.status_code == 201

    public = client.get(f"/api/public/{slug}")
    assert public.status_code == 200
    assert public.json()["business_name"] == "Test Cafe"
    assert public.json()["items"][0]["text"] == "Open daily"
