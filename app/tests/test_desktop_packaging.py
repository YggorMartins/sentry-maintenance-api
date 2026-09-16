from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.spa import SPAStaticFiles
from main_desktop import configure_desktop_environment


def test_spa_static_files_entrega_index_para_rota_react(tmp_path):
    (tmp_path / "index.html").write_text("<main>Sentry Desktop</main>", encoding="utf-8")
    (tmp_path / "asset.js").write_text("console.log('ok')", encoding="utf-8")
    test_app = FastAPI()
    test_app.mount("/", SPAStaticFiles(directory=tmp_path, html=True))

    with TestClient(test_app) as client:
        assert client.get("/dashboard").text == "<main>Sentry Desktop</main>"
        assert client.get("/asset.js").status_code == 200
        assert client.get("/arquivo-inexistente.js").status_code == 404


def test_configuracao_desktop_cria_defaults_persistentes(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    for name in (
        "DATABASE_URL", "SECRET_KEY", "UPLOAD_DIR", "RATE_LIMIT_ENABLED",
        "CORS_ORIGINS", "ALLOWED_HOSTS",
    ):
        monkeypatch.delenv(name, raising=False)

    data_dir = configure_desktop_environment()
    primeiro_segredo = (data_dir / ".desktop-secret").read_text(encoding="utf-8")
    monkeypatch.delenv("SECRET_KEY")
    configure_desktop_environment()

    assert data_dir == tmp_path / "SentryMaintenance"
    assert "sentry-maintenance.db" in __import__("os").environ["DATABASE_URL"]
    assert len(primeiro_segredo) == 64
    assert __import__("os").environ["SECRET_KEY"] == primeiro_segredo
