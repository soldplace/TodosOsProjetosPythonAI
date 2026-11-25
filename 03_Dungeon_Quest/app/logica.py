"""Lógica de jogo do RPG Dungeon Quest (masmorra, combate, inventário e evolução)."""

from __future__ import annotations

import copy
import random
from typing import Any

from app.dados import (
    CHEFE_FINAL,
    COLUNAS_MASMORRA,
    ITENS_CATALOGO,
    LINHAS_MASMORRA,
    MONSTROS_COMUNS,
)


def _obter_item_por_id(item_id: str) -> dict[str, Any]:
    for item in ITENS_CATALOGO:
        if item["id"] == item_id:
            return copy.deepcopy(item)
    return copy.deepcopy(ITENS_CATALOGO[0])


def criar_nova_aventura(
    nome_heroi: str = "Aventureiro", semente: int | None = None
) -> dict[str, Any]:
    """Gera uma nova masmorra 5x5 e inicializa a personagem."""
    gerador = random.Random(semente)
    nome_limpo = nome_heroi.strip() or "Aventureiro"

    salas: list[dict[str, Any]] = []
    for linha in range(LINHAS_MASMORRA):
        for coluna in range(COLUNAS_MASMORRA):
            if (linha, coluna) == (0, 0):
                sala = {
                    "linha": linha,
                    "coluna": coluna,
                    "tipo": "entrada",
                    "visitada": True,
                    "concluida": True,
                    "monstro": None,
                    "tesouro": None,
                }
            elif (linha, coluna) == (LINHAS_MASMORRA - 1, COLUNAS_MASMORRA - 1):
                chefe = copy.deepcopy(CHEFE_FINAL)
                chefe["hp_max"] = chefe["hp"]
                sala = {
                    "linha": linha,
                    "coluna": coluna,
                    "tipo": "chefe",
                    "visitada": False,
                    "concluida": False,
                    "monstro": chefe,
                    "tesouro": None,
                }
            else:
                sorteio = gerador.random()
                if sorteio < 0.45:
                    monstro = copy.deepcopy(gerador.choice(MONSTROS_COMUNS))
                    monstro["hp_max"] = monstro["hp"]
                    monstro["chefe"] = False
                    sala = {
                        "linha": linha,
                        "coluna": coluna,
                        "tipo": "monstro",
                        "visitada": False,
                        "concluida": False,
                        "monstro": monstro,
                        "tesouro": None,
                    }
                elif sorteio < 0.72:
                    item_tesouro = copy.deepcopy(gerador.choice(ITENS_CATALOGO))
                    sala = {
                        "linha": linha,
                        "coluna": coluna,
                        "tipo": "tesouro",
                        "visitada": False,
                        "concluida": False,
                        "monstro": None,
                        "tesouro": item_tesouro,
                    }
                elif sorteio < 0.86:
                    sala = {
                        "linha": linha,
                        "coluna": coluna,
                        "tipo": "fonte",
                        "visitada": False,
                        "concluida": False,
                        "monstro": None,
                        "tesouro": None,
                    }
                else:
                    sala = {
                        "linha": linha,
                        "coluna": coluna,
                        "tipo": "vazia",
                        "visitada": False,
                        "concluida": True,
                        "monstro": None,
                        "tesouro": None,
                    }
            salas.append(sala)

    return {
        "estado_jogo": "em_curso",  # "em_curso", "vitoria", "derrota"
        "motivo_fim": "",
        "em_combate": False,
        "defendendo": False,
        "posicao": [0, 0],
        "posicao_anterior": [0, 0],
        "heroi": {
            "nome": nome_limpo,
            "nivel": 1,
            "xp": 0,
            "xp_proximo": 50,
            "hp": 45,
            "hp_max": 45,
            "ataque_base": 8,
            "defesa_base": 3,
            "ouro": 20,
            "arma": {"id": "adaga_inicial", "nome": "Adaga Simples", "tipo": "arma", "bonus": 2, "descricao": "+2 Ataque"},
            "armadura": {"id": "tunica", "nome": "Túnica de Couro", "tipo": "armadura", "bonus": 1, "descricao": "+1 Defesa"},
            "inventario": [_obter_item_por_id("pocao_menor"), _obter_item_por_id("pocao_menor")],
        },
        "salas": salas,
        "registo": [
            f"{nome_limpo} entrou nas Profundezas Púrpuras em busca de Malakor!"
        ],
    }


