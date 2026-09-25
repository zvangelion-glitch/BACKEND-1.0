from fastapi import APIRouter

from app.api.v1 import atendimentos, auth, beneficiarios, dashboard, financeiro, prestadores, relatorios

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(beneficiarios.router)
api_router.include_router(atendimentos.router)
api_router.include_router(prestadores.router)
api_router.include_router(financeiro.router)
api_router.include_router(relatorios.router)
