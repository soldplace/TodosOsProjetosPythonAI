"""Lógica de simulação da Colónia Marciana."""

from __future__ import annotations

import copy
import random
from typing import Any

from app.dados import (
    CAPACIDADE_BASE_CUPULA,
    CONSUMO_POR_HABITANTE,
    DIAS_OBJETIVO,
    ESTRUTURAS_INICIAIS,
    EVENTOS_MARCIANOS,
    INFRAESTRUTURAS,
    LIMITES_RECURSOS,
    POPULACAO_INICIAL,
    RECURSOS_INICIAIS,
)


def criar_nova_colonia() -> dict[str, Any]:
    """Cria o estado inicial de uma nova simulação em Marte."""
    return {
        "dia": 1,
        "estado_simulacao": "em_curso",  # "em_curso", "vitoria", "derrota"
        "motivo_fim": "",
        "populacao": POPULACAO_INICIAL,
        "moral": 85,  # 0 a 100
        "dias_tempestade": 0,
        "recursos": dict(RECURSOS_INICIAIS),
        "estruturas": copy.deepcopy(ESTRUTURAS_INICIAIS),
        "estatisticas": {
            "construcoes_feitas": 0,
            "melhorias_feitas": 0,
            "eventos_enfrentados": 0,
            "colonos_perdidos": 0,
            "colonos_chegados": 0,
        },
        "relatorio_ultimo_dia": [
            "Sol 1: Aterragens concluídas. Mantém a colónia viva durante 30 sóis!"
        ],
        "historico": [
            "Sol 1: Colónia Ares-1 inicializada com 12 colonos."
        ],
    }


def calcular_capacidade_habitacional(estado: dict[str, Any]) -> int:
    """Calcula a lotação máxima de habitantes nas cúpulas."""
    cupula = estado["estruturas"]["cupula"]
    return CAPACIDADE_BASE_CUPULA + (cupula["quantidade"] * cupula["nivel"] * 8)