def obter_sala(estado: dict[str, Any], linha: int, coluna: int) -> dict[str, Any] | None:
    """Devolve a sala nas coordenadas indicadas ou None se fora dos limites."""
    if not (0 <= linha < LINHAS_MASMORRA and 0 <= coluna < COLUNAS_MASMORRA):
        return None
    indice = linha * COLUNAS_MASMORRA + coluna
    return estado["salas"][indice]


def calcular_ataque_total(estado: dict[str, Any]) -> int:
    """Calcula o ataque total do herói somando ataque base e arma equipada."""
    heroi = estado["heroi"]
    bonus_arma = heroi["arma"]["bonus"] if heroi.get("arma") else 0
    return heroi["ataque_base"] + bonus_arma


def calcular_defesa_total(estado: dict[str, Any]) -> int:
    """Calcula a defesa total do herói somando defesa base e armadura equipada."""
    heroi = estado["heroi"]
    bonus_arm = heroi["armadura"]["bonus"] if heroi.get("armadura") else 0
    return heroi["defesa_base"] + bonus_arm


def _adicionar_xp(estado: dict[str, Any], xp_ganho: int) -> list[str]:
    """Adiciona XP e processa eventuais subidas de nível."""
    mensagens: list[str] = []
    heroi = estado["heroi"]
    heroi["xp"] += xp_ganho
    while heroi["xp"] >= heroi["xp_proximo"]:
        heroi["xp"] -= heroi["xp_proximo"]
        heroi["nivel"] += 1
        heroi["xp_proximo"] = int(round(heroi["xp_proximo"] * 1.4))
        heroi["hp_max"] += 10
        heroi["ataque_base"] += 2
        heroi["defesa_base"] += 1
        heroi["hp"] = min(heroi["hp_max"], heroi["hp"] + 15)
        mensagens.append(
            f"SUBIDA DE NÍVEL! {heroi['nome']} atingiu o nível {heroi['nivel']} "
            "(+10 HP máx, +2 Ataque, +1 Defesa)."
        )
    return mensagens


def mover_heroi(estado: dict[str, Any], d_linha: int, d_coluna: int) -> tuple[bool, str]:
    """Move a personagem para uma sala adjacente se não estiver em combate."""
    if estado["estado_jogo"] != "em_curso":
        return False, "A aventura já terminou."
    if estado["em_combate"]:
        return False, "Não podes mover-te durante um combate! Derrota o inimigo ou tenta fugir."

    lin_atual, col_atual = estado["posicao"]
    nova_lin = lin_atual + d_linha
    nova_col = col_atual + d_coluna

    if abs(d_linha) + abs(d_coluna) != 1:
        return False, "Só te podes mover uma sala de cada vez (Norte, Sul, Este, Oeste)."

    sala = obter_sala(estado, nova_lin, nova_col)
    if sala is None:
        return False, "Parede de pedra sólida! Não há saída nessa direção."

    estado["posicao_anterior"] = [lin_atual, col_atual]
    estado["posicao"] = [nova_lin, nova_col]
    sala["visitada"] = True

    if sala["monstro"] is not None and not sala["concluida"]:
        estado["em_combate"] = True
        estado["defendendo"] = False
        msg = f"Encontraste {sala['monstro']['nome']}! O combate começou!"
        estado["registo"].append(msg)
        return True, msg

    if sala["tipo"] == "tesouro" and not sala["concluida"] and sala["tesouro"] is not None:
        item = sala["tesouro"]
        estado["heroi"]["inventario"].append(item)
        sala["concluida"] = True
        sala["tesouro"] = None
        msg = f"Abriste um baú e encontraste: {item['nome']}!"
        estado["registo"].append(msg)
        return True, msg

    if sala["tipo"] == "fonte" and not sala["concluida"]:
        heroi = estado["heroi"]
        cura = min(15, heroi["hp_max"] - heroi["hp"])
        heroi["hp"] += cura
        sala["concluida"] = True
        msg = f"Bebeste de uma fonte luminosa e recuperaste {cura} HP."
        estado["registo"].append(msg)
        return True, msg

    msg = f"Entraste na sala ({nova_lin + 1}, {nova_col + 1}). Tudo tranquilo."
    estado["registo"].append(msg)
    return True, msg


