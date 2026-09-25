from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_usuario_atual
from app.core.pagination import calcular_periodo_anterior, calcular_variacao_percentual
from app.db.session import get_db
from app.schemas.dashboard import (
    AvisoPendencia,
    FatiaEspecialidade,
    KpisPeriodo,
    PontoEvolucaoMensal,
    PrestadorRanking,
    TempoMedioAtendimento,
    VariacaoPercentual,
)

router = APIRouter(prefix="/dashboard", tags=["Painel Inicial"], dependencies=[Depends(get_usuario_atual)])


def _contar_atendimentos(db: Session, inicio: date, fim: date) -> int:
    return db.scalar(
        text("SELECT COUNT(*) FROM atendimentos WHERE data_atendimento BETWEEN :inicio AND :fim AND status != 'cancelado'"),
        {"inicio": inicio, "fim": fim},
    ) or 0


def _contar_beneficiarios_ativos(db: Session, ate: date) -> int:
    return db.scalar(
        text("SELECT COUNT(*) FROM beneficiarios WHERE status = 'ativo' AND data_adesao <= :ate"),
        {"ate": ate},
    ) or 0


def _contar_rede_credenciada(db: Session, ate: date) -> int:
    return db.scalar(
        text("SELECT COUNT(*) FROM prestadores WHERE status_credenciamento = 'ativo' AND data_credenciamento <= :ate"),
        {"ate": ate},
    ) or 0


def _somar_custo_total(db: Session, inicio: date, fim: date) -> float:
    return float(
        db.scalar(
            text("SELECT COALESCE(SUM(valor), 0) FROM atendimentos WHERE data_atendimento BETWEEN :inicio AND :fim AND status != 'cancelado'"),
            {"inicio": inicio, "fim": fim},
        ) or 0
    )


@router.get("/kpis", response_model=KpisPeriodo)
def kpis(
    periodo_inicio: date = Query(...),
    periodo_fim: date = Query(...),
    db: Session = Depends(get_db),
) -> KpisPeriodo:
    ant_inicio, ant_fim = calcular_periodo_anterior(periodo_inicio, periodo_fim)

    atend_atual = _contar_atendimentos(db, periodo_inicio, periodo_fim)
    atend_anterior = _contar_atendimentos(db, ant_inicio, ant_fim)

    benef_atual = _contar_beneficiarios_ativos(db, periodo_fim)
    benef_anterior = _contar_beneficiarios_ativos(db, ant_fim)

    rede_atual = _contar_rede_credenciada(db, periodo_fim)
    rede_anterior = _contar_rede_credenciada(db, ant_fim)

    custo_atual = _somar_custo_total(db, periodo_inicio, periodo_fim)
    custo_anterior = _somar_custo_total(db, ant_inicio, ant_fim)

    return KpisPeriodo(
        total_atendimentos=VariacaoPercentual(
            valor_atual=atend_atual, valor_anterior=atend_anterior,
            variacao_percentual=calcular_variacao_percentual(atend_atual, atend_anterior),
        ),
        beneficiarios_ativos=VariacaoPercentual(
            valor_atual=benef_atual, valor_anterior=benef_anterior,
            variacao_percentual=calcular_variacao_percentual(benef_atual, benef_anterior),
        ),
        rede_credenciada=VariacaoPercentual(
            valor_atual=rede_atual, valor_anterior=rede_anterior,
            variacao_percentual=calcular_variacao_percentual(rede_atual, rede_anterior),
        ),
        custo_total=VariacaoPercentual(
            valor_atual=custo_atual, valor_anterior=custo_anterior,
            variacao_percentual=calcular_variacao_percentual(custo_atual, custo_anterior),
        ),
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
    )


@router.get("/evolucao-atendimentos", response_model=list[PontoEvolucaoMensal])
def evolucao_atendimentos(
    periodo_inicio: date = Query(...),
    periodo_fim: date = Query(...),
    db: Session = Depends(get_db),
) -> list[PontoEvolucaoMensal]:
    rows = db.execute(
        text(
            """
            SELECT to_char(data_atendimento, 'Mon') AS mes,
                   EXTRACT(YEAR FROM data_atendimento)::int AS ano,
                   COUNT(*) AS total
            FROM atendimentos
            WHERE data_atendimento BETWEEN :inicio AND :fim AND status != 'cancelado'
            GROUP BY 1, 2, date_trunc('month', data_atendimento)
            ORDER BY date_trunc('month', data_atendimento)
            """
        ),
        {"inicio": periodo_inicio, "fim": periodo_fim},
    ).all()
    return [PontoEvolucaoMensal(mes=r.mes, ano=r.ano, total_atendimentos=r.total) for r in rows]


