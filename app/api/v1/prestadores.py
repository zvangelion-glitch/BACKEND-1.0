import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_usuario_atual
from app.core.pagination import Meta, PaginatedResponse
from app.db.session import get_db
from app.models.enums import StatusCredenciamento
from app.models.prestador import Especialidade, Prestador
from app.schemas.prestador import PrestadorRead

router = APIRouter(prefix="/prestadores", tags=["Rede Prestadora"], dependencies=[Depends(get_usuario_atual)])


@router.get("", response_model=PaginatedResponse[PrestadorRead])
def listar_prestadores(
    status: StatusCredenciamento | None = Query(None),
    especialidade: str | None = Query(None, description="Nome da especialidade"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[PrestadorRead]:
    stmt = select(Prestador)
    if status is not None:
        stmt = stmt.where(Prestador.status_credenciamento == status)
    if especialidade:
        stmt = stmt.join(Prestador.especialidades).where(Especialidade.nome.ilike(f"%{especialidade}%"))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    itens = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()

    return PaginatedResponse(
        data=[
            PrestadorRead.model_validate(p).model_copy(update={"especialidades": [e.nome for e in p.especialidades]})
            for p in itens
        ],
        meta=Meta(total=total, page=page, page_size=page_size),
    )


@router.get("/{prestador_id}", response_model=PrestadorRead)
def obter_prestador(prestador_id: uuid.UUID, db: Session = Depends(get_db)) -> PrestadorRead:
    prestador = db.get(Prestador, prestador_id)
    if prestador is None:
        raise HTTPException(status_code=404, detail="Prestador não encontrado")
    dados = PrestadorRead.model_validate(prestador)
    return dados.model_copy(update={"especialidades": [e.nome for e in prestador.especialidades]})
