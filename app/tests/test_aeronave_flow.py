"""Testes de integração de Aeronaves."""
from app.tests.helpers import auth_headers, criar_aeronave, criar_cliente_pf, criar_motor, registrar_e_logar


def test_criar_aeronave_com_motor_e_proprietario_validos(client):
    token = registrar_e_logar(client, role="admin", email="admin_aer@teste.com")
    headers = auth_headers(token)

    cliente = criar_cliente_pf(client, headers, cpf="112.233.445-17")
    motor = criar_motor(client, headers, numero_serie="MOT-AER-0001")

    aeronave = criar_aeronave(client, headers, cliente_id=cliente["id"], motor_id=motor["id"])

    assert aeronave["prefixo"] == "PT-TST"
    assert aeronave["motor"]["id"] == motor["id"]


def test_nao_permite_dois_aeronaves_com_mesmo_motor(client):
    token = registrar_e_logar(client, role="admin", email="admin_aer2@teste.com")
    headers = auth_headers(token)

    cliente = criar_cliente_pf(client, headers, cpf="998.877.665-93")
    motor = criar_motor(client, headers, numero_serie="MOT-AER-0002")

    criar_aeronave(
        client, headers, cliente_id=cliente["id"], motor_id=motor["id"],
        prefixo="PT-AAA", numero_serie="SN-AER-0001",
    )

    resp = client.post(
        "/aeronaves",
        headers=headers,
        json={
            "prefixo": "PT-BBB",
            "fabricante": "Cessna",
            "modelo": "172",
            "numero_serie": "SN-AER-0002",
            "ano": 2021,
            "categoria": "monomotor",
            "cliente_id": cliente["id"],
            "motor_id": motor["id"],
        },
    )
    assert resp.status_code == 409


def test_criar_aeronave_com_proprietario_inexistente_retorna_400(client):
    token = registrar_e_logar(client, role="admin", email="admin_aer3@teste.com")
    headers = auth_headers(token)

    resp = client.post(
        "/aeronaves",
        headers=headers,
        json={
            "prefixo": "PT-CCC",
            "fabricante": "Cessna",
            "modelo": "172",
            "numero_serie": "SN-AER-0003",
            "ano": 2021,
            "categoria": "monomotor",
            "cliente_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert resp.status_code == 400