def _contra_ataque_monstro(estado: dict[str, Any], monstro: dict[str, Any], dado_monstro: int) -> str:
    """Executa o ataque do monstro contra o herói."""
    defesa = calcular_defesa_total(estado)
    if estado.get("defendendo"):
        defesa = int(round(defesa * 1.8))
        estado["defendendo"] = False

    dano = max(1, monstro["ataque"] + dado_monstro - defesa)
    estado["heroi"]["hp"] = max(0, estado["heroi"]["hp"] - dano)
    texto = f"{monstro['nome']} atacou (dado {dado_monstro}) e causou {dano} de dano!"

    if estado["heroi"]["hp"] <= 0:
        estado["estado_jogo"] = "derrota"
        estado["em_combate"] = False
        estado["motivo_fim"] = f"{estado['heroi']['nome']} tombou diante de {monstro['nome']}..."
        texto += " Foste derrotado!"
    return texto


def executar_ataque_combate(
    estado: dict[str, Any], dado_heroi: int | None = None, dado_monstro: int | None = None
) -> tuple[bool, str]:
    """Executa um turno de combate onde o herói ataca o monstro da sala atual."""
    if estado["estado_jogo"] != "em_curso" or not estado["em_combate"]:
        return False, "Não estás em combate."

    sala = obter_sala(estado, *estado["posicao"])
    if sala is None or sala["monstro"] is None:
        estado["em_combate"] = False
        return False, "Nenhum monstro na sala."

    monstro = sala["monstro"]
    d_heroi = dado_heroi if dado_heroi is not None else random.randint(1, 6)
    d_monstro = dado_monstro if dado_monstro is not None else random.randint(1, 4)

    dano = max(1, calcular_ataque_total(estado) + d_heroi - monstro["defesa"])
    monstro["hp"] = max(0, monstro["hp"] - dano)
    mensagens = [f"Atacaste {monstro['nome']} (dado {d_heroi}) causando {dano} de dano!"]

    if monstro["hp"] <= 0:
        sala["concluida"] = True
        estado["em_combate"] = False
        estado["heroi"]["ouro"] += monstro["ouro"]
        mensagens.append(
            f"{monstro['nome']} foi derrotado! Ganhaste {monstro['xp']} XP e {monstro['ouro']} ouro."
        )
        mensagens.extend(_adicionar_xp(estado, monstro["xp"]))

        if monstro.get("chefe"):
            estado["estado_jogo"] = "vitoria"
            estado["motivo_fim"] = (
                f"Vitória Épica! {estado['heroi']['nome']} derrotou {monstro['nome']} e conquistou a masmorra!"
            )
            mensagens.append(estado["motivo_fim"])
        elif random.random() < 0.40:
            drop = _obter_item_por_id("pocao_menor")
            estado["heroi"]["inventario"].append(drop)
            mensagens.append(f"O inimigo deixou cair: {drop['nome']}!")
    else:
        mensagens.append(_contra_ataque_monstro(estado, monstro, d_monstro))

    texto_final = " ".join(mensagens)
    estado["registo"].append(texto_final)
    return True, texto_final


