from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_usuario_atual
from app.core.pagination import Meta, PaginatedResponse
from app.db.session import get_db
from app.models.enums import StatusFatura
from app.models.financeiro import Contrato, Fatura
from app.schemas.financeiro import ContratoRead, FaturaRead

router = APIRouter(prefix="/financeiro", tags=["Financeiro"], dependencies=[Depends(get_usuario_atual)])


@router.get("/faturas", response_model=PaginatedResponse[FaturaRead])
def listar_faturas(
    status: StatusFatura | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[FaturaRead]:
    stmt = select(Fatura)
    if status is not None:
        stmt = stmt.where(Fatura.status == status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    itens = db.scalars(stmt.order_by(Fatura.data_vencimento).offset((page - 1) * page_size).limit(page_size)).all()

    return PaginatedResponse(
        data=[FaturaRead.model_validate(f) for f in itens],
        meta=Meta(total=total, page=page, page_size=page_size),
    )


@router.get("/contratos", response_model=PaginatedResponse[ContratoRead])
def listar_contratos(
    vigencia_proxima: bool = Query(False, description="Filtra contratos com vigência a vencer em até 60 dias"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[ContratoRead]:
    stmt = select(Contrato)
    if vigencia_proxima:
        limite = date.today().toordinal() + 60
        stmt = stmt.where(Contrato.vigencia_fim <= date.fromordinal(limite))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    itens = db.scalars(stmt.order_by(Contrato.vigencia_fim).offset((page - 1) * page_size).limit(page_size)).all()

    hoje = date.today()
    dados = []
    for c in itens:
        item = ContratoRead.model_validate(c)
        item.dias_para_vencer = (c.vigencia_fim - hoje).days
        dados.append(item)

    return PaginatedResponse(data=dados, meta=Meta(total=total, page=page, page_size=page_size))
