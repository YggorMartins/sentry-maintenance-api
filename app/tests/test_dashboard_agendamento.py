from datetime import datetime, timedelta, timezone

from app.tests.helpers import auth_headers, criar_aeronave, criar_cliente_pf, registrar_e_logar


def _aeronave(client, headers):
    cliente = criar_cliente_pf(client, headers, cpf="529.982.247-25")
    return criar_aeronave(
        client, headers, cliente_id=cliente["id"], prefixo="PT-DAS", numero_serie="SN-DASH-001"
    )


def test_dashboard_retorna_kpis_e_ordens_ativas(client):
    token = registrar_e_logar(client, role="admin", email="dashboard@teste.com")
    headers = auth_headers(token)
    aeronave = _aeronave(client, headers)
    criada = client.post(
        "/ordens-servico",
        headers=headers,
        json={
            "aeronave_id": aeronave["id"],
            "descricao": "Inspeção programada de aviônicos",
            "tipo_manutencao": "preventiva",
            "categoria": "avionicos",
            "custo_estimado": 12500,
        },
    )
    assert criada.status_code == 201, criada.text

    resposta = client.get("/dashboard/resumo", headers=headers)
    assert resposta.status_code == 200, resposta.text
    body = resposta.json()
    assert body["kpis"]["manutencoes_ativas"] == 1
    assert body["kpis"]["custo_total"] == 12500
    assert body["ordens_ativas"][0]["ativo"] == "PT-DAS"


def test_cria_e_lista_agendamento_recorrente(client):
    token = registrar_e_logar(client, role="admin", email="agenda@teste.com")
    headers = auth_headers(token)
    aeronave = _aeronave(client, headers)
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    resposta = client.post(
        "/agendamentos",
        headers=headers,
        json={
            "aeronave_id": aeronave["id"],
            "titulo": "Inspeção mensal",
            "inicio": inicio.isoformat(),
            "fim": (inicio + timedelta(hours=3)).isoformat(),
            "tipo": "preventiva",
            "recorrencia": "mensal",
            "recorrencia_ate": (inicio + timedelta(days=180)).isoformat(),
        },
    )
    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["recorrencia"] == "mensal"

    listagem = client.get("/agendamentos", headers=headers)
    assert listagem.status_code == 200
    assert listagem.json()["total"] == 1


def test_dashboard_exige_autenticacao(client):
    assert client.get("/dashboard/resumo").status_code == 401
