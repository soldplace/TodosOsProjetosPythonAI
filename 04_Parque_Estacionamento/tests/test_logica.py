"""Testes unitários do Simulador de Parque de Estacionamento."""

from pathlib import Path
import sys
import tempfile
import unittest

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app.armazenamento import carregar_parque, guardar_parque
from app.logica import (
    avancar_relogio,
    configurar_tarifa,
    criar_novo_parque,
    normalizar_e_validar_matricula,
    obter_estatisticas,
    reconfigurar_capacidade,
    registar_entrada,
    registar_saida,
    simular_saida,
)


class TestParqueEstacionamento(unittest.TestCase):
    """Testes para entradas, saídas, validação, tarifário e persistência."""

    def setUp(self) -> None:
        self.estado = criar_novo_parque(capacidade=4, tarifa_hora=2.00)

    def test_validacao_matriculas(self) -> None:
        self.assertTrue(normalizar_e_validar_matricula("aa-12-bb")[0])
        self.assertTrue(normalizar_e_validar_matricula("12-AB-34")[0])
        self.assertTrue(normalizar_e_validar_matricula("12-34-AB")[0])
        self.assertFalse(normalizar_e_validar_matricula("")[0])
        self.assertFalse(normalizar_e_validar_matricula("INVALIDA")[0])

    def test_entrada_lotacao_e_duplicados(self) -> None:
        self.assertTrue(registar_entrada(self.estado, "AA-01-BB")[0])
        # Matrícula duplicada deve ser rejeitada
        self.assertFalse(registar_entrada(self.estado, "aa-01-bb")[0])

        self.assertTrue(registar_entrada(self.estado, "AA-02-BB")[0])
        self.assertTrue(registar_entrada(self.estado, "AA-03-BB")[0])
        self.assertTrue(registar_entrada(self.estado, "AA-04-BB")[0])

        # Parque lotado (4/4)
        ok_lotado, _, _ = registar_entrada(self.estado, "AA-05-BB")
        self.assertFalse(ok_lotado)

    def test_saida_calculo_arredondamento_e_relogio(self) -> None:
        ok, _, veic = registar_entrada(self.estado, "10-AA-20")
        self.assertTrue(ok)
        bilhete = veic["bilhete"]

        # Avançar 90 minutos -> 2 horas cobradas -> 4.00 €
        avancar_relogio(self.estado, 90)
        ok_sim, _, resumo = simular_saida(self.estado, bilhete)
        self.assertTrue(ok_sim)
        self.assertEqual(resumo["minutos"], 90)
        self.assertEqual(resumo["horas_cobradas"], 2)
        self.assertEqual(resumo["valor"], 4.00)

        ok_sai, _, _ = registar_saida(self.estado, "10-AA-20")
        self.assertTrue(ok_sai)
        stats = obter_estatisticas(self.estado)
        self.assertEqual(stats["receita_total"], 4.00)
        self.assertEqual(stats["ocupados"], 0)
        self.assertEqual(stats["tempo_medio_min"], 90.0)

    def test_configurar_tarifa_e_capacidade(self) -> None:
        self.assertFalse(configurar_tarifa(self.estado, -1.0)[0])
        self.assertTrue(configurar_tarifa(self.estado, 2.50)[0])

        # Ocupar lugar 4 (índice 3) e tentar reduzir para 3 lugares -> deve falhar
        registar_entrada(self.estado, "AA-11-AA")
        registar_entrada(self.estado, "AA-22-AA")
        registar_entrada(self.estado, "AA-33-AA")
        registar_entrada(self.estado, "AA-44-AA")
        self.assertFalse(reconfigurar_capacidade(self.estado, 3)[0])
        self.assertTrue(reconfigurar_capacidade(self.estado, 8)[0])

    def test_persistencia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "parque.json"
            registar_entrada(self.estado, "BB-99-CC")
            self.assertTrue(guardar_parque(self.estado, caminho)[0])
            dados, _ = carregar_parque(caminho)
            self.assertIsNotNone(dados)
            self.assertEqual(dados["total_entradas"], 1)
            self.assertIsNone(carregar_parque(Path(tmp) / "nao.json")[0])


if __name__ == "__main__":
    unittest.main()
