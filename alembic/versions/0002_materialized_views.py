"""materialized views do painel

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-20

"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_evolucao_mensal AS
        SELECT
            date_trunc('month', data_atendimento) AS mes_referencia,
            to_char(data_atendimento, 'Mon') AS mes,
            EXTRACT(YEAR FROM data_atendimento)::int AS ano,
            COUNT(*) AS total_atendimentos
        FROM atendimentos
        WHERE status != 'cancelado'
        GROUP BY 1, 2, 3
        ORDER BY 1;
        """
    )
    op.execute("CREATE UNIQUE INDEX ix_mv_evolucao_mensal ON mv_evolucao_mensal (mes_referencia);")

    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_distribuicao_especialidade AS
        SELECT
            e.id AS especialidade_id,
            e.nome AS especialidade,
            date_trunc('month', a.data_atendimento) AS mes_referencia,
            COUNT(*) AS total_atendimentos
        FROM atendimentos a
        JOIN especialidades e ON e.id = a.especialidade_id
        WHERE a.status != 'cancelado'
        GROUP BY 1, 2, 3;
        """
    )
    op.execute("CREATE INDEX ix_mv_distribuicao_especialidade ON mv_distribuicao_especialidade (mes_referencia);")

    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_top_prestadores AS
        SELECT
            p.id AS prestador_id,
            p.nome_fantasia,
            date_trunc('month', a.data_atendimento) AS mes_referencia,
            COUNT(*) AS total_atendimentos
        FROM atendimentos a
        JOIN prestadores p ON p.id = a.prestador_id
        WHERE a.status != 'cancelado'
        GROUP BY 1, 2, 3;
        """
    )
    op.execute("CREATE INDEX ix_mv_top_prestadores ON mv_top_prestadores (mes_referencia);")

    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_tempo_medio_atendimento AS
        SELECT
            date_trunc('month', data_atendimento) AS mes_referencia,
            AVG(EXTRACT(EPOCH FROM (hora_fim - hora_inicio)) / 60) AS tempo_medio_minutos
        FROM atendimentos
        WHERE hora_inicio IS NOT NULL AND hora_fim IS NOT NULL
        GROUP BY 1;
        """
    )
    op.execute("CREATE UNIQUE INDEX ix_mv_tempo_medio_atendimento ON mv_tempo_medio_atendimento (mes_referencia);")

    op.execute(
        """
        CREATE MATERIALIZED VIEW mv_kpis_periodo AS
        SELECT
            date_trunc('month', a.data_atendimento) AS mes_referencia,
            COUNT(*) AS total_atendimentos,
            COALESCE(SUM(a.valor), 0) AS custo_total
        FROM atendimentos a
        WHERE a.status != 'cancelado'
        GROUP BY 1;
        """
    )
    op.execute("CREATE UNIQUE INDEX ix_mv_kpis_periodo ON mv_kpis_periodo (mes_referencia);")

    # Refresh concorrente (não bloqueia leitura) — requer índice único em cada MV, já criado acima.
    # Agendamento sugerido via pg_cron, a cada hora:
    #   SELECT cron.schedule('refresh_mv_saudedados', '0 * * * *', $$
    #       REFRESH MATERIALIZED VIEW CONCURRENTLY mv_evolucao_mensal;
    #       REFRESH MATERIALIZED VIEW CONCURRENTLY mv_distribuicao_especialidade;
    #       REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_prestadores;
    #       REFRESH MATERIALIZED VIEW CONCURRENTLY mv_tempo_medio_atendimento;
    #       REFRESH MATERIALIZED VIEW CONCURRENTLY mv_kpis_periodo;
    #   $$);


def downgrade() -> None:
    for view in (
        "mv_kpis_periodo", "mv_tempo_medio_atendimento", "mv_top_prestadores",
        "mv_distribuicao_especialidade", "mv_evolucao_mensal",
    ):
        op.execute(f"DROP MATERIALIZED VIEW IF EXISTS {view}")
