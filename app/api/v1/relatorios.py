import uuid
from datetime import date
from enum import Enum

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from app.core.deps import get_usuario_atual

router = APIRouter(prefix="/relatorios", tags=["Relatórios"], dependencies=[Depends(get_usuario_atual)])

# Armazenamento em memória apenas para o esqueleto do projeto.
# Em produção: status e URL do arquivo ficam em tabela dedicada (relatorios_gerados),
# a geração roda em worker consumindo fila (SQS) e o arquivo final é salvo no S3
# (ver seção 5 - Stack Tecnológica Recomendada), retornando uma URL assinada.
_RELATORIOS: dict[str, dict] = {}


class TipoRelatorio(str, Enum):
    PRODUCAO_ASSISTENCIAL = "producao_assistencial"
    PERFIL_POPULACIONAL = "perfil_populacional"
    REDE_PRESTADORA = "rede_prestadora"
    IMPACTO_FINANCEIRO = "impacto_financeiro"


class FormatoRelatorio(str, Enum):
    PDF = "pdf"
    XLSX = "xlsx"


class GerarRelatorioRequest(BaseModel):
    tipo: TipoRelatorio
    periodo_inicio: date
    periodo_fim: date
    formato: FormatoRelatorio = FormatoRelatorio.PDF


class RelatorioStatus(BaseModel):
    id: str
    status: str  # "processando" | "concluido" | "erro"
    tipo: TipoRelatorio
    formato: FormatoRelatorio
    download_url: str | None = None


def _processar_relatorio(relatorio_id: str) -> None:
    """Placeholder de job assíncrono. Em produção, isto roda em um worker separado."""
    _RELATORIOS[relatorio_id]["status"] = "concluido"
    _RELATORIOS[relatorio_id]["download_url"] = f"https://s3.exemplo/relatorios/{relatorio_id}"


@router.post("/gerar", response_model=RelatorioStatus)
def gerar_relatorio(payload: GerarRelatorioRequest, background_tasks: BackgroundTasks) -> RelatorioStatus:
    relatorio_id = str(uuid.uuid4())
    _RELATORIOS[relatorio_id] = {
        "status": "processando",
        "tipo": payload.tipo,
        "formato": payload.formato,
        "download_url": None,
    }
    background_tasks.add_task(_processar_relatorio, relatorio_id)
    return RelatorioStatus(id=relatorio_id, **_RELATORIOS[relatorio_id])


@router.get("/{relatorio_id}/download", response_model=RelatorioStatus)
def status_download_relatorio(relatorio_id: str) -> RelatorioStatus:
    relatorio = _RELATORIOS.get(relatorio_id)
    if relatorio is None:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return RelatorioStatus(id=relatorio_id, **relatorio)
