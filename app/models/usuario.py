import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.enums import RolePerfil


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cargo: Mapped[str | None] = mapped_column(String(100))  # ex.: "Analista de Dados"
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[RolePerfil] = mapped_column(Enum(RolePerfil, name="role_perfil"), default=RolePerfil.LEITURA, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