def defender_em_combate(estado: dict[str, Any], dado_monstro: int | None = None) -> tuple[bool, str]:
    """Assume postura defensiva, recupera 3 HP e reduz dano do contra-ataque."""
    if estado["estado_jogo"] != "em_curso" or not estado["em_combate"]:
        return False, "Não estás em combate."

    sala = obter_sala(estado, *estado["posicao"])
    if sala is None or sala["monstro"] is None:
        return False, "Nenhum monstro na sala."

    heroi = estado["heroi"]
    cura = min(3, heroi["hp_max"] - heroi["hp"])
    heroi["hp"] += cura
    estado["defendendo"] = True

    d_monstro = dado_monstro if dado_monstro is not None else random.randint(1, 4)
    resp = _contra_ataque_monstro(estado, sala["monstro"], d_monstro)
    msg = f"Assumiste guarda defensiva (+{cura} HP). {resp}"
    estado["registo"].append(msg)
    return True, msg


def fugir_combate(estado: dict[str, Any], dado_fuga: int | None = None) -> tuple[bool, str]:
    """Tenta fugir para a sala anterior (não permitido contra o chefe final)."""
    if estado["estado_jogo"] != "em_curso" or not estado["em_combate"]:
        return False, "Não estás em combate."

    sala = obter_sala(estado, *estado["posicao"])
    if sala and sala["monstro"] and sala["monstro"].get("chefe"):
        return False, "Não é possível fugir da câmara do Chefe Final!"

    rolagem = dado_fuga if dado_fuga is not None else random.randint(1, 6)
    if rolagem >= 3:
        estado["em_combate"] = False
        estado["posicao"] = list(estado["posicao_anterior"])
        msg = f"Fugiste com sucesso (dado {rolagem}) para a sala anterior!"
        estado["registo"].append(msg)
        return True, msg

    d_monstro = random.randint(1, 4)
    resp = _contra_ataque_monstro(estado, sala["monstro"], d_monstro)
    msg = f"Fuga falhou (dado {rolagem})! {resp}"
    estado["registo"].append(msg)
    return False, msg


def usar_ou_equipar_item(estado: dict[str, Any], indice_item: int) -> tuple[bool, str]:
    """Usa uma poção ou equipa uma arma/armadura do inventário."""
    if estado["estado_jogo"] != "em_curso":
        return False, "A aventura já terminou."

    inv = estado["heroi"]["inventario"]
    if not (0 <= indice_item < len(inv)):
        return False, "Item inválido selecionado."

    item = inv[indice_item]
    heroi = estado["heroi"]

    if item["tipo"] == "pocao":
        if heroi["hp"] >= heroi["hp_max"]:
            return False, "Já tens os pontos de vida no máximo."
        cura = min(item["valor"], heroi["hp_max"] - heroi["hp"])
        heroi["hp"] += cura
        inv.pop(indice_item)
        msg = f"Usaste {item['nome']} e recuperaste {cura} HP."
        estado["registo"].append(msg)
        return True, msg

    if item["tipo"] == "arma":
        antiga = heroi.get("arma")
        heroi["arma"] = inv.pop(indice_item)
        if antiga is not None:
            inv.append(antiga)
        msg = f"Equipaste a arma: {heroi['arma']['nome']} (+{heroi['arma']['bonus']} Ataque)."
        estado["registo"].append(msg)
        return True, msg

    if item["tipo"] == "armadura":
        antiga = heroi.get("armadura")
        heroi["armadura"] = inv.pop(indice_item)
        if antiga is not None:
            inv.append(antiga)
        msg = f"Equipaste a armadura: {heroi['armadura']['nome']} (+{heroi['armadura']['bonus']} Defesa)."
        estado["registo"].append(msg)
        return True, msg

    return False, "Não é possível usar este item."
