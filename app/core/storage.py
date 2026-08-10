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
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, subdir: str, filename: str) -> str:
        destino_dir = self.base_dir / subdir
        destino_dir.mkdir(parents=True, exist_ok=True)

        nome_unico = f"{uuid.uuid4().hex}_{filename}"
        destino = destino_dir / nome_unico
        destino.write_bytes(content)

        # Caminho relativo (independente de sistema operacional), é isso
        # que fica salvo no banco em Anexo.caminho_arquivo.
        return f"{subdir}/{nome_unico}"

    def delete(self, caminho_relativo: str) -> None:
        caminho = self.base_dir / caminho_relativo
        caminho.unlink(missing_ok=True)

    def get_full_path(self, caminho_relativo: str) -> Path:
        return self.base_dir / caminho_relativo


def get_storage_backend() -> StorageBackend:
    """Dependency do FastAPI — ÚNICO lugar que decide qual backend está ativo."""
    return LocalStorageBackend()
