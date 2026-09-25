import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusContrato, StatusFatura


class FaturaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    prestador_id: uuid.UUID
    competencia: date
    valor_total: float
    status: StatusFatura
    data_vencimento: date


class ContratoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    prestador_id: uuid.UUID
    vigencia_inicio: date
    vigencia_fim: date
    status: StatusContrato
    dias_para_vencer: int | None = None
