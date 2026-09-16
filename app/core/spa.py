"""Servidor de arquivos do frontend com fallback para o React Router."""

from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles


class SPAStaticFiles(StaticFiles):
    """Entrega ``index.html`` para rotas que pertencem à SPA.

    Assets inexistentes continuam retornando 404; o fallback só é usado para
    URLs sem extensão, como ``/dashboard`` e ``/estoque``.
    """

    async def get_response(self, path: str, scope: dict) -> Response:
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code == 404 and "." not in path.rsplit("/", 1)[-1]:
                return await super().get_response("index.html", scope)
            raise
