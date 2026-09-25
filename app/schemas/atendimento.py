import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusAtendimento, TipoAtendimento


class AtendimentoBase(BaseModel):
    beneficiario_id: uuid.UUID
    prestador_id: uuid.UUID
    especialidade_id: uuid.UUID
    data_atendimento: datetime
    tipo: TipoAtendimento
    hora_inicio: datetime | None = None
    hora_fim: datetime | None = None
    valor: float
    status: StatusAtendimento = StatusAtendimento.REALIZADO


class AtendimentoCreate(AtendimentoBase):
    pass


class AtendimentoRead(AtendimentoBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
