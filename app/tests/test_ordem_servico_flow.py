"""Testes de integração de Ordens de Serviço."""
from app.tests.helpers import auth_headers, criar_aeronave, criar_cliente_pf, registrar_e_logar


def _preparar_aeronave(client, headers, sufixo: str) -> dict:
    cliente = criar_cliente_pf(client, headers, cpf="123.456.789-09" if sufixo == "A" else "987.654.321-00")
    aeronave = criar_aeronave(
        client, headers, cliente_id=cliente["id"], prefixo=f"PT-{sufixo}OS", numero_serie=f"SN-OS-{sufixo}"
    )
    return aeronave


def test_criar_os_gera_numero_automatico_e_status_aberta(client):
    token = registrar_e_logar(client, role="admin", email="admin_os1@teste.com")
    headers = auth_headers(token)
    aeronave = _preparar_aeronave(client, headers, "A")

    resp = client.post(
        "/ordens-servico",
        headers=headers,
        json={"aeronave_id": aeronave["id"], "descricao": "Revisão de 100 horas"},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "aberta"
    assert body["numero"].startswith("OS-")
    assert body["data_fechamento"] is None


def test_nao_permite_pular_direto_para_concluida(client):
    token = registrar_e_logar(client, role="admin", email="admin_os2@teste.com")
    headers = auth_headers(token)
    aeronave = _preparar_aeronave(client, headers, "B")

    os_criada = client.post(
        "/ordens-servico", headers=headers, json={"aeronave_id": aeronave["id"], "descricao": "Troca de óleo"}
    ).json()

    resp = client.patch(
        f"/ordens-servico/{os_criada['id']}/status", headers=headers, json={"status": "concluida"}
    )
    assert resp.status_code == 409


def test_fluxo_completo_de_status_preenche_data_fechamento(client):
    token = registrar_e_logar(client, role="admin", email="admin_os3@teste.com")
    headers = auth_headers(token)
    aeronave = _preparar_aeronave(client, headers, "C")

    os_id = client.post(
        "/ordens-servico", headers=headers, json={"aeronave_id": aeronave["id"], "descricao": "Inspeção anual"}
    ).json()["id"]

    resp_em_andamento = client.patch(
        f"/ordens-servico/{os_id}/status", headers=headers, json={"status": "em_andamento"}
    )
    assert resp_em_andamento.status_code == 200
    assert resp_em_andamento.json()["data_fechamento"] is None

    resp_concluida = client.patch(
        f"/ordens-servico/{os_id}/status", headers=headers, json={"status": "concluida"}
    )
    assert resp_concluida.status_code == 200
    assert resp_concluida.json()["data_fechamento"] is not None


def test_nao_permite_editar_os_ja_concluida(client):
    token = registrar_e_logar(client, role="admin", email="admin_os4@teste.com")
    headers = auth_headers(token)
    aeronave = _preparar_aeronave(client, headers, "D")

    os_id = client.post(
        "/ordens-servico", headers=headers, json={"aeronave_id": aeronave["id"], "descricao": "Revisão geral"}
    ).json()["id"]

    client.patch(f"/ordens-servico/{os_id}/status", headers=headers, json={"status": "em_andamento"})
    client.patch(f"/ordens-servico/{os_id}/status", headers=headers, json={"status": "concluida"})

    resp_edicao = client.put(
        f"/ordens-servico/{os_id}",
        headers=headers,
        json={"descricao": "Tentativa de edição pós-conclusão", "horas_trabalhadas": 5},
    )
    assert resp_edicao.status_code == 409
