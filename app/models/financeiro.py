import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import StatusContrato, StatusFatura


class Fatura(Base):
    __tablename__ = "financeiro_faturas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prestador_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prestadores.id"), nullable=False)

    competencia: Mapped[date] = mapped_column(Date, nullable=False)  # dia 1 do mês de referência
    valor_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    status: Mapped[StatusFatura] = mapped_column(
        Enum(StatusFatura, name="status_fatura"), default=StatusFatura.AGUARDANDO_ANALISE, nullable=False
    )
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    prestador: Mapped["Prestador"] = relationship()


class Contrato(Base):
    __tablename__ = "contratos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prestador_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prestadores.id"), nullable=False)

    vigencia_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    vigencia_fim: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[StatusContrato] = mapped_column(
        Enum(StatusContrato, name="status_contrato"), default=StatusContrato.VIGENTE, nullable=False
    )

    prestador: Mapped["Prestador"] = relationship()
