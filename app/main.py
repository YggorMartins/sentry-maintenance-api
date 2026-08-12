"""
Ponto de entrada da aplicação.

Monta a aplicação FastAPI, registra logging, middlewares (CORS +
logging de requisições), o exception handler global de segurança, e
todos os routers de negócio construídos ao longo das Etapas 1-7.
"""
import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.core.logging import setup_logging
from app.routers import aeronave as aeronave_router
from app.routers import anexo as anexo_router
from app.routers import auth as auth_router
from app.routers import cliente as cliente_router
from app.routers import inspecao as inspecao_router
from app.routers import motor as motor_router
from app.routers import movimentacao as movimentacao_router
from app.routers import ordem_servico as ordem_servico_router
from app.routers import peca as peca_router

setup_logging()
logger = logging.getLogger("sentry_api")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API de gestão de manutenção aeronáutica.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS] if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Loga método, rota, status e duração de cada requisição. Essencial
    pra investigar problemas em produção sem precisar reproduzir o bug
    manualmente — a primeira coisa que você olha é o log.
    """
    inicio = time.perf_counter()
    response = await call_next(request)
    duracao_ms = (time.perf_counter() - inicio) * 1000

    logger.info(
        '%s %s -> %d (%.1fms)',
        request.method,
        request.url.path,
        response.status_code,
        duracao_ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Rede de segurança para qualquer exceção NÃO prevista (bug, falha de
    infra). Sem isso, o FastAPI devolveria o stack trace completo pro
    cliente da API — um vazamento de informação interna. Logamos o
    erro real no servidor (pra você debugar) e devolvemos uma mensagem
    genérica e segura pro cliente.
    """
    logger.exception("Erro não tratado em %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor. Tente novamente mais tarde."},
    )


app.include_router(auth_router.router)
app.include_router(cliente_router.router)
app.include_router(motor_router.router)
app.include_router(aeronave_router.router)
app.include_router(ordem_servico_router.router)
app.include_router(inspecao_router.router)
app.include_router(peca_router.router)
app.include_router(movimentacao_router.router)
app.include_router(anexo_router.router)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Endpoint simples para verificar se a API e o processo estão de pé."""
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}
