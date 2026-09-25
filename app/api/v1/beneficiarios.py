import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_usuario_atual
from app.core.pagination import Meta, PaginatedResponse
from app.db.session import get_db
from app.models.beneficiario import Beneficiario
from app.models.enums import StatusBeneficiario
from app.schemas.beneficiario import BeneficiarioRead, FaixaEtariaPerfil, PerfilPopulacional

router = APIRouter(prefix="/beneficiarios", tags=["Beneficiários"], dependencies=[Depends(get_usuario_atual)])


@router.get("", response_model=PaginatedResponse[BeneficiarioRead])
def listar_beneficiarios(
    status: StatusBeneficiario | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[BeneficiarioRead]:
    stmt = select(Beneficiario)
    if status is not None:
        stmt = stmt.where(Beneficiario.status == status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    itens = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()

    return PaginatedResponse(
        data=[BeneficiarioRead.model_validate(b) for b in itens],
        meta=Meta(total=total, page=page, page_size=page_size),
    )


@router.get("/perfil-populacional", response_model=PerfilPopulacional)
def perfil_populacional(db: Session = Depends(get_db)) -> PerfilPopulacional:
    faixas_sql = """
        SELECT
            CASE
                WHEN idade BETWEEN 0 AND 18 THEN '0-18'
                WHEN idade BETWEEN 19 AND 25 THEN '19-25'
                WHEN idade BETWEEN 26 AND 50 THEN '26-50'
                WHEN idade BETWEEN 51 AND 65 THEN '51-65'
                ELSE '65+'
            END AS faixa,
            COUNT(*) AS total
        FROM (
            SELECT DATE_PART('year', AGE(CURRENT_DATE, data_nascimento))::int AS idade
            FROM beneficiarios WHERE status = 'ativo'
        ) sub
        GROUP BY faixa
    """
    from sqlalchemy import text

    rows = db.execute(text(faixas_sql)).all()
    total = sum(r.total for r in rows)
    faixas = [
        FaixaEtariaPerfil(faixa=r.faixa, total=r.total, percentual=round(100 * r.total / total, 1) if total else 0)
        for r in rows
    ]
    return PerfilPopulacional(faixas_etarias=faixas, total_beneficiarios=total)


@router.get("/{beneficiario_id}", response_model=BeneficiarioRead)
def obter_beneficiario(beneficiario_id: uuid.UUID, db: Session = Depends(get_db)) -> Beneficiario:
    beneficiario = db.get(Beneficiario, beneficiario_id)
    if beneficiario is None:
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado")
    return beneficiario
