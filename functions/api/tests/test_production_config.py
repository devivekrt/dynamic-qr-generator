import os
import subprocess
import sys


def test_production_rejects_short_secret(tmp_path):
    env = os.environ.copy()
    env.update(
        {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "too-short",
            "BASE_URL": "https://example.com",
            "DB_PATH": str(tmp_path / "data.db"),
            "UPLOAD_DIR": str(tmp_path / "uploads"),
        }
    )
    result = subprocess.run(
        [sys.executable, "-c", "import config"],
        cwd=os.path.dirname(__file__) + "/..",
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr
