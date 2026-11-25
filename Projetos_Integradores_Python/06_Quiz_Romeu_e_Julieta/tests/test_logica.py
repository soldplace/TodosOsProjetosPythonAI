"""Testes unitários do banco de perguntas, algoritmo adaptativo e classificações."""

from pathlib import Path
import sys
import tempfile
import unittest

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app.armazenamento import carregar_classificacoes, guardar_resultado_sessao
from app.dados import PERGUNTAS
from app.logica import (
    criar_nova_sessao,
    responder_pergunta,
    selecionar_proxima_pergunta,
)


class TestQuizRomeuJulieta(unittest.TestCase):
    """Testes para validar conteúdo, adaptação de dificuldade, pontuação e ranking."""

    def test_integridade_banco_perguntas(self) -> None:
        self.assertGreaterEqual(len(PERGUNTAS), 20)
        categorias = {p["categoria"] for p in PERGUNTAS}
        self.assertEqual(
            categorias,
            {"Personagens", "Enredo", "Acontecimentos", "Temas da obra", "Contexto literário"},
        )
        dificuldades = {p["dificuldade"] for p in PERGUNTAS}
        self.assertEqual(dificuldades, {"Fácil", "Média", "Difícil"})
        for p in PERGUNTAS:
            self.assertEqual(len(p["opcoes"]), 4)
            self.assertIn(p["indice_correto"], (0, 1, 2, 3))
            self.assertTrue(p["explicacao"])

    def test_adaptacao_sobe_e_desce(self) -> None:
        sessao = criar_nova_sessao("Julieta", total_perguntas=6)
        self.assertEqual(sessao["dificuldade_atual"], "Média")

        # 2 respostas certas seguidas -> sobe para Difícil
        for _ in range(2):
            p = selecionar_proxima_pergunta(sessao, semente=1)
            self.assertEqual(p["dificuldade"], "Média")
            ok, res = responder_pergunta(sessao, p["indice_correto"])
            self.assertTrue(ok)
            self.assertTrue(res["correta"])

        self.assertEqual(sessao["dificuldade_atual"], "Difícil")
        self.assertGreater(sessao["pontuacao"], 0)

        # 2 respostas erradas seguidas -> desce de Difícil para Média
        for _ in range(2):
            p = selecionar_proxima_pergunta(sessao, semente=2)
            indice_errado = (p["indice_correto"] + 1) % 4
            responder_pergunta(sessao, indice_errado)

        self.assertEqual(sessao["dificuldade_atual"], "Média")

        # Mais 2 erradas -> desce para Fácil
        for _ in range(2):
            p = selecionar_proxima_pergunta(sessao, semente=3)
            indice_errado = (p["indice_correto"] + 1) % 4
            responder_pergunta(sessao, indice_errado)

        self.assertEqual(sessao["dificuldade_atual"], "Fácil")
        self.assertTrue(sessao["terminado"])

    def test_nome_vazio_e_opcao_invalida(self) -> None:
        with self.assertRaises(ValueError):
            criar_nova_sessao("   ")

        sessao = criar_nova_sessao("Romeu", total_perguntas=3)
        selecionar_proxima_pergunta(sessao)
        ok, _ = responder_pergunta(sessao, 9)
        self.assertFalse(ok)

    def test_persistencia_classificacoes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "ranking.json"
            s1 = criar_nova_sessao("Ana", total_perguntas=2)
            p1 = selecionar_proxima_pergunta(s1)
            responder_pergunta(s1, p1["indice_correto"])
            guardar_resultado_sessao(s1, caminho)

            s2 = criar_nova_sessao("Bruno", total_perguntas=2)
            for _ in range(2):
                p = selecionar_proxima_pergunta(s2)
                responder_pergunta(s2, p["indice_correto"])
            _, ranking, _ = guardar_resultado_sessao(s2, caminho)

            self.assertEqual(len(ranking), 2)
            # Bruno tem pontuação maior e deve surgir em 1.º lugar
            self.assertEqual(ranking[0]["jogador"], "Bruno")
            self.assertEqual(carregar_classificacoes(Path(tmp) / "nao.json"), [])


if __name__ == "__main__":
    unittest.main()
