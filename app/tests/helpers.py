"""
Funções auxiliares para os testes de integração.

Não são fixtures (não usam @pytest.fixture) porque cada teste precisa
de combinações diferentes (papéis diferentes, quantidades diferentes
de clientes/aeronaves) — funções simples, chamadas explicitamente
dentro de cada teste, são mais claras aqui do que fixtures genéricas
demais.
"""
from fastapi.testclient import TestClient

SENHA_PADRAO = "SenhaForte123"


def registrar_e_logar(client: TestClient, role: str, email: str) -> str:
    client.post(
        "/auth/register",
        json={"full_name": f"Usuario {role}", "email": email, "password": SENHA_PADRAO, "role": role},
    )
    resp = client.post("/auth/login", json={"email": email, "password": SENHA_PADRAO})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def criar_cliente_pf(client: TestClient, headers: dict, cpf: str = "111.444.777-35") -> dict:
    resp = client.post(
        "/clientes",
        headers=headers,
        json={"tipo_pessoa": "fisica", "nome": "Cliente de Teste", "cpf": cpf},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def criar_motor(client: TestClient, headers: dict, numero_serie: str = "MOT-TESTE-0001") -> dict:
    resp = client.post(
        "/motores",
        headers=headers,
        json={
            "fabricante": "Lycoming",
            "modelo": "O-360",
            "numero_serie": numero_serie,
            "tsn": 100,
            "tso": 50,
            "tbo": 2000,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def criar_aeronave(
    client: TestClient,
    headers: dict,
    cliente_id: str,
    motor_id: str | None = None,
    prefixo: str = "PT-TST",
    numero_serie: str = "SN-TESTE-0001",
) -> dict:
    payload = {
        "prefixo": prefixo,
        "fabricante": "Cessna",
        "modelo": "172",
        "numero_serie": numero_serie,
        "ano": 2020,
        "categoria": "monomotor",
        "cliente_id": cliente_id,
    }
    if motor_id is not None:
        payload["motor_id"] = motor_id

    resp = client.post("/aeronaves", headers=headers, json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()
