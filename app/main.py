"""
Ponto de entrada da aplicação.

Nesta etapa (Etapa 0), o main.py só monta a aplicação e expõe um
health check. Os routers de negócio (auth, clientes, aeronaves, etc.)
serão incluídos aqui conforme forem desenvolvidos nas próximas etapas.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routers import aeronave as aeronave_router
from app.routers import anexo as anexo_router
from app.routers import auth as auth_router
from app.routers import cliente as cliente_router
from app.routers import inspecao as inspecao_router
from app.routers import motor as motor_router
from app.routers import movimentacao as movimentacao_router
from app.routers import ordem_servico as ordem_servico_router
from app.routers import peca as peca_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="API de gestão de manutenção aeronáutica.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS] if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