@router.get("/distribuicao-especialidade", response_model=list[FatiaEspecialidade])
def distribuicao_especialidade(
    periodo_inicio: date = Query(...),
    periodo_fim: date = Query(...),
    db: Session = Depends(get_db),
) -> list[FatiaEspecialidade]:
    rows = db.execute(
        text(
            """
            SELECT e.nome AS especialidade, COUNT(*) AS total,
                   ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0), 1) AS percentual
            FROM atendimentos a
            JOIN especialidades e ON e.id = a.especialidade_id
            WHERE a.data_atendimento BETWEEN :inicio AND :fim AND a.status != 'cancelado'
            GROUP BY e.nome
            ORDER BY total DESC
            """
        ),
        {"inicio": periodo_inicio, "fim": periodo_fim},
    ).all()
    return [FatiaEspecialidade(especialidade=r.especialidade, total_atendimentos=r.total, percentual=float(r.percentual or 0)) for r in rows]


@router.get("/top-prestadores", response_model=list[PrestadorRanking])
def top_prestadores(
    periodo_inicio: date = Query(...),
    periodo_fim: date = Query(...),
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[PrestadorRanking]:
    rows = db.execute(
        text(
            """
            SELECT p.id AS prestador_id, p.nome_fantasia, COUNT(*) AS total
            FROM atendimentos a
            JOIN prestadores p ON p.id = a.prestador_id
            WHERE a.data_atendimento BETWEEN :inicio AND :fim AND a.status != 'cancelado'
            GROUP BY p.id, p.nome_fantasia
            ORDER BY total DESC
            LIMIT :limit
            """
        ),
        {"inicio": periodo_inicio, "fim": periodo_fim, "limit": limit},
    ).all()
    return [PrestadorRanking(prestador_id=str(r.prestador_id), nome_fantasia=r.nome_fantasia, total_atendimentos=r.total) for r in rows]


@router.get("/tempo-medio-atendimento", response_model=TempoMedioAtendimento)
def tempo_medio_atendimento(
    periodo_inicio: date = Query(...),
    periodo_fim: date = Query(...),
    db: Session = Depends(get_db),
) -> TempoMedioAtendimento:
    ant_inicio, ant_fim = calcular_periodo_anterior(periodo_inicio, periodo_fim)

    def _media(inicio: date, fim: date) -> float:
        return float(
            db.scalar(
                text(
                    """
                    SELECT COALESCE(AVG(EXTRACT(EPOCH FROM (hora_fim - hora_inicio)) / 60), 0)
                    FROM atendimentos
                    WHERE data_atendimento BETWEEN :inicio AND :fim
                      AND hora_inicio IS NOT NULL AND hora_fim IS NOT NULL
                    """
                ),
                {"inicio": inicio, "fim": fim},
            ) or 0
        )

    atual = _media(periodo_inicio, periodo_fim)
    anterior = _media(ant_inicio, ant_fim)
    return TempoMedioAtendimento(
        tempo_medio_minutos=round(atual, 1),
        variacao_percentual=calcular_variacao_percentual(atual, anterior),
    )


@router.get("/avisos", response_model=list[AvisoPendencia])
def avisos(db: Session = Depends(get_db)) -> list[AvisoPendencia]:
    rows = db.execute(
        text(
            """
            SELECT id, tipo_evento, descricao, criado_em, lido
            FROM auditoria_eventos
            ORDER BY criado_em DESC
            LIMIT 20
            """
        )
    ).all()
    return [
        AvisoPendencia(
            id=str(r.id), tipo_evento=r.tipo_evento, descricao=r.descricao,
            criado_em=r.criado_em.isoformat(), lido=r.lido,
        )
        for r in rows
    ]
