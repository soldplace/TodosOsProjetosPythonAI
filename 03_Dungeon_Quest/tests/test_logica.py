"""Testes unitários da lógica e persistência de Dungeon Quest."""

from pathlib import Path
import sys
import tempfile
import unittest

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app.armazenamento import carregar_aventura, guardar_aventura
from app.logica import (
    calcular_ataque_total,
    calcular_defesa_total,
    criar_nova_aventura,
    defender_em_combate,
    executar_ataque_combate,
    fugir_combate,
    mover_heroi,
    obter_sala,
    usar_ou_equipar_item,
)


class TestDungeonQuest(unittest.TestCase):
    """Testes das regras de exploração, combate, inventário e persistência."""

    def setUp(self) -> None:
        self.estado = criar_nova_aventura("Valente", semente=10)

    def test_movimento_limites_e_combate(self) -> None:
        # Não pode sair do mapa para norte a partir de (0, 0)
        ok_parede, _ = mover_heroi(self.estado, -1, 0)
        self.assertFalse(ok_parede)

        # Forçar monstro na sala (0, 1) para testar início de combate
        sala_dir = obter_sala(self.estado, 0, 1)
        sala_dir["tipo"] = "monstro"
        sala_dir["concluida"] = False
        sala_dir["monstro"] = {
            "nome": "Goblin Teste",
            "hp": 10,
            "hp_max": 10,
            "ataque": 5,
            "defesa": 1,
            "xp": 60,
            "ouro": 10,
            "chefe": False,
        }
        ok_mov, _ = mover_heroi(self.estado, 0, 1)
        self.assertTrue(ok_mov)
        self.assertTrue(self.estado["em_combate"])

        # Não pode mover enquanto está em combate
        self.assertFalse(mover_heroi(self.estado, 1, 0)[0])

        # Derrotar o monstro e verificar subida de nível (xp=60 > 50)
        executar_ataque_combate(self.estado, dado_heroi=6, dado_monstro=1)
        self.assertFalse(self.estado["em_combate"])
        self.assertEqual(self.estado["heroi"]["nivel"], 2)

    def test_fuga_e_defesa(self) -> None:
        sala_abaixo = obter_sala(self.estado, 1, 0)
        sala_abaixo["tipo"] = "monstro"
        sala_abaixo["concluida"] = False
        sala_abaixo["monstro"] = {
            "nome": "Esqueleto",
            "hp": 30,
            "hp_max": 30,
            "ataque": 6,
            "defesa": 2,
            "xp": 20,
            "ouro": 10,
            "chefe": False,
        }
        mover_heroi(self.estado, 1, 0)
        self.assertTrue(defender_em_combate(self.estado, dado_monstro=1)[0])

        # Fugir com dado >= 3 regressa a (0,0)
        ok_fuga, _ = fugir_combate(self.estado, dado_fuga=5)
        self.assertTrue(ok_fuga)
        self.assertEqual(self.estado["posicao"], [0, 0])

    def test_chefe_vitoria_e_derrota(self) -> None:
        # Colocar herói adjacente ao chefe (4, 3) -> (4, 4)
        self.estado["posicao"] = [4, 3]
        self.estado["em_combate"] = False
        mover_heroi(self.estado, 0, 1)
        self.assertTrue(self.estado["em_combate"])
        # Não pode fugir do chefe
        self.assertFalse(fugir_combate(self.estado, dado_fuga=6)[0])

        # Reduzir HP do chefe para vencer num golpe
        sala_chefe = obter_sala(self.estado, 4, 4)
        sala_chefe["monstro"]["hp"] = 5
        executar_ataque_combate(self.estado, dado_heroi=6, dado_monstro=1)
        self.assertEqual(self.estado["estado_jogo"], "vitoria")

    def test_inventario_equipar_e_curar(self) -> None:
        heroi = self.estado["heroi"]
        heroi["hp"] = 20
        atk_antes = calcular_ataque_total(self.estado)
        def_antes = calcular_defesa_total(self.estado)

        heroi["inventario"].append(
            {"id": "espada", "nome": "Espada Rúnica", "tipo": "arma", "bonus": 6, "descricao": "+6 ATQ"}
        )
        heroi["inventario"].append(
            {"id": "arm", "nome": "Armadura Aço", "tipo": "armadura", "bonus": 4, "descricao": "+4 DEF"}
        )

        # Usar poção no índice 0
        self.assertTrue(usar_ou_equipar_item(self.estado, 0)[0])
        self.assertEqual(heroi["hp"], 40)

        # Equipar arma e armadura
        idx_espada = next(i for i, x in enumerate(heroi["inventario"]) if x["tipo"] == "arma")
        self.assertTrue(usar_ou_equipar_item(self.estado, idx_espada)[0])
        self.assertGreater(calcular_ataque_total(self.estado), atk_antes)

        idx_arm = next(i for i, x in enumerate(heroi["inventario"]) if x["tipo"] == "armadura")
        self.assertTrue(usar_ou_equipar_item(self.estado, idx_arm)[0])
        self.assertGreater(calcular_defesa_total(self.estado), def_antes)

    def test_persistencia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "dungeon.json"
            self.estado["heroi"]["ouro"] = 999
            self.assertTrue(guardar_aventura(self.estado, caminho)[0])
            dados, _ = carregar_aventura(caminho)
            self.assertIsNotNone(dados)
            self.assertEqual(dados["heroi"]["ouro"], 999)
            self.assertIsNone(carregar_aventura(Path(tmp) / "falta.json")[0])


if __name__ == "__main__":
    unittest.main()
