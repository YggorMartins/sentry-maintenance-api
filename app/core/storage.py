"""
Abstração de armazenamento de arquivos.

`StorageBackend` é a interface. Hoje só existe `LocalStorageBackend`
(disco local). Quando for migrar pra AWS S3, crie `S3StorageBackend`
implementando a mesma interface e troque a instância retornada por
`get_storage_backend()` — nada no resto do sistema (service, router)
precisa mudar. Ver explicação completa na conversa da Etapa 7.
"""
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from app.config.settings import settings


class StorageBackend(ABC):
    @abstractmethod
    def save(self, content: bytes, subdir: str, filename: str) -> str:
        """Salva o conteúdo e retorna o caminho relativo onde foi salvo."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, caminho_relativo: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_full_path(self, caminho_relativo: str) -> Path:
        """Retorna o caminho absoluto/local para servir o arquivo (download)."""
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_dir: str = settings.UPLOAD_DIR):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, caminho_relativo: str) -> Path:
        relative = Path(caminho_relativo)
        if relative.is_absolute():
            raise ValueError("Caminho absoluto não é permitido no armazenamento.")
        candidate = (self.base_dir / relative).resolve()
        if not candidate.is_relative_to(self.base_dir):
            raise ValueError("Caminho fora do diretório de uploads.")
        return candidate

    def save(self, content: bytes, subdir: str, filename: str) -> str:
        if Path(filename).name != filename or filename in {"", ".", ".."}:
            raise ValueError("Nome de arquivo inválido.")

        destino_dir = self._safe_path(subdir)
        destino_dir.mkdir(parents=True, exist_ok=True)

        nome_unico = f"{uuid.uuid4().hex}_{filename}"
        destino = destino_dir / nome_unico
        destino.write_bytes(content)

        # Caminho relativo (independente de sistema operacional), é isso
        # que fica salvo no banco em Anexo.caminho_arquivo.
        return f"{subdir}/{nome_unico}"

    def delete(self, caminho_relativo: str) -> None:
        caminho = self._safe_path(caminho_relativo)
        caminho.unlink(missing_ok=True)

    def get_full_path(self, caminho_relativo: str) -> Path:
        return self._safe_path(caminho_relativo)


def get_storage_backend() -> StorageBackend:
    """Dependency do FastAPI — ÚNICO lugar que decide qual backend está ativo."""
    return LocalStorageBackend()
