import enum


class StatusBeneficiario(str, enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    CANCELADO = "cancelado"


class TipoPrestador(str, enum.Enum):
    HOSPITAL = "hospital"
    CLINICA = "clinica"
    LABORATORIO = "laboratorio"
    CONSULTORIO = "consultorio"


class StatusCredenciamento(str, enum.Enum):
    ATIVO = "ativo"
    SUSPENSO = "suspenso"
    DESCREDENCIADO = "descredenciado"


class TipoAtendimento(str, enum.Enum):
    CONSULTA = "consulta"
    EXAME = "exame"
    INTERNACAO = "internacao"
    PROCEDIMENTO = "procedimento"


class StatusAtendimento(str, enum.Enum):
    REALIZADO = "realizado"
    CANCELADO = "cancelado"
    GLOSADO = "glosado"


class StatusFatura(str, enum.Enum):
    AGUARDANDO_ANALISE = "aguardando_analise"
    APROVADA = "aprovada"
    GLOSADA = "glosada"
    PAGA = "paga"


class StatusContrato(str, enum.Enum):
    VIGENTE = "vigente"
    ENCERRADO = "encerrado"
    SUSPENSO = "suspenso"


class RolePerfil(str, enum.Enum):
    ADMIN = "admin"
    GESTOR = "gestor"
    ANALISTA_DADOS = "analista_dados"
    LEITURA = "leitura"
