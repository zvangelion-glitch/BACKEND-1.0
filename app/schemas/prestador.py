import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusCredenciamento, TipoPrestador


class PrestadorBase(BaseModel):
    nome_fantasia: str
    razao_social: str | None = None
    tipo: TipoPrestador
    status_credenciamento: StatusCredenciamento = StatusCredenciamento.ATIVO
    data_credenciamento: date
    capacidade: int | None = None
    avaliacao: float | None = None


class PrestadorRead(PrestadorBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    especialidades: list[str] = []
