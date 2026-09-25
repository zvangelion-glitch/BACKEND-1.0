"""schema inicial

Revision ID: 0001
Revises:
Create Date: 2026-09-20

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ---- Enums ----
    status_beneficiario = pg.ENUM("ativo", "inativo", "cancelado", name="status_beneficiario")
    tipo_prestador = pg.ENUM("hospital", "clinica", "laboratorio", "consultorio", name="tipo_prestador")
    status_credenciamento = pg.ENUM("ativo", "suspenso", "descredenciado", name="status_credenciamento")
    tipo_atendimento = pg.ENUM("consulta", "exame", "internacao", "procedimento", name="tipo_atendimento")
    status_atendimento = pg.ENUM("realizado", "cancelado", "glosado", name="status_atendimento")
    status_fatura = pg.ENUM("aguardando_analise", "aprovada", "glosada", "paga", name="status_fatura")
    status_contrato = pg.ENUM("vigente", "encerrado", "suspenso", name="status_contrato")
    role_perfil = pg.ENUM("admin", "gestor", "analista_dados", "leitura", name="role_perfil")

    bind = op.get_bind()
    for enum_type in (
        status_beneficiario, tipo_prestador, status_credenciamento, tipo_atendimento,
        status_atendimento, status_fatura, status_contrato, role_perfil,
    ):
        enum_type.create(bind, checkfirst=True)

    # ---- planos ----
    op.create_table(
        "planos",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.text("true")),
    )

    # ---- beneficiarios ----
    op.create_table(
        "beneficiarios",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("cpf", sa.String(255), nullable=False, unique=True),
        sa.Column("data_nascimento", sa.Date, nullable=False),
        sa.Column("sexo", sa.String(20)),
        sa.Column("plano_id", pg.UUID(as_uuid=True), sa.ForeignKey("planos.id")),
        sa.Column("status", status_beneficiario, nullable=False, server_default="ativo"),
        sa.Column("data_adesao", sa.Date, nullable=False),
        sa.Column("municipio", sa.String(120)),
        sa.Column("uf", sa.String(2)),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_beneficiarios_status", "beneficiarios", ["status"])

    # ---- especialidades ----
    op.create_table(
        "especialidades",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("nome", sa.String(120), nullable=False, unique=True),
        sa.Column("categoria", sa.String(80)),
    )

    # ---- prestadores ----
    op.create_table(
        "prestadores",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("nome_fantasia", sa.String(200), nullable=False),
        sa.Column("razao_social", sa.String(200)),
        sa.Column("tipo", tipo_prestador, nullable=False),
        sa.Column("status_credenciamento", status_credenciamento, nullable=False, server_default="ativo"),
        sa.Column("data_credenciamento", sa.Date, nullable=False),
        sa.Column("capacidade", sa.Integer),
        sa.Column("avaliacao", sa.Float),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_prestadores_status_credenciamento", "prestadores", ["status_credenciamento"])

    # ---- prestador_especialidade (N:N) ----
    op.create_table(
        "prestador_especialidade",
        sa.Column("prestador_id", pg.UUID(as_uuid=True), sa.ForeignKey("prestadores.id"), primary_key=True),
        sa.Column("especialidade_id", pg.UUID(as_uuid=True), sa.ForeignKey("especialidades.id"), primary_key=True),
    )

    # ---- atendimentos (particionada por mês, ver seção 6.2 da documentação) ----
    op.execute(
        """
        CREATE TABLE atendimentos (
            id UUID NOT NULL DEFAULT uuid_generate_v4(),
            beneficiario_id UUID NOT NULL REFERENCES beneficiarios(id),
            prestador_id UUID NOT NULL REFERENCES prestadores(id),
            especialidade_id UUID NOT NULL REFERENCES especialidades(id),
            data_atendimento TIMESTAMPTZ NOT NULL,
            tipo tipo_atendimento NOT NULL,
            hora_inicio TIMESTAMPTZ,
            hora_fim TIMESTAMPTZ,
            valor NUMERIC(12, 2) NOT NULL,
            status status_atendimento NOT NULL DEFAULT 'realizado',
            criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (id, data_atendimento)
        ) PARTITION BY RANGE (data_atendimento);
        """
    )
    op.execute("CREATE INDEX ix_atendimentos_data ON atendimentos (data_atendimento);")
    op.execute("CREATE INDEX ix_atendimentos_especialidade ON atendimentos (especialidade_id);")
    op.execute("CREATE INDEX ix_atendimentos_prestador ON atendimentos (prestador_id);")

    # Partições iniciais (mensais) cobrindo o período corrente + próximos meses.
    # Em produção, a criação de novas partições deve ser automatizada via job mensal
    # (ex.: pg_partman ou rotina agendada) para evitar falha de INSERT por falta de partição.
    op.execute(
        """
        DO $$
        DECLARE
            data_inicio DATE := date_trunc('month', CURRENT_DATE - INTERVAL '3 months');
            data_fim DATE;
            i INT;
        BEGIN
            FOR i IN 0..11 LOOP
                data_fim := data_inicio + INTERVAL '1 month';
                EXECUTE format(
                    'CREATE TABLE IF NOT EXISTS atendimentos_%s PARTITION OF atendimentos FOR VALUES FROM (%L) TO (%L);',
                    to_char(data_inicio, 'YYYY_MM'), data_inicio, data_fim
                );
                data_inicio := data_fim;
            END LOOP;
        END $$;
        """
    )

    # ---- financeiro_faturas ----
    op.create_table(
        "financeiro_faturas",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("prestador_id", pg.UUID(as_uuid=True), sa.ForeignKey("prestadores.id"), nullable=False),
        sa.Column("competencia", sa.Date, nullable=False),
        sa.Column("valor_total", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", status_fatura, nullable=False, server_default="aguardando_analise"),
        sa.Column("data_vencimento", sa.Date, nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_faturas_status", "financeiro_faturas", ["status"])

    # ---- contratos ----
    op.create_table(
        "contratos",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("prestador_id", pg.UUID(as_uuid=True), sa.ForeignKey("prestadores.id"), nullable=False),
        sa.Column("vigencia_inicio", sa.Date, nullable=False),
        sa.Column("vigencia_fim", sa.Date, nullable=False),
        sa.Column("status", status_contrato, nullable=False, server_default="vigente"),
    )
    op.create_index("ix_contratos_vigencia_fim", "contratos", ["vigencia_fim"])

    # ---- auditoria_eventos ----
    op.create_table(
        "auditoria_eventos",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tipo_evento", sa.String(80), nullable=False),
        sa.Column("descricao", sa.String(500), nullable=False),
        sa.Column("entidade_ref", sa.String(200)),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("lido", sa.Boolean, nullable=False, server_default=sa.text("false")),
    )

    # ---- usuarios ----
    op.create_table(
        "usuarios",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("cargo", sa.String(100)),
        sa.Column("email", sa.String(200), nullable=False, unique=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("role", role_perfil, nullable=False, server_default="leitura"),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("usuarios")
    op.drop_table("auditoria_eventos")
    op.drop_table("contratos")
    op.drop_table("financeiro_faturas")
    op.execute("DROP TABLE atendimentos CASCADE")
    op.drop_table("prestador_especialidade")
    op.drop_table("prestadores")
    op.drop_table("especialidades")
    op.drop_table("beneficiarios")
    op.drop_table("planos")

    for enum_name in (
        "status_beneficiario", "tipo_prestador", "status_credenciamento", "tipo_atendimento",
        "status_atendimento", "status_fatura", "status_contrato", "role_perfil",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
