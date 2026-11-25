"""Testes unitários da lógica e persistência do Planeamento Alimentar Semanal."""

from pathlib import Path
import sys
import tempfile
import unittest

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app.armazenamento import carregar_plano, guardar_plano
from app.logica import (
    adicionar_alimento_refeicao,
    alterar_quantidade_alimento,
    calcular_totais_dia,
    calcular_totais_refeicao,
    calcular_totais_semana,
    criar_plano_vazio,
    identificar_refeicoes_nao_planeadas,
    pesquisar_alimentos,
    remover_alimento_refeicao,
    substituir_refeicao,
)


class TestPlaneamentoAlimentar(unittest.TestCase):
    """Testes de cálculos nutricionais, gestão de refeições, validações e persistência."""

    def setUp(self) -> None:
        self.plano = criar_plano_vazio()

    def test_adicionar_e_calcular_totais(self) -> None:
        # 200g de Peito de frango grelhado (id 10: 165 kcal, 31g prot / 100g)
        ok, _ = adicionar_alimento_refeicao(self.plano, "Segunda-feira", "Almoço", 10, 200)
        self.assertTrue(ok)
        tot_ref = calcular_totais_refeicao(self.plano, "Segunda-feira", "Almoço")
        self.assertEqual(tot_ref["calorias"], 330.0)
        self.assertEqual(tot_ref["proteinas"], 62.0)

        # Adicionar 100g de Arroz cozido (id 14: 130 kcal)
        adicionar_alimento_refeicao(self.plano, "Segunda-feira", "Almoço", 14, 100)
        tot_dia = calcular_totais_dia(self.plano, "Segunda-feira")
        self.assertEqual(tot_dia["calorias"], 460.0)

        semana = calcular_totais_semana(self.plano)
        self.assertEqual(semana["totais"]["calorias"], 460.0)

    def test_validacao_entradas_invalidas(self) -> None:
        self.assertFalse(adicionar_alimento_refeicao(self.plano, "Feriado", "Almoço", 10, 100)[0])
        self.assertFalse(adicionar_alimento_refeicao(self.plano, "Segunda-feira", "Ceia", 10, 100)[0])
        self.assertFalse(adicionar_alimento_refeicao(self.plano, "Segunda-feira", "Almoço", 999, 100)[0])
        self.assertFalse(adicionar_alimento_refeicao(self.plano, "Segunda-feira", "Almoço", 10, -50)[0])
        self.assertFalse(adicionar_alimento_refeicao(self.plano, "Segunda-feira", "Almoço", 10, 0)[0])

    def test_alterar_remover_e_substituir_refeicao(self) -> None:
        adicionar_alimento_refeicao(self.plano, "Terça-feira", "Jantar", 12, 150)  # Salmão
        self.assertTrue(alterar_quantidade_alimento(self.plano, "Terça-feira", "Jantar", 0, 200)[0])
        self.assertEqual(self.plano["dias"]["Terça-feira"]["Jantar"][0]["gramas"], 200.0)

        self.assertTrue(substituir_refeicao(self.plano, "Terça-feira", "Jantar", [(22, 250), (8, 120)])[0])
        self.assertEqual(len(self.plano["dias"]["Terça-feira"]["Jantar"]), 2)

        self.assertTrue(remover_alimento_refeicao(self.plano, "Terça-feira", "Jantar", 0)[0])
        self.assertEqual(len(self.plano["dias"]["Terça-feira"]["Jantar"]), 1)

    def test_refeicoes_nao_planeadas_e_pesquisa(self) -> None:
        vazias_inicial = identificar_refeicoes_nao_planeadas(self.plano)
        self.assertEqual(len(vazias_inicial), 35)  # 7 dias x 5 refeições

        adicionar_alimento_refeicao(self.plano, "Domingo", "Pequeno-almoço", 1, 60)
        vazias_depois = identificar_refeicoes_nao_planeadas(self.plano)
        self.assertEqual(len(vazias_depois), 34)

        self.assertGreaterEqual(len(pesquisar_alimentos("frango")), 1)

    def test_persistencia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "plano.json"
            adicionar_alimento_refeicao(self.plano, "Sexta-feira", "Almoço", 10, 150)
            self.assertTrue(guardar_plano(self.plano, caminho)[0])
            dados, _ = carregar_plano(caminho)
            self.assertIsNotNone(dados)
            self.assertEqual(len(dados["dias"]["Sexta-feira"]["Almoço"]), 1)
            self.assertIsNone(carregar_plano(Path(tmp) / "falta.json")[0])


if __name__ == "__main__":
    unittest.main()
