"""
Teste unitário do LocalStorageBackend.

Usa um diretório temporário (fixture `tmp_path` do pytest) — não toca
no diretório real de uploads da aplicação nem depende de banco.
"""
from app.core.storage import LocalStorageBackend


def test_save_cria_arquivo_e_retorna_caminho_relativo(tmp_path):
    storage = LocalStorageBackend(base_dir=str(tmp_path))
    caminho = storage.save(b"conteudo de teste", "ordem_servico/abc123", "laudo.pdf")

    assert caminho.startswith("ordem_servico/abc123/")
    assert caminho.endswith("_laudo.pdf")

    caminho_absoluto = storage.get_full_path(caminho)
    assert caminho_absoluto.exists()
    assert caminho_absoluto.read_bytes() == b"conteudo de teste"


def test_save_gera_nomes_unicos_para_mesmo_arquivo(tmp_path):
    storage = LocalStorageBackend(base_dir=str(tmp_path))
    caminho1 = storage.save(b"a", "aeronave/x", "certificado.pdf")
    caminho2 = storage.save(b"b", "aeronave/x", "certificado.pdf")
    assert caminho1 != caminho2


def test_delete_remove_arquivo_do_disco(tmp_path):
    storage = LocalStorageBackend(base_dir=str(tmp_path))
    caminho = storage.save(b"conteudo", "cliente/y", "doc.pdf")
    caminho_absoluto = storage.get_full_path(caminho)
    assert caminho_absoluto.exists()

    storage.delete(caminho)
    assert not caminho_absoluto.exists()


def test_delete_de_arquivo_inexistente_nao_gera_erro(tmp_path):
    storage = LocalStorageBackend(base_dir=str(tmp_path))
    # missing_ok=True no unlink() garante que isso não levanta exceção.
    storage.delete("caminho/que/nao/existe.pdf")
