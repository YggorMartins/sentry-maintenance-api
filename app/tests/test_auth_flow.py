"""Testes de integração de Autenticação."""
from app.tests.helpers import SENHA_PADRAO, auth_headers, registrar_e_logar


def test_registro_login_e_me_retornam_dados_consistentes(client):
    token = registrar_e_logar(client, role="admin", email="admin@teste.com")

    resp = client.get("/auth/me", headers=auth_headers(token))

    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "admin@teste.com"
    assert body["role"] == "admin"


def test_login_com_senha_incorreta_retorna_401(client):
    client.post(
        "/auth/register",
        json={"full_name": "Fulano", "email": "fulano@teste.com", "password": SENHA_PADRAO, "role": "cliente"},
    )
    resp = client.post("/auth/login", json={"email": "fulano@teste.com", "password": "senhaErrada"})
    assert resp.status_code == 401


def test_me_sem_token_retorna_401(client):
    resp = client.get("/auth/me")
    assert resp.status_code in (401, 403)


def test_refresh_gera_novo_par_e_revoga_o_antigo(client):
    client.post(
        "/auth/register",
        json={"full_name": "Ciclano", "email": "ciclano@teste.com", "password": SENHA_PADRAO, "role": "admin"},
    )
    login = client.post("/auth/login", json={"email": "ciclano@teste.com", "password": SENHA_PADRAO})
    refresh_token_original = login.json()["refresh_token"]

    resp_refresh = client.post("/auth/refresh", json={"refresh_token": refresh_token_original})
    assert resp_refresh.status_code == 200

    # O refresh token ORIGINAL já foi rotacionado (revogado) — tentar
    # usá-lo de novo deve falhar.
    resp_refresh_repetido = client.post("/auth/refresh", json={"refresh_token": refresh_token_original})
    assert resp_refresh_repetido.status_code == 401


def test_logout_revoga_refresh_token(client):
    client.post(
        "/auth/register",
        json={"full_name": "Beltrano", "email": "beltrano@teste.com", "password": SENHA_PADRAO, "role": "admin"},
    )
    login = client.post("/auth/login", json={"email": "beltrano@teste.com", "password": SENHA_PADRAO})
    refresh_token = login.json()["refresh_token"]

    resp_logout = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert resp_logout.status_code == 204

    resp_refresh_apos_logout = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp_refresh_apos_logout.status_code == 401
