import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusBeneficiario


class BeneficiarioBase(BaseModel):
    nome: str
    data_nascimento: date
    sexo: str | None = None
    plano_id: uuid.UUID | None = None
    status: StatusBeneficiario = StatusBeneficiario.ATIVO
    data_adesao: date
    municipio: str | None = None
    uf: str | None = None


class BeneficiarioCreate(BeneficiarioBase):
    cpf: str


class BeneficiarioRead(BeneficiarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class FaixaEtariaPerfil(BaseModel):
    faixa: str  # "0-18", "19-25", "26-50", "51-65", "65+"
    total: int
    percentual: float


class PerfilPopulacional(BaseModel):
    faixas_etarias: list[FaixaEtariaPerfil]
    total_beneficiarios: int
