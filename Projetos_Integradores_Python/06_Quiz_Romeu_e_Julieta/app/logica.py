"""Lógica do Quiz Adaptativo sobre Romeu e Julieta."""

from __future__ import annotations

import random
from typing import Any

from app.dados import (
    BONUS_SEQUENCIA,
    NIVEIS_DIFICULDADE,
    PERGUNTAS,
    PONTOS_POR_DIFICULDADE,
    TOTAL_PERGUNTAS_SESSAO,
)


def criar_nova_sessao(
    nome_jogador: str, total_perguntas: int = TOTAL_PERGUNTAS_SESSAO
) -> dict[str, Any]:
    """Cria o estado inicial de uma nova sessão do quiz adaptativo."""
    nome_limpo = nome_jogador.strip()
    if not nome_limpo:
        raise ValueError("O nome do jogador não pode estar vazio.")

    return {
        "jogador": nome_limpo,
        "total_perguntas": min(total_perguntas, len(PERGUNTAS)),
        "perguntas_respondidas": 0,
        "acertos": 0,
        "pontuacao": 0,
        "dificuldade_atual": "Média",
        "sequencia_acertos": 0,
        "sequencia_erros": 0,
        "melhor_sequencia": 0,
        "desempenho_recente": [],  # Lista de bools das últimas respostas
        "ids_usadas": [],
        "pergunta_atual": None,
        "terminado": False,
        "historico_respostas": [],
    }


def selecionar_proxima_pergunta(
    estado: dict[str, Any], semente: int | None = None
) -> dict[str, Any] | None:
    """
    Seleciona uma pergunta ainda não utilizada adequada à dificuldade atual.
    Se todas as perguntas do nível atual tiverem sido usadas, recorre ao nível mais próximo.
    """
    if estado["perguntas_respondidas"] >= estado["total_perguntas"]:
        estado["terminado"] = True
        estado["pergunta_atual"] = None
        return None

    gerador = random.Random(semente)
    usadas = set(estado["ids_usadas"])
    nivel_atual = estado["dificuldade_atual"]
    idx_nivel = NIVEIS_DIFICULDADE.index(nivel_atual)

    # Ordem de preferência: nível atual -> níveis adjacentes
    niveis_ordenados = sorted(
        NIVEIS_DIFICULDADE, key=lambda n: abs(NIVEIS_DIFICULDADE.index(n) - idx_nivel)
    )

    escolhida = None
    for nivel in niveis_ordenados:
        candidatas = [
            p for p in PERGUNTAS if p["dificuldade"] == nivel and p["id"] not in usadas
        ]
        if candidatas:
            escolhida = gerador.choice(candidatas)
            break

    estado["pergunta_atual"] = escolhida
    if escolhida is None:
        estado["terminado"] = True
    return escolhida


def _adaptar_dificuldade(estado: dict[str, Any]) -> str:
    """
    Algoritmo adaptativo real:
    - Sobe de dificuldade se o jogador tiver 2 acertos seguidos ou >= 2 acertos nas últimas 3
      quando já está estável.
    - Desce de dificuldade se tiver 2 erros seguidos ou 0/1 acerto nas últimas 3 após erro.
    """
    idx = NIVEIS_DIFICULDADE.index(estado["dificuldade_atual"])
    recente = estado["desempenho_recente"][-3:]

    if estado["sequencia_acertos"] >= 2 or (len(recente) == 3 and sum(recente) == 3):
        if idx < len(NIVEIS_DIFICULDADE) - 1:
            estado["dificuldade_atual"] = NIVEIS_DIFICULDADE[idx + 1]
            estado["sequencia_acertos"] = 0
            return f"Dificuldade aumentada para {estado['dificuldade_atual']}!"
    elif estado["sequencia_erros"] >= 2 or (
        len(recente) == 3 and sum(recente) <= 1 and not recente[-1]
    ):
        if idx > 0:
            estado["dificuldade_atual"] = NIVEIS_DIFICULDADE[idx - 1]
            estado["sequencia_erros"] = 0
            return f"Dificuldade ajustada para {estado['dificuldade_atual']}."

    return f"Dificuldade mantida em {estado['dificuldade_atual']}."


def responder_pergunta(
    estado: dict[str, Any], indice_resposta: int
) -> tuple[bool, dict[str, Any]]:
    """Avalia a resposta selecionada, atualiza pontuação e adapta a dificuldade."""
    pergunta = estado.get("pergunta_atual")
    if pergunta is None or estado["terminado"]:
        return False, {"erro": "Não há nenhuma pergunta ativa."}
    if not (0 <= indice_resposta < len(pergunta["opcoes"])):
        return False, {"erro": "Opção de resposta inválida."}

    correta = indice_resposta == pergunta["indice_correto"]
    estado["ids_usadas"].append(pergunta["id"])
    estado["perguntas_respondidas"] += 1
    estado["desempenho_recente"].append(correta)

    pontos_ganhos = 0
    if correta:
        estado["acertos"] += 1
        estado["sequencia_acertos"] += 1
        estado["sequencia_erros"] = 0
        estado["melhor_sequencia"] = max(
            estado["melhor_sequencia"], estado["sequencia_acertos"]
        )
        base = PONTOS_POR_DIFICULDADE[pergunta["dificuldade"]]
        bonus = max(0, estado["sequencia_acertos"] - 1) * BONUS_SEQUENCIA
        pontos_ganhos = base + bonus
        estado["pontuacao"] += pontos_ganhos
    else:
        estado["sequencia_erros"] += 1
        estado["sequencia_acertos"] = 0

    dificuldade_antes = estado["dificuldade_atual"]
    aviso_adaptacao = _adaptar_dificuldade(estado)

    registo_resp = {
        "id": pergunta["id"],
        "categoria": pergunta["categoria"],
        "dificuldade": pergunta["dificuldade"],
        "correta": correta,
        "pontos_ganhos": pontos_ganhos,
    }
    estado["historico_respostas"].append(registo_resp)

    if estado["perguntas_respondidas"] >= estado["total_perguntas"]:
        estado["terminado"] = True
        estado["pergunta_atual"] = None

    resultado = {
        "correta": correta,
        "resposta_correta": pergunta["opcoes"][pergunta["indice_correto"]],
        "explicacao": pergunta["explicacao"],
        "pontos_ganhos": pontos_ganhos,
        "dificuldade_antes": dificuldade_antes,
        "dificuldade_depois": estado["dificuldade_atual"],
        "aviso_adaptacao": aviso_adaptacao,
    }
    return True, resultado
