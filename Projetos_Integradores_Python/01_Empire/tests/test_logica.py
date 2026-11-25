"""Testes unitários da lógica e persistência do jogo Empire."""

from pathlib import Path
import sys
import tempfile
import unittest

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app.armazenamento import carregar_partida, guardar_partida
from app.dados import TOTAL_TERRITORIOS
from app.logica import (
    atacar_territorio,
    calcular_manutencao_turno,
    calcular_producao_turno,
    calcular_total_tropas,
    construir_melhoria,
    contar_territorios_por_dono,
    criar_novo_jogo,
    investigar_tecnologia,
    mover_tropas,
    obter_territorio,
    recrutar_soldados,
    sao_adjacentes,
    terminar_turno,
    verificar_fim_de_jogo,
)


class TestLogicaEmpire(unittest.TestCase):
    """Conjunto de testes para validar regras, combates e persistência."""

    def setUp(self) -> None:
        self.estado = criar_novo_jogo(semente=42)

    def test_inicializacao_mapa(self) -> None:
        self.assertEqual(len(self.estado["territorios"]), TOTAL_TERRITORIOS)
        contagem = contar_territorios_por_dono(self.estado)
        self.assertEqual(contagem["jogador"], 3)
        self.assertEqual(contagem["inimigo_1"], 3)
        self.assertEqual(contagem["inimigo_2"], 3)

    def test_adjacencia_territorios(self) -> None:
        t_20 = obter_territorio(self.estado, 20)  # (4,0)
        t_21 = obter_territorio(self.estado, 21)  # (4,1)
        t_15 = obter_territorio(self.estado, 15)  # (3,0)
        t_16 = obter_territorio(self.estado, 16)  # (3,1) diagonal
        self.assertTrue(sao_adjacentes(t_20, t_21))
        self.assertTrue(sao_adjacentes(t_20, t_15))
        self.assertFalse(sao_adjacentes(t_20, t_16))

    def test_recrutamento_valido_e_invalido(self) -> None:
        tropas_antes = calcular_total_tropas(self.estado, "jogador")
        ok, _ = recrutar_soldados(self.estado, 20, 4)
        self.assertTrue(ok)
        self.assertEqual(calcular_total_tropas(self.estado, "jogador"), tropas_antes + 4)

        # Quantidade inválida
        ok_neg, _ = recrutar_soldados(self.estado, 20, 0)
        self.assertFalse(ok_neg)

        # Território que não pertence ao jogador
        ok_inimigo, _ = recrutar_soldados(self.estado, 0, 2)
        self.assertFalse(ok_inimigo)

        # Recursos insuficientes
        ok_caro, _ = recrutar_soldados(self.estado, 20, 500)
        self.assertFalse(ok_caro)

    def test_mover_tropas(self) -> None:
        ok, _ = mover_tropas(self.estado, 20, 21, 5)
        self.assertTrue(ok)
        self.assertEqual(obter_territorio(self.estado, 20)["guarnicao"], 13)
        self.assertEqual(obter_territorio(self.estado, 21)["guarnicao"], 15)

        # Não pode deixar 0 tropas
        ok_vazio, _ = mover_tropas(self.estado, 20, 21, 13)
        self.assertFalse(ok_vazio)

    def test_melhoria_e_tecnologia(self) -> None:
        prod_base = calcular_producao_turno(self.estado)
        ok_mel, _ = construir_melhoria(self.estado, "mercado")
        self.assertTrue(ok_mel)
        prod_depois = calcular_producao_turno(self.estado)
        self.assertGreater(prod_depois["ouro"], prod_base["ouro"])

        # Requisito em falta
        ok_req, _ = investigar_tecnologia(self.estado, "taticas_cerco")
        self.assertFalse(ok_req)

        # Investigar agricultura e depois logistica
        self.estado["recursos"]["ouro"] = 1000
        self.estado["recursos"]["madeira"] = 1000
        self.estado["recursos"]["ferro"] = 1000
        self.assertTrue(investigar_tecnologia(self.estado, "agricultura")[0])
        manut_antes = calcular_manutencao_turno(self.estado)["ouro"]
        self.assertTrue(investigar_tecnologia(self.estado, "logistica")[0])
        manut_depois = calcular_manutencao_turno(self.estado)["ouro"]
        self.assertLessEqual(manut_depois, manut_antes)

    def test_combate_vitoria_e_derrota(self) -> None:
        # Território 16 (3,1) é adjacente a 21 (4,1) do jogador
        alvo = obter_territorio(self.estado, 16)
        alvo["dono"] = "neutro"
        alvo["guarnicao"] = 3
        alvo["defesa_base"] = 1.0

        venceu, _ = atacar_territorio(self.estado, 21, 16, 9, fator_sorte=1.0)
        self.assertTrue(venceu)
        self.assertEqual(alvo["dono"], "jogador")
        self.assertGreaterEqual(alvo["guarnicao"], 1)

        # Ataque fraco a território forte deve falhar
        alvo_forte = obter_territorio(self.estado, 11)  # (2,1) adjacente a 16 (3,1)
        alvo_forte["dono"] = "neutro"
        alvo_forte["guarnicao"] = 50
        venceu_f, _ = atacar_territorio(self.estado, 16, 11, 2, fator_sorte=1.0)
        self.assertFalse(venceu_f)
        self.assertEqual(alvo_forte["dono"], "neutro")

    def test_condicoes_vitoria_e_derrota(self) -> None:
        # Simular vitória: jogador domina tudo
        for t in self.estado["territorios"]:
            t["dono"] = "jogador"
        self.assertEqual(verificar_fim_de_jogo(self.estado), "vitoria")

        # Simular derrota: jogador fica sem territórios
        for t in self.estado["territorios"]:
            t["dono"] = "inimigo_1"
        self.assertEqual(verificar_fim_de_jogo(self.estado), "derrota")

    def test_terminar_turno_avanca_e_atualiza_recursos(self) -> None:
        turno_inicial = self.estado["turno"]
        res = terminar_turno(self.estado)
        self.assertEqual(self.estado["turno"], turno_inicial + 1)
        self.assertIn("producao", res)

    def test_guardar_e_carregar_partida(self) -> None:
        with tempfile.TemporaryDirectory() as pasta_tmp:
            caminho = Path(pasta_tmp) / "save.json"
            self.estado["turno"] = 7
            ok, _ = guardar_partida(self.estado, caminho)
            self.assertTrue(ok)

            carregado, _ = carregar_partida(caminho)
            self.assertIsNotNone(carregado)
            self.assertEqual(carregado["turno"], 7)

            # Ficheiro inexistente
            inex, _ = carregar_partida(Path(pasta_tmp) / "nao_existe.json")
            self.assertIsNone(inex)

            # Ficheiro corrompido
            corrompido = Path(pasta_tmp) / "corrompido.json"
            corrompido.write_text("{invalido", encoding="utf-8")
            res_corr, _ = carregar_partida(corrompido)
            self.assertIsNone(res_corr)


if __name__ == "__main__":
    unittest.main()
