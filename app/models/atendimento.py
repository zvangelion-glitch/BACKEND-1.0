import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import StatusAtendimento, TipoAtendimento


class Atendimento(Base):
    """
    Tabela de maior volume do sistema.
    Particionamento por mês/ano (RANGE em data_atendimento) — ver alembic/versions
    e nota de escalabilidade na seção 6.2 da documentação.
    """

    __tablename__ = "atendimentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    beneficiario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("beneficiarios.id"), nullable=False)
    prestador_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prestadores.id"), nullable=False)
    especialidade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("especialidades.id"), nullable=False)

    data_atendimento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    tipo: Mapped[TipoAtendimento] = mapped_column(Enum(TipoAtendimento, name="tipo_atendimento"), nullable=False)

    hora_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    hora_fim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    valor: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[StatusAtendimento] = mapped_column(
        Enum(StatusAtendimento, name="status_atendimento"), default=StatusAtendimento.REALIZADO, nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    beneficiario: Mapped["Beneficiario"] = relationship(back_populates="atendimentos")
    prestador: Mapped["Prestador"] = relationship(back_populates="atendimentos")
    especialidade: Mapped["Especialidade"] = relationship()
