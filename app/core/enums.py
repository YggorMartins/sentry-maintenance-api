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
