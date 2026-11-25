"""Testes unitários da lógica e persistência do Simulador de Porto Marítimo."""

from pathlib import Path
import sys
import tempfile
import unittest

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app.armazenamento import carregar_porto, guardar_porto
from app.logica import (
    atracar_navio,
    atribuir_cais_otimizado,
    criar_novo_porto,
    executar_ciclo_portuario,
    expedir_contentor,
    obter_fila_espera_ordenada,
    obter_indicadores,
    registar_navio,
)


class TestPortoMaritimo(unittest.TestCase):
    """Testes de fila, compatibilidade de cais, contentores, finanças e gravação."""

    def setUp(self) -> None:
        self.estado = criar_novo_porto()

    def test_registo_navio_e_fila_prioritaria(self) -> None:
        self.assertFalse(registar_navio(self.estado, "", "Pequeno", 5)[0])
        self.assertFalse(registar_navio(self.estado, "Teste", "Gigante", 5)[0])

        registar_navio(self.estado, "Normal A", "Pequeno", 4, prioridade="Normal")
        registar_navio(self.estado, "Urgente B", "Médio", 4, prioridade="Urgente")
        fila = obter_fila_espera_ordenada(self.estado)
        self.assertEqual(fila[0]["nome"], "Urgente B")

    def test_compatibilidade_e_atribuicao_otimizada(self) -> None:
        _, _, nav_grande = registar_navio(self.estado, "Colosso", "Grande", 6)
        _, _, nav_peq = registar_navio(self.estado, "Costeiro", "Pequeno", 3)

        # Navio grande não pode atracar no Cais 1 (Pequeno)
        self.assertFalse(atracar_navio(self.estado, nav_grande["id"], "CAIS-1")[0])

        # Atribuição otimizada deve colocar o Grande no CAIS-4 e o Pequeno no CAIS-1
        atribuir_cais_otimizado(self.estado)
        self.assertEqual(nav_grande["cais_id"], "CAIS-4")
        self.assertEqual(nav_peq["cais_id"], "CAIS-1")

        # Impedir ocupação simultânea do mesmo cais
        _, _, nav_extra = registar_navio(self.estado, "Outro", "Pequeno", 2)
        self.assertFalse(atracar_navio(self.estado, nav_extra["id"], "CAIS-1")[0])

    def test_operacao_ciclo_contentores_e_financas(self) -> None:
        _, _, nav = registar_navio(
            self.estado, "Descarga Rapida", "Pequeno", 2, operacao="Descarga", tipo_carga="Refrigerado"
        )
        atribuir_cais_otimizado(self.estado)

        # CAIS-1 tem 1 grua (2 contentores/ciclo), logo conclui em 1 ciclo
        executar_ciclo_portuario(self.estado)
        self.assertEqual(nav["estado"], "Concluído")
        self.assertEqual(len(self.estado["contentores"]), 2)

        ind = obter_indicadores(self.estado)
        self.assertGreater(ind["receitas"], 0.0)
        self.assertEqual(ind["navios_concluidos"], 1)

        # Expedir um contentor do pátio
        cid = self.estado["contentores"][0]["id"]
        self.assertTrue(expedir_contentor(self.estado, cid)[0])
        self.assertEqual(len(self.estado["contentores"]), 1)

    def test_persistencia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "porto.json"
            registar_navio(self.estado, "N/M Teste", "Médio", 5)
            self.assertTrue(guardar_porto(self.estado, caminho)[0])
            dados, _ = carregar_porto(caminho)
            self.assertIsNotNone(dados)
            self.assertEqual(len(dados["navios"]), 1)
            self.assertIsNone(carregar_porto(Path(tmp) / "ausente.json")[0])


if __name__ == "__main__":
    unittest.main()
