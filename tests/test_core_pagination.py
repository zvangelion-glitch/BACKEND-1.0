from datetime import date

from app.core.pagination import calcular_periodo_anterior, calcular_variacao_percentual


class TestCalcularPeriodoAnterior:
    def test_periodo_de_um_mes(self):
        inicio, fim = date(2026, 8, 1), date(2026, 8, 31)
        ant_inicio, ant_fim = calcular_periodo_anterior(inicio, fim)

        # o período anterior deve ter a mesma duração (30 dias) e terminar
        # imediatamente antes do período informado
        assert ant_fim == date(2026, 7, 31)
        assert (fim - inicio).days == (ant_fim - ant_inicio).days

    def test_periodo_de_um_dia(self):
        inicio = fim = date(2026, 9, 20)
        ant_inicio, ant_fim = calcular_periodo_anterior(inicio, fim)
        assert ant_fim == date(2026, 9, 19)
        assert ant_inicio == date(2026, 9, 19)

    def test_periodo_de_oito_meses_jan_a_ago(self):
        # caso do dashboard de referência: Jan/2026 - Ago/2026
        inicio, fim = date(2026, 1, 1), date(2026, 8, 31)
        ant_inicio, ant_fim = calcular_periodo_anterior(inicio, fim)
        assert ant_fim == date(2025, 12, 31)
        assert (fim - inicio).days == (ant_fim - ant_inicio).days


class TestCalcularVariacaoPercentual:
    def test_aumento(self):
        assert calcular_variacao_percentual(123, 100) == 23.0

    def test_reducao(self):
        assert calcular_variacao_percentual(80, 100) == -20.0

    def test_sem_mudanca(self):
        assert calcular_variacao_percentual(100, 100) == 0.0

    def test_base_anterior_zero_com_valor_atual(self):
        # divisão por zero não deve estourar exceção
        assert calcular_variacao_percentual(50, 0) == 100.0

    def test_base_anterior_zero_sem_valor_atual(self):
        assert calcular_variacao_percentual(0, 0) == 0.0
