"""Enums de domínio compartilhados entre models e schemas."""
import enum


class TipoPessoa(str, enum.Enum):
    FISICA = "fisica"
    JURIDICA = "juridica"


class CategoriaAeronave(str, enum.Enum):
    MONOMOTOR = "monomotor"
    MULTIMOTOR = "multimotor"
    HELICOPTERO = "helicoptero"
    TURBOPROP = "turboprop"
    JATO = "jato"


class StatusAeronave(str, enum.Enum):
    ATIVA = "ativa"
    EM_MANUTENCAO = "em_manutencao"
    INATIVA = "inativa"


class StatusOS(str, enum.Enum):
    ABERTA = "aberta"
    EM_ANDAMENTO = "em_andamento"
    AGUARDANDO_PECAS = "aguardando_pecas"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class TipoInspecao(str, enum.Enum):
    CINQUENTA_HORAS = "50_horas"
    CEM_HORAS = "100_horas"
    ANUAL = "anual"
    ESPECIAL = "especial"
    PROGRESSIVA = "progressiva"


class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class TipoManutencao(str, enum.Enum):
    PREVENTIVA = "preventiva"
    CORRETIVA = "corretiva"
    INSPECAO = "inspecao"
    PREDITIVA = "preditiva"


class CategoriaManutencao(str, enum.Enum):
    AVIONICOS = "avionicos"
    MECANICA = "mecanica"
    ESTRUTURA = "estrutura"
    MOTOR = "motor"


class RecorrenciaManutencao(str, enum.Enum):
    NENHUMA = "nenhuma"
    SEMANAL = "semanal"
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    ANUAL = "anual"


class StatusAgendamento(str, enum.Enum):
    AGENDADO = "agendado"
    CONFIRMADO = "confirmado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class TipoEntidadeAnexo(str, enum.Enum):
    AERONAVE = "aeronave"
    ORDEM_SERVICO = "ordem_servico"
    CLIENTE = "cliente"
    INSPECAO = "inspecao"
