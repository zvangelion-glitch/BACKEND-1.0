from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import exigir_roles, get_usuario_atual
from app.core.pagination import Meta, PaginatedResponse
from app.db.session import get_db
from app.models.atendimento import Atendimento
from app.models.enums import RolePerfil
from app.schemas.atendimento import AtendimentoCreate, AtendimentoRead

router = APIRouter(prefix="/atendimentos", tags=["Atendimentos"], dependencies=[Depends(get_usuario_atual)])


@router.get("", response_model=PaginatedResponse[AtendimentoRead])
def listar_atendimentos(
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    especialidade_id: str | None = Query(None),
    prestador_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AtendimentoRead]:
    stmt = select(Atendimento)
    if data_inicio:
        stmt = stmt.where(Atendimento.data_atendimento >= data_inicio)
    if data_fim:
        stmt = stmt.where(Atendimento.data_atendimento <= data_fim)
    if especialidade_id:
        stmt = stmt.where(Atendimento.especialidade_id == especialidade_id)
    if prestador_id:
        stmt = stmt.where(Atendimento.prestador_id == prestador_id)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    itens = db.scalars(stmt.order_by(Atendimento.data_atendimento.desc()).offset((page - 1) * page_size).limit(page_size)).all()

    return PaginatedResponse(
        data=[AtendimentoRead.model_validate(a) for a in itens],
        meta=Meta(total=total, page=page, page_size=page_size),
    )


@router.post("", response_model=AtendimentoRead, status_code=status.HTTP_201_CREATED)
def criar_atendimento(
    payload: AtendimentoCreate,
    db: Session = Depends(get_db),
    _usuario=Depends(exigir_roles(RolePerfil.ADMIN, RolePerfil.GESTOR)),
) -> Atendimento:
    atendimento = Atendimento(**payload.model_dump())
    db.add(atendimento)
    db.commit()
    db.refresh(atendimento)
    return atendimento
