"""
Teste unitário da tabela de transições de status da Ordem de Serviço.

A tabela é uma estrutura de dados pura (dict), então testamos direto,
sem precisar instanciar o service com uma sessão de banco real.
"""
from app.core.enums import StatusOS
from app.services.ordem_servico_service import ESTADOS_TERMINAIS, TRANSICOES_PERMITIDAS


def test_aberta_pode_ir_para_em_andamento_ou_cancelada():
    assert TRANSICOES_PERMITIDAS[StatusOS.ABERTA] == {StatusOS.EM_ANDAMENTO, StatusOS.CANCELADA}


def test_aberta_nao_pode_ir_direto_para_concluida():
    assert StatusOS.CONCLUIDA not in TRANSICOES_PERMITIDAS[StatusOS.ABERTA]


def test_em_andamento_pode_ir_para_aguardando_pecas_concluida_ou_cancelada():
    assert TRANSICOES_PERMITIDAS[StatusOS.EM_ANDAMENTO] == {
        StatusOS.AGUARDANDO_PECAS,
        StatusOS.CONCLUIDA,
        StatusOS.CANCELADA,
    }


def test_estados_terminais_nao_tem_transicoes_de_saida():
    assert TRANSICOES_PERMITIDAS[StatusOS.CONCLUIDA] == set()
    assert TRANSICOES_PERMITIDAS[StatusOS.CANCELADA] == set()


def test_estados_terminais_contem_concluida_e_cancelada():
    assert ESTADOS_TERMINAIS == {StatusOS.CONCLUIDA, StatusOS.CANCELADA}
