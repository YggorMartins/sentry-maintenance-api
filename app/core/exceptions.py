"""
Exceções customizadas.

Services levantam essas exceções de domínio (sem saber nada de HTTP).
Os routers (ou um exception handler global, na Etapa 8) traduzem para
o status HTTP apropriado. Isso mantém a camada de serviço desacoplada
do FastAPI.
"""


class InvalidCredentialsError(Exception):
    """Email ou senha incorretos."""


class InactiveUserError(Exception):
    """Usuário existe mas está desativado."""


class InvalidTokenError(Exception):
    """Token ausente, malformado, expirado ou revogado."""


class UserAlreadyExistsError(Exception):
    """Já existe um usuário com esse email."""


class ClienteAlreadyExistsError(Exception):
    """Já existe um cliente cadastrado com esse CPF/CNPJ."""


class ClienteNotFoundError(Exception):
    """Cliente não encontrado."""


class ClienteEmUsoError(Exception):
    """Cliente não pode ser removido pois possui aeronaves vinculadas."""


class MotorAlreadyExistsError(Exception):
    """Já existe um motor cadastrado com esse número de série."""


class MotorNotFoundError(Exception):
    """Motor não encontrado."""


class AeronaveAlreadyExistsError(Exception):
    """Já existe uma aeronave cadastrada com esse prefixo ou número de série."""


class AeronaveNotFoundError(Exception):
    """Aeronave não encontrada."""


class MotorJaInstaladoError(Exception):
    """O motor informado já está instalado em outra aeronave."""


class ProprietarioNotFoundError(Exception):
    """O cliente (proprietário) informado não existe."""


class OrdemServicoNotFoundError(Exception):
    """Ordem de serviço não encontrada."""


class TransicaoStatusInvalidaError(Exception):
    """A transição de status solicitada não é permitida a partir do status atual."""


class ResponsavelInvalidoError(Exception):
    """O usuário informado como mecânico/inspetor não existe ou não tem o papel correto."""


class OrdemServicoNaoEditavelError(Exception):
    """A ordem de serviço está em status terminal (concluída/cancelada) e não pode ser editada."""


class InspecaoNotFoundError(Exception):
    """Inspeção não encontrada."""
