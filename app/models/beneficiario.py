import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import StatusBeneficiario


class Beneficiario(Base):
    __tablename__ = "beneficiarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)  # armazenado criptografado
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    sexo: Mapped[str | None] = mapped_column(String(20))

    plano_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("planos.id"))
    plano: Mapped["Plano"] = relationship(back_populates="beneficiarios")

    status: Mapped[StatusBeneficiario] = mapped_column(
        Enum(StatusBeneficiario, name="status_beneficiario"), default=StatusBeneficiario.ATIVO, nullable=False
    )
    data_adesao: Mapped[date] = mapped_column(Date, nullable=False)
    municipio: Mapped[str | None] = mapped_column(String(120))
    uf: Mapped[str | None] = mapped_column(String(2))

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    atendimentos: Mapped[list["Atendimento"]] = relationship(back_populates="beneficiario")


class Plano(Base):
    __tablename__ = "planos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True)

    beneficiarios: Mapped[list["Beneficiario"]] = relationship(back_populates="plano")
