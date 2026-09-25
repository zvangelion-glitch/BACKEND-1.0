from datetime import date, timedelta
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Meta(BaseModel):
    total: int
    page: int
    page_size: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: Meta


def calcular_periodo_anterior(periodo_inicio: date, periodo_fim: date) -> tuple[date, date]:
    """
    Regra de negócio única (seção 3.3 da documentação): o período anterior tem o mesmo
    número de dias do período informado, e termina imediatamente antes do periodo_inicio.
    Usada por todos os endpoints de indicadores para garantir consistência entre web e mobile.
    """
    duracao = (periodo_fim - periodo_inicio).days
    anterior_fim = periodo_inicio - timedelta(days=1)
    anterior_inicio = anterior_fim - timedelta(days=duracao)
    return anterior_inicio, anterior_fim


def calcular_variacao_percentual(valor_atual: float, valor_anterior: float) -> float:
    if valor_anterior == 0:
        return 0.0 if valor_atual == 0 else 100.0
    return round(((valor_atual - valor_anterior) / valor_anterior) * 100, 2)
