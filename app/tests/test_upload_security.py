import io
import zipfile

from app.services.anexo_service import AnexoService


def _minimal_docx() -> bytes:
    content = io.BytesIO()
    with zipfile.ZipFile(content, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("word/document.xml", "<document />")
    return content.getvalue()


def test_upload_detecta_formatos_por_assinatura():
    assert AnexoService.detectar_content_type(b"%PDF-1.7\n") == "application/pdf"
    assert AnexoService.detectar_content_type(b"\x89PNG\r\n\x1a\nresto") == "image/png"
    assert AnexoService.detectar_content_type(b"\xff\xd8\xffresto") == "image/jpeg"
    assert AnexoService.detectar_content_type(_minimal_docx()) == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_upload_rejeita_conteudo_disfarcado_por_extensao():
    assert AnexoService.detectar_content_type(b"nao e um pdf") is None


def test_nome_do_upload_remove_componentes_de_caminho():
    assert AnexoService._sanitizar_nome_arquivo("../../segredo.pdf") == "segredo.pdf"
