"""Testes unitários da lógica e persistência da Colónia Marciana."""

from pathlib import Path
import sys
import tempfile
import unittest

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app.armazenamento import carregar_colonia, guardar_colonia
from app.dados import DIAS_OBJETIVO
from app.logica import (
    acolher_colonos,
    aplicar_evento_aleatorio,
    avancar_dia,
    calcular_balanco_previsto,
    calcular_capacidade_habitacional,
    construir_estrutura,
    criar_nova_colonia,
    melhorar_estrutura,
)


class TestColoniaMarciana(unittest.TestCase):
    """Testes para validar sobrevivência, recursos, construções e gravação."""

    def setUp(self) -> None:
        self.estado = criar_nova_colonia()

    def test_construir_e_melhorar_infraestrutura(self) -> None:
        balanco_antes = calcular_balanco_previsto(self.estado)
        ok, _ = construir_estrutura(self.estado, "painel_solar")
        self.assertTrue(ok)
        balanco_depois = calcular_balanco_previsto(self.estado)
        self.assertGreater(
            balanco_depois["producao"]["energia"], balanco_antes["producao"]["energia"]
        )

        ok_mel, _ = melhorar_estrutura(self.estado, "estufa")
        self.assertTrue(ok_mel)
        self.assertEqual(self.estado["estruturas"]["estufa"]["nivel"], 2)

        # Sem materiais suficientes deve falhar
        self.estado["recursos"]["materiais"] = 0
        self.assertFalse(construir_estrutura(self.estado, "cupula")[0])

    def test_acolher_colonos_respeita_capacidade(self) -> None:
        cap = calcular_capacidade_habitacional(self.estado)
        self.estado["populacao"] = cap
        ok, _ = acolher_colonos(self.estado, 2)
        self.assertFalse(ok)

        self.estado["populacao"] = cap - 2
        ok2, _ = acolher_colonos(self.estado, 2)
        self.assertTrue(ok2)
        self.assertEqual(self.estado["populacao"], cap)

    def test_eventos_e_tempestade(self) -> None:
        prod_normal = calcular_balanco_previsto(self.estado)["producao"]["energia"]
        aplicar_evento_aleatorio(self.estado, evento_forcado="tempestade_poeira")
        self.assertGreater(self.estado["dias_tempestade"], 0)
        prod_temp = calcular_balanco_previsto(self.estado)["producao"]["energia"]
        self.assertLess(prod_temp, prod_normal)

    def test_crise_recursos_e_derrota(self) -> None:
        self.estado["recursos"]["agua"] = 0
        self.estado["recursos"]["oxigenio"] = 0
        self.estado["recursos"]["alimentos"] = 0
        self.estado["estruturas"]["extrator_agua"]["quantidade"] = 0
        self.estado["estruturas"]["gerador_oxigenio"]["quantidade"] = 0
        self.estado["estruturas"]["estufa"]["quantidade"] = 0
        self.estado["populacao"] = 2

        avancar_dia(self.estado, permitir_evento=False)
        self.assertEqual(self.estado["estado_simulacao"], "derrota")

    def test_vitoria_ao_completar_objetivo(self) -> None:
        self.estado["dia"] = DIAS_OBJETIVO
        avancar_dia(self.estado, permitir_evento=False)
        self.assertEqual(self.estado["estado_simulacao"], "vitoria")

    def test_persistencia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "colonia.json"
            self.estado["dia"] = 12
            ok, _ = guardar_colonia(self.estado, caminho)
            self.assertTrue(ok)
            dados, _ = carregar_colonia(caminho)
            self.assertIsNotNone(dados)
            self.assertEqual(dados["dia"], 12)
            self.assertIsNone(carregar_colonia(Path(tmp) / "inexistente.json")[0])


if __name__ == "__main__":
    unittest.main()
