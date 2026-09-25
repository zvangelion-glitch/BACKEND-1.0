from datetime import date

from pydantic import BaseModel


class VariacaoPercentual(BaseModel):
    valor_atual: float
    valor_anterior: float
    variacao_percentual: float


class KpisPeriodo(BaseModel):
    total_atendimentos: VariacaoPercentual
    beneficiarios_ativos: VariacaoPercentual
    rede_credenciada: VariacaoPercentual
    custo_total: VariacaoPercentual
    periodo_inicio: date
    periodo_fim: date


class PontoEvolucaoMensal(BaseModel):
    mes: str  # "Jan", "Fev", ...
    ano: int
    total_atendimentos: int


class FatiaEspecialidade(BaseModel):
    especialidade: str
    total_atendimentos: int
    percentual: float


class PrestadorRanking(BaseModel):
    prestador_id: str
    nome_fantasia: str
    total_atendimentos: int


class TempoMedioAtendimento(BaseModel):
    tempo_medio_minutos: float
    variacao_percentual: float


class AvisoPendencia(BaseModel):
    id: str
    tipo_evento: str
    descricao: str
    criado_em: str
    lido: bool
