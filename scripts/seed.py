"""
Popula o banco com dados de exemplo para desenvolvimento e testes manuais.

Uso:
    python -m scripts.seed
"""
import random
from datetime import date, datetime, timedelta, timezone

from app.core.security import gerar_hash_senha
from app.db.session import SessionLocal
from app.models.atendimento import Atendimento
from app.models.beneficiario import Beneficiario, Plano
from app.models.enums import (
    RolePerfil,
    StatusAtendimento,
    StatusBeneficiario,
    StatusContrato,
    StatusCredenciamento,
    StatusFatura,
    TipoAtendimento,
    TipoPrestador,
)
from app.models.financeiro import Contrato, Fatura
from app.models.prestador import Especialidade, Prestador
from app.models.usuario import Usuario

ESPECIALIDADES = ["Clínica Médica", "Ortopedia", "Ginecologia", "Pediatria", "Cardiologia", "Dermatologia"]
PRESTADORES = [
    ("Hospital ABC", TipoPrestador.HOSPITAL),
    ("Clínica Vida", TipoPrestador.CLINICA),
    ("Santa Casa", TipoPrestador.HOSPITAL),
    ("Centro Médico", TipoPrestador.CLINICA),
    ("Instituto Saúde", TipoPrestador.CLINICA),
]
MUNICIPIOS = [("Belo Horizonte", "MG"), ("Contagem", "MG"), ("Betim", "MG"), ("Santa Luzia", "MG")]


def run() -> None:
    db = SessionLocal()
    try:
        print("Criando plano padrão...")
        plano = Plano(nome="Plano Essencial", ativo=True)
        db.add(plano)

        print("Criando usuário administrador de exemplo...")
        admin = Usuario(
            nome="Administrador",
            cargo="Analista de Dados",
            email="admin@saudedados.local",
            senha_hash=gerar_hash_senha("trocar123"),
            role=RolePerfil.ADMIN,
        )
        db.add(admin)

        print("Criando especialidades...")
        especialidades = [Especialidade(nome=nome, categoria="Assistencial") for nome in ESPECIALIDADES]
        db.add_all(especialidades)

        print("Criando prestadores...")
        prestadores = []
        for nome, tipo in PRESTADORES:
            p = Prestador(
                nome_fantasia=nome,
                razao_social=f"{nome} LTDA",
                tipo=tipo,
                status_credenciamento=StatusCredenciamento.ATIVO,
                data_credenciamento=date.today() - timedelta(days=random.randint(200, 2000)),
                capacidade=random.randint(20, 200),
                avaliacao=round(random.uniform(3.5, 5.0), 1),
            )
            p.especialidades = random.sample(especialidades, k=random.randint(1, 3))
            prestadores.append(p)
        db.add_all(prestadores)

        db.flush()  # garante IDs antes de usar como FK

        print("Criando beneficiários...")
        beneficiarios = []
        for i in range(300):
            municipio, uf = random.choice(MUNICIPIOS)
            idade_dias = random.randint(0 * 365, 85 * 365)
            b = Beneficiario(
                nome=f"Beneficiário Exemplo {i+1}",
                cpf=f"{random.randint(10000000000, 99999999999)}",
                data_nascimento=date.today() - timedelta(days=idade_dias),
                sexo=random.choice(["F", "M"]),
                plano=plano,
                status=random.choices(
                    [StatusBeneficiario.ATIVO, StatusBeneficiario.INATIVO, StatusBeneficiario.CANCELADO],
                    weights=[85, 10, 5],
                )[0],
                data_adesao=date.today() - timedelta(days=random.randint(30, 1500)),
                municipio=municipio,
                uf=uf,
            )
            beneficiarios.append(b)
        db.add_all(beneficiarios)
        db.flush()

        print("Criando atendimentos dos últimos 8 meses...")
        hoje = datetime.now(timezone.utc)
        atendimentos = []
        for _ in range(2000):
            dias_atras = random.randint(0, 240)
            data_atendimento = hoje - timedelta(days=dias_atras, hours=random.randint(0, 23))
            duracao_min = random.randint(15, 180)
            hora_inicio = data_atendimento
            hora_fim = data_atendimento + timedelta(minutes=duracao_min)

            a = Atendimento(
                beneficiario=random.choice(beneficiarios),
                prestador=random.choice(prestadores),
                especialidade_id=random.choice(especialidades).id,
                data_atendimento=data_atendimento,
                tipo=random.choice(list(TipoAtendimento)),
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                valor=round(random.uniform(80, 1500), 2),
                status=random.choices(
                    [StatusAtendimento.REALIZADO, StatusAtendimento.CANCELADO, StatusAtendimento.GLOSADO],
                    weights=[90, 5, 5],
                )[0],
            )
            atendimentos.append(a)
        db.add_all(atendimentos)

        print("Criando faturas e contratos...")
        faturas = []
        contratos = []
        for p in prestadores:
            for mes_atras in range(3):
                competencia = date.today().replace(day=1) - timedelta(days=30 * mes_atras)
                faturas.append(
                    Fatura(
                        prestador=p,
                        competencia=competencia.replace(day=1),
                        valor_total=round(random.uniform(5000, 80000), 2),
                        status=random.choice(list(StatusFatura)),
                        data_vencimento=competencia + timedelta(days=30),
                    )
                )
            contratos.append(
                Contrato(
                    prestador=p,
                    vigencia_inicio=date.today() - timedelta(days=400),
                    vigencia_fim=date.today() + timedelta(days=random.randint(15, 500)),
                    status=StatusContrato.VIGENTE,
                )
            )
        db.add_all(faturas)
        db.add_all(contratos)

        db.commit()
        print(f"Seed concluído: {len(beneficiarios)} beneficiários, {len(prestadores)} prestadores, "
              f"{len(atendimentos)} atendimentos, {len(faturas)} faturas, {len(contratos)} contratos.")
        print("Login de exemplo -> email: admin@saudedados.local | senha: trocar123")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
