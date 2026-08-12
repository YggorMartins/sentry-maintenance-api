"""Testes de integração de Clientes."""
from app.tests.helpers import auth_headers, criar_cliente_pf, registrar_e_logar


def test_criar_cliente_pf_com_cpf_valido(client):
    token = registrar_e_logar(client, role="admin", email="admin_cli@teste.com")
    body = criar_cliente_pf(client, auth_headers(token))
    assert body["tipo_pessoa"] == "fisica"
    assert body["cpf"] == "11144477735"


def test_criar_cliente_com_cpf_duplicado_retorna_409(client):
    token = registrar_e_logar(client, role="admin", email="admin_dup@teste.com")
    headers = auth_headers(token)

    criar_cliente_pf(client, headers, cpf="123.456.789-09")
    resp = client.post(
        "/clientes",
        headers=headers,
        json={"tipo_pessoa": "fisica", "nome": "Outro Nome", "cpf": "123.456.789-09"},
    )
    assert resp.status_code == 409


def test_criar_cliente_com_cpf_invalido_retorna_422(client):
    token = registrar_e_logar(client, role="admin", email="admin_inv@teste.com")
    resp = client.post(
        "/clientes",
        headers=auth_headers(token),
        json={"tipo_pessoa": "fisica", "nome": "Nome Qualquer", "cpf": "111.111.111-11"},
    )
    assert resp.status_code == 422


def test_listar_clientes_sem_autenticacao_retorna_401(client):
    resp = client.get("/clientes")
    assert resp.status_code in (401, 403)


def test_mecanico_nao_pode_excluir_cliente(client):
    admin_token = registrar_e_logar(client, role="admin", email="admin_rbac@teste.com")
    cliente = criar_cliente_pf(client, auth_headers(admin_token), cpf="987.654.321-00")

    mecanico_token = registrar_e_logar(client, role="mecanico", email="mecanico_rbac@teste.com")
    resp = client.delete(f"/clientes/{cliente['id']}", headers=auth_headers(mecanico_token))

    assert resp.status_code == 403
