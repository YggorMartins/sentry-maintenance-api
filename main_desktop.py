"""Entrada do aplicativo desktop Windows (FastAPI + pywebview)."""

from __future__ import annotations

import os
import secrets
import socket
import threading
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


APP_TITLE = "Sentry Maintenance System - CTM Desktop"


def _desktop_data_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    path = base / "SentryMaintenance"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _persistent_secret(data_dir: Path) -> str:
    secret_file = data_dir / ".desktop-secret"
    try:
        value = secret_file.read_text(encoding="utf-8").strip()
        if len(value) >= 32:
            return value
    except FileNotFoundError:
        pass

    value = secrets.token_hex(32)
    secret_file.write_text(value, encoding="utf-8")
    return value


def configure_desktop_environment() -> Path:
    """Define defaults locais antes de importar a aplicação FastAPI."""
    data_dir = _desktop_data_dir()
    database_path = (data_dir / "sentry-maintenance.db").as_posix()
    uploads_path = (data_dir / "uploads").as_posix()

    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("DEBUG", "False")
    os.environ.setdefault("DATABASE_URL", f"sqlite+pysqlite:///{database_path}")
    os.environ.setdefault("SECRET_KEY", _persistent_secret(data_dir))
    os.environ.setdefault("RATE_LIMIT_ENABLED", "False")
    os.environ.setdefault("CORS_ORIGINS", "http://127.0.0.1")
    os.environ.setdefault("ALLOWED_HOSTS", "127.0.0.1,localhost")
    os.environ.setdefault("UPLOAD_DIR", uploads_path)
    return data_dir


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_until_ready(url: str, timeout: float = 15.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(f"{url}/health", timeout=0.5) as response:
                if response.status == 200:
                    return True
        except (OSError, URLError):
            time.sleep(0.1)
    return False


def main() -> None:
    configure_desktop_environment()

    # Imports tardios garantem que pydantic-settings leia os defaults desktop.
    import uvicorn
    import webview

    from app.database.session import Base, engine
    from app.main import app

    Base.metadata.create_all(bind=engine)
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    backend = threading.Thread(target=server.run, daemon=True, name="sentry-api")
    backend.start()

    if _wait_until_ready(base_url):
        target = base_url
    else:
        target = (
            "data:text/html,<h2>Sentry Maintenance</h2>"
            "<p>Não foi possível iniciar o servidor local. Consulte os logs do aplicativo.</p>"
        )

    webview.create_window(APP_TITLE, target, width=1280, height=800, min_size=(1024, 680))
    webview.start()
    server.should_exit = True


if __name__ == "__main__":
    main()