def calcular_balanco_previsto(estado: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Calcula a produção e o consumo previstos para o próximo dia."""
    producao = {"energia": 0, "agua": 0, "oxigenio": 0, "alimentos": 0, "materiais": 0}
    consumo = {"energia": 0, "agua": 0, "oxigenio": 0, "alimentos": 0, "materiais": 0}

    fator_solar = 0.60 if estado.get("dias_tempestade", 0) > 0 else 1.0

    for chave, dados_est in estado["estruturas"].items():
        espec = INFRAESTRUTURAS[chave]
        qtd = dados_est["quantidade"]
        nivel = dados_est["nivel"]
        multiplicador = qtd * (1.0 + 0.35 * (nivel - 1))

        if espec["energia_produzida"] > 0:
            producao["energia"] += int(round(espec["energia_produzida"] * multiplicador * fator_solar))
        consumo["energia"] += int(round(espec["energia_consumida"] * qtd * (1.0 + 0.15 * (nivel - 1))))

        for rec, val in espec["producao"].items():
            producao[rec] += int(round(val * multiplicador))

    pop = estado["populacao"]
    for rec, cons_hab in CONSUMO_POR_HABITANTE.items():
        consumo[rec] += pop * cons_hab

    return {"producao": producao, "consumo": consumo}


def construir_estrutura(estado: dict[str, Any], chave: str) -> tuple[bool, str]:
    """Constrói uma nova unidade de uma infraestrutura existente."""
    if estado["estado_simulacao"] != "em_curso":
        return False, "A simulação já terminou."
    if chave not in INFRAESTRUTURAS:
        return False, "Infraestrutura inválida."

    custo = INFRAESTRUTURAS[chave]["custo_construir"]
    faltas = [
        f"{k} ({v - estado['recursos'].get(k, 0)} em falta)"
        for k, v in custo.items()
        if estado["recursos"].get(k, 0) < v
    ]
    if faltas:
        return False, "Recursos insuficientes: " + ", ".join(faltas)

    for k, v in custo.items():
        estado["recursos"][k] -= v

    estado["estruturas"][chave]["quantidade"] += 1
    estado["estatisticas"]["construcoes_feitas"] += 1
    msg = f"Construída nova unidade de {INFRAESTRUTURAS[chave]['nome']}."
    estado["historico"].append(f"Sol {estado['dia']}: {msg}")
    return True, msg


def melhorar_estrutura(estado: dict[str, Any], chave: str) -> tuple[bool, str]:
    """Melhora o nível de eficiência de uma infraestrutura (até nível 5)."""
    if estado["estado_simulacao"] != "em_curso":
        return False, "A simulação já terminou."
    if chave not in INFRAESTRUTURAS:
        return False, "Infraestrutura inválida."

    est = estado["estruturas"][chave]
    if est["nivel"] >= 5:
        return False, f"{INFRAESTRUTURAS[chave]['nome']} já está no nível máximo (5)."

    fator = 1.0 + 0.4 * (est["nivel"] - 1)
    custo = {k: int(round(v * fator)) for k, v in INFRAESTRUTURAS[chave]["custo_melhorar"].items()}
    faltas = [
        f"{k} ({v - estado['recursos'].get(k, 0)} em falta)"
        for k, v in custo.items()
        if estado["recursos"].get(k, 0) < v
    ]
    if faltas:
        return False, "Recursos insuficientes: " + ", ".join(faltas)

    for k, v in custo.items():
        estado["recursos"][k] -= v

    est["nivel"] += 1
    estado["estatisticas"]["melhorias_feitas"] += 1
    msg = f"{INFRAESTRUTURAS[chave]['nome']} melhorado para o nível {est['nivel']}."
    estado["historico"].append(f"Sol {estado['dia']}: {msg}")
    return True, msg


def acolher_colonos(estado: dict[str, Any], quantidade: int = 2) -> tuple[bool, str]:
    """Permite recrutar colonos da reserva orbital se houver capacidade e recursos."""
    if estado["estado_simulacao"] != "em_curso":
        return False, "A simulação já terminou."
    if quantidade <= 0:
        return False, "A quantidade tem de ser positiva."

    cap = calcular_capacidade_habitacional(estado)
    if estado["populacao"] + quantidade > cap:
        return False, f"Capacidade insuficiente nas cúpulas ({estado['populacao']}/{cap}). Constrói ou melhora uma cúpula."

    custo_alimentos = quantidade * 8
    custo_agua = quantidade * 6
    if estado["recursos"]["alimentos"] < custo_alimentos or estado["recursos"]["agua"] < custo_agua:
        return False, f"Requer {custo_alimentos} alimentos e {custo_agua} água para acolher {quantidade} colonos."

    estado["recursos"]["alimentos"] -= custo_alimentos
    estado["recursos"]["agua"] -= custo_agua
    estado["populacao"] += quantidade
    estado["estatisticas"]["colonos_chegados"] += quantidade
    msg = f"Acolhidos {quantidade} novos colonos! População atual: {estado['populacao']}."
    estado["historico"].append(f"Sol {estado['dia']}: {msg}")
    return True, msg


def aplicar_evento_aleatorio(
    estado: dict[str, Any], evento_forcado: str | None = None, probabilidade: float = 0.45
) -> str | None:
    """Aplica um evento aleatório (ou específico para testes) à colónia."""
    if evento_forcado is None and random.random() > probabilidade:
        return None

    if evento_forcado is not None:
        correspondencias = [e for e in EVENTOS_MARCIANOS if e["id"] == evento_forcado]
        if not correspondencias:
            return None
        evento = correspondencias[0]
    else:
        evento = random.choice(EVENTOS_MARCIANOS)

    estado["estatisticas"]["eventos_enfrentados"] += 1
    eid = evento["id"]

    if eid == "tempestade_poeira":
        estado["dias_tempestade"] = max(estado["dias_tempestade"], 2)
    elif eid == "falha_eletrica":
        estado["recursos"]["energia"] = max(0, estado["recursos"]["energia"] - 25)
    elif eid == "fuga_agua":
        estado["recursos"]["agua"] = max(0, estado["recursos"]["agua"] - 22)
    elif eid == "descoberta_cientifica":
        estado["recursos"]["agua"] = min(LIMITES_RECURSOS["agua"], estado["recursos"]["agua"] + 25)
        estado["recursos"]["oxigenio"] = min(LIMITES_RECURSOS["oxigenio"], estado["recursos"]["oxigenio"] + 25)
        estado["moral"] = min(100, estado["moral"] + 5)
    elif eid == "capsula_suprimentos":
        estado["recursos"]["alimentos"] = min(LIMITES_RECURSOS["alimentos"], estado["recursos"]["alimentos"] + 35)
        estado["recursos"]["materiais"] = min(LIMITES_RECURSOS["materiais"], estado["recursos"]["materiais"] + 35)
    elif eid == "novos_colonos":
        cap = calcular_capacidade_habitacional(estado)
        espaco = cap - estado["populacao"]
        if espaco >= 1:
            novos = min(2, espaco)
            estado["populacao"] += novos
            estado["estatisticas"]["colonos_chegados"] += novos
            return f"Evento: {evento['titulo']} — +{novos} colonos chegaram à colónia!"
        return f"Evento: {evento['titulo']} — Sem espaço nas cúpulas para novos colonos."

    return f"Evento: {evento['titulo']} — {evento['descricao']}"


def avancar_dia(
    estado: dict[str, Any], evento_forcado: str | None = None, permitir_evento: bool = True
) -> list[str]:
    """Processa o fim de um dia marciano: energia, produção, consumo, eventos e estado."""
    if estado["estado_simulacao"] != "em_curso":
        return ["A simulação já terminou."]

    relatorio: list[str] = []
    balanco = calcular_balanco_previsto(estado)
    prod = balanco["producao"]
    cons = balanco["consumo"]

    # 1. Energia: produção solar + reserva vs consumo das máquinas
    energia_disponivel = estado["recursos"]["energia"] + prod["energia"]
    if energia_disponivel >= cons["energia"]:
        estado["recursos"]["energia"] = min(
            LIMITES_RECURSOS["energia"], energia_disponivel - cons["energia"]
        )
        eficiencia_maquinas = 1.0
    else:
        estado["recursos"]["energia"] = 0
        eficiencia_maquinas = max(0.35, energia_disponivel / max(1, cons["energia"]))
        relatorio.append(
            f"ALERTA ENERGÉTICO: Energia insuficiente! Sistemas operaram a {int(eficiencia_maquinas * 100)}%."
        )

    # 2. Produção de recursos vitais e materiais
    for rec in ("agua", "oxigenio", "alimentos", "materiais"):
        ganho = int(round(prod[rec] * eficiencia_maquinas))
        estado["recursos"][rec] = min(LIMITES_RECURSOS[rec], estado["recursos"][rec] + ganho)

    # 3. Consumo dos colonos
    escassez = []
    for rec in ("agua", "oxigenio", "alimentos"):
        if estado["recursos"][rec] >= cons[rec]:
            estado["recursos"][rec] -= cons[rec]
        else:
            estado["recursos"][rec] = 0
            escassez.append(rec)

    if escassez:
        perda_moral = 15 * len(escassez)
        estado["moral"] = max(0, estado["moral"] - perda_moral)
        baixas = max(1, len(escassez) * 2)
        perdas_reais = min(estado["populacao"], baixas)
        estado["populacao"] -= perdas_reais
        estado["estatisticas"]["colonos_perdidos"] += perdas_reais
        relatorio.append(
            f"CRISE DE SUPORTE DE VIDA ({', '.join(escassez)} em falta): "
            f"{perdas_reais} colonos não sobreviveram e a moral caiu -{perda_moral}%."
        )
    else:
        estado["moral"] = min(100, estado["moral"] + 2)

    # 4. Atualiza contador de tempestade
    if estado["dias_tempestade"] > 0:
        estado["dias_tempestade"] -= 1

    # 5. Evento aleatório
    if permitir_evento and estado["populacao"] > 0:
        msg_evento = aplicar_evento_aleatorio(estado, evento_forcado=evento_forcado)
        if msg_evento:
            relatorio.append(msg_evento)

    relatorio.insert(
        0,
        (
            f"Resumo Sol {estado['dia']}: +{prod['energia']}/-{cons['energia']} Energia | "
            f"+{int(round(prod['agua'] * eficiencia_maquinas))}/-{cons['agua']} Água | "
            f"+{int(round(prod['oxigenio'] * eficiencia_maquinas))}/-{cons['oxigenio']} O₂ | "
            f"+{int(round(prod['alimentos'] * eficiencia_maquinas))}/-{cons['alimentos']} Alim."
        ),
    )

    estado["relatorio_ultimo_dia"] = relatorio
    for linha in relatorio:
        estado["historico"].append(f"Sol {estado['dia']}: {linha}")
    if len(estado["historico"]) > 90:
        estado["historico"] = estado["historico"][-90:]

    # 6. Verificar vitória ou derrota
    if estado["populacao"] <= 0 or estado["moral"] <= 0:
        estado["populacao"] = max(0, estado["populacao"])
        estado["estado_simulacao"] = "derrota"
        estado["motivo_fim"] = (
            "A colónia entrou em colapso por falta de condições de sobrevivência."
        )
        relatorio.append(estado["motivo_fim"])
    elif estado["dia"] >= DIAS_OBJETIVO:
        estado["estado_simulacao"] = "vitoria"
        estado["motivo_fim"] = (
            f"Missão cumprida! A colónia sobreviveu aos {DIAS_OBJETIVO} sóis marcianos com "
            f"{estado['populacao']} habitantes."
        )
        relatorio.append(estado["motivo_fim"])
    else:
        estado["dia"] += 1

    return relatorio
