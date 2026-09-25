import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Table, Column, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import StatusCredenciamento, TipoPrestador

prestador_especialidade = Table(
    "prestador_especialidade",
    Base.metadata,
    Column("prestador_id", UUID(as_uuid=True), ForeignKey("prestadores.id"), primary_key=True),
    Column("especialidade_id", UUID(as_uuid=True), ForeignKey("especialidades.id"), primary_key=True),
)


class Especialidade(Base):
    __tablename__ = "especialidades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    categoria: Mapped[str | None] = mapped_column(String(80))

    prestadores: Mapped[list["Prestador"]] = relationship(
        secondary=prestador_especialidade, back_populates="especialidades"
    )


class Prestador(Base):
    __tablename__ = "prestadores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_fantasia: Mapped[str] = mapped_column(String(200), nullable=False)
    razao_social: Mapped[str | None] = mapped_column(String(200))
    tipo: Mapped[TipoPrestador] = mapped_column(Enum(TipoPrestador, name="tipo_prestador"), nullable=False)

    status_credenciamento: Mapped[StatusCredenciamento] = mapped_column(
        Enum(StatusCredenciamento, name="status_credenciamento"),
        default=StatusCredenciamento.ATIVO,
        nullable=False,
    )
    data_credenciamento: Mapped[date] = mapped_column(Date, nullable=False)
    capacidade: Mapped[int | None] = mapped_column()
    avaliacao: Mapped[float | None] = mapped_column()

    especialidades: Mapped[list["Especialidade"]] = relationship(
        secondary=prestador_especialidade, back_populates="prestadores"
    )
    atendimentos: Mapped[list["Atendimento"]] = relationship(back_populates="prestador")

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
