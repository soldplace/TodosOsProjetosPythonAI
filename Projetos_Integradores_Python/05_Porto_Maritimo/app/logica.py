"""Lógica operacional, logística, fila de espera e finanças do Porto Marítimo."""

from __future__ import annotations

import copy
import random
from typing import Any

from app.dados import (
    CAIS_INICIAIS,
    CUSTO_ESPERA_NAVIO_CICLO,
    CUSTO_OPERACIONAL_CAIS_CICLO,
    MOVIMENTACAO_POR_GRUA,
    NOMES_NAVIOS_EXEMPLO,
    ORDEM_DIMENSOES,
    ORDEM_PRIORIDADES,
    RECEITA_ATRACACAO_BASE,
    TIPOS_CONTENTOR,
)


def criar_novo_porto() -> dict[str, Any]:
    """Inicializa o estado completo de um porto marítimo operacional."""
    cais = []
    for item in CAIS_INICIAIS:
        cais.append(
            {
                "id": item["id"],
                "nome": item["nome"],
                "capacidade_dimensao": item["capacidade_dimensao"],
                "gruas": item["gruas"],
                "ocupado": False,
                "navio_id": None,
                "ciclos_ocupado": 0,
            }
        )

    estado = {
        "ciclo": 1,
        "proximo_navio_seq": 1,
        "proximo_contentor_seq": 1,
        "cais": cais,
        "navios": [],
        "contentores": [],
        "financas": {
            "receitas": 0.0,
            "custos": 0.0,
            "contentores_movimentados": 0,
            "navios_concluidos": 0,
        },
        "estatisticas": {
            "soma_espera_atracados": 0,
            "total_atracados": 0,
        },
        "historico": [
            "Ciclo 1: Terminal Portuário operacional e pronto a receber navios."
        ],
    }
    return estado


def obter_navio(estado: dict[str, Any], navio_id: str) -> dict[str, Any] | None:
    """Procura um navio pelo seu identificador."""
    for navio in estado["navios"]:
        if navio["id"] == navio_id:
            return navio
    return None


def obter_cais(estado: dict[str, Any], cais_id: str) -> dict[str, Any] | None:
    """Procura um cais pelo seu identificador."""
    for c in estado["cais"]:
        if c["id"] == cais_id:
            return c
    return None


def registar_navio(
    estado: dict[str, Any],
    nome: str,
    dimensao: str,
    num_contentores: int,
    operacao: str = "Descarga",
    prioridade: str = "Normal",
    tipo_carga: str = "Normal",
) -> tuple[bool, str, dict[str, Any] | None]:
    """Regista um novo navio na fila de espera do porto."""
    nome_limpo = nome.strip()
    if not nome_limpo:
        return False, "O nome do navio é obrigatório.", None
    if dimensao not in ORDEM_DIMENSOES:
        return False, "Dimensão inválida (escolhe Pequeno, Médio ou Grande).", None
    if not isinstance(num_contentores, int) or num_contentores <= 0 or num_contentores > 40:
        return False, "O número de contentores deve estar entre 1 e 40.", None
    if operacao not in ("Descarga", "Carga"):
        return False, "Operação inválida (escolhe Descarga ou Carga).", None
    if prioridade not in ORDEM_PRIORIDADES:
        return False, "Prioridade inválida.", None
    if tipo_carga not in TIPOS_CONTENTOR:
        return False, "Tipo de contentor inválido.", None

    navio_id = f"NAV-{estado['proximo_navio_seq']:03d}"
    estado["proximo_navio_seq"] += 1

    navio = {
        "id": navio_id,
        "nome": nome_limpo,
        "dimensao": dimensao,
        "operacao": operacao,
        "tipo_carga": tipo_carga,
        "prioridade": prioridade,
        "contentores_totais": num_contentores,
        "contentores_restantes": num_contentores,
        "estado": "Em Fila",  # "Em Fila", "Atracado", "Concluído"
        "cais_id": None,
        "ciclos_espera": 0,
        "ciclo_chegada": estado["ciclo"],
    }
    estado["navios"].append(navio)
    msg = (
        f"Ciclo {estado['ciclo']}: Navio {navio_id} ({nome_limpo}, {dimensao}, "
        f"{num_contentores} contentores {tipo_carga}, Prioridade {prioridade}) entrou na fila."
    )
    estado["historico"].append(msg)
    return True, msg, navio


def gerar_navio_aleatorio(estado: dict[str, Any]) -> tuple[bool, str, dict[str, Any] | None]:
    """Gera e regista um navio com parâmetros aleatórios realistas."""
    nome = random.choice(NOMES_NAVIOS_EXEMPLO)
    dim = random.choice(list(ORDEM_DIMENSOES.keys()))
    qtd = random.randint(4, 14) if dim != "Pequeno" else random.randint(2, 8)
    op = random.choice(["Descarga", "Carga"])
    prio = random.choices(["Normal", "Alta", "Urgente"], weights=[60, 28, 12], k=1)[0]
    tipo = random.choice(list(TIPOS_CONTENTOR.keys()))
    return registar_navio(estado, nome, dim, qtd, op, prio, tipo)


def obter_fila_espera_ordenada(estado: dict[str, Any]) -> list[dict[str, Any]]:
    """Devolve os navios em fila ordenados por prioridade, tempo de espera e chegada."""
    em_fila = [n for n in estado["navios"] if n["estado"] == "Em Fila"]
    return sorted(
        em_fila,
        key=lambda n: (
            -ORDEM_PRIORIDADES[n["prioridade"]],
            -n["ciclos_espera"],
            n["ciclo_chegada"],
        ),
    )


def cais_compativel(cais: dict[str, Any], navio: dict[str, Any]) -> bool:
    """Verifica se o cais suporta a dimensão do navio."""
    return ORDEM_DIMENSOES[cais["capacidade_dimensao"]] >= ORDEM_DIMENSOES[navio["dimensao"]]


def atracar_navio(
    estado: dict[str, Any], navio_id: str, cais_id: str
) -> tuple[bool, str]:
    """Atraca manualmente ou automaticamente um navio num cais livre compatível."""
    navio = obter_navio(estado, navio_id)
    cais = obter_cais(estado, cais_id)
    if navio is None or cais is None:
        return False, "Navio ou cais inexistente."
    if navio["estado"] != "Em Fila":
        return False, f"O navio {navio_id} não está em fila de espera."
    if cais["ocupado"]:
        return False, f"O {cais['nome']} já está ocupado por outro navio."
    if not cais_compativel(cais, navio):
        return (
            False,
            f"O {cais['nome']} ({cais['capacidade_dimensao']}) não comporta navios de dimensão {navio['dimensao']}.",
        )

    cais["ocupado"] = True
    cais["navio_id"] = navio["id"]
    navio["estado"] = "Atracado"
    navio["cais_id"] = cais["id"]

    estado["financas"]["receitas"] = round(
        estado["financas"]["receitas"] + RECEITA_ATRACACAO_BASE, 2
    )
    estado["estatisticas"]["soma_espera_atracados"] += navio["ciclos_espera"]
    estado["estatisticas"]["total_atracados"] += 1

    msg = f"Ciclo {estado['ciclo']}: {navio['id']} ({navio['nome']}) atracou no {cais['nome']}."
    estado["historico"].append(msg)
    return True, msg


def atribuir_cais_otimizado(estado: dict[str, Any]) -> list[str]:
    """
    Algoritmo de otimização: percorre a fila ordenada por prioridade e atribui a cada
    navio o menor cais livre compatível (best-fit), reservando cais grandes para navios grandes.
    """
    mensagens: list[str] = []
    fila = obter_fila_espera_ordenada(estado)

    for navio in fila:
        cais_livres_compativeis = [
            c for c in estado["cais"] if not c["ocupado"] and cais_compativel(c, navio)
        ]
        if not cais_livres_compativeis:
            continue
        # Escolhe o menor cais compatível (best-fit)
        melhor_cais = min(
            cais_livres_compativeis,
            key=lambda c: (ORDEM_DIMENSOES[c["capacidade_dimensao"]], -c["gruas"]),
        )
        ok, msg = atracar_navio(estado, navio["id"], melhor_cais["id"])
        if ok:
            mensagens.append(msg)
    return mensagens


def adicionar_contentor_patio(
    estado: dict[str, Any], tipo: str, origem: str = "Entrada Terrestre"
) -> tuple[bool, str, dict[str, Any] | None]:
    """Regista um contentor no inventário do pátio portuário."""
    if tipo not in TIPOS_CONTENTOR:
        return False, "Tipo de contentor inválido.", None

    cid = f"CNT-{estado['proximo_contentor_seq']:04d}"
    estado["proximo_contentor_seq"] += 1
    setor = f"Setor-{((estado['proximo_contentor_seq'] - 2) % 4) + 1}"

    contentor = {
        "id": cid,
        "tipo": tipo,
        "localizacao": setor,
        "estado": "Em Armazém",
        "origem": origem,
    }
    estado["contentores"].append(contentor)
    msg = f"Contentor {cid} ({tipo}) armazenado em {setor} ({origem})."
    return True, msg, contentor


def expedir_contentor(estado: dict[str, Any], contentor_id: str) -> tuple[bool, str]:
    """Regista a saída/expedição de um contentor do pátio e gera receita logística."""
    for idx, c in enumerate(estado["contentores"]):
        if c["id"] == contentor_id:
            tipo = c["tipo"]
            estado["contentores"].pop(idx)
            taxa_saida = round(TIPOS_CONTENTOR[tipo]["receita"] * 0.4, 2)
            estado["financas"]["receitas"] = round(
                estado["financas"]["receitas"] + taxa_saida, 2
            )
            msg = f"Ciclo {estado['ciclo']}: Contentor {contentor_id} ({tipo}) expedido (+{taxa_saida:.2f} €)."
            estado["historico"].append(msg)
            return True, msg
    return False, "Contentor não encontrado no armazém."


def libertar_cais(estado: dict[str, Any], cais_id: str) -> tuple[bool, str]:
    """Liberta manualmente um cais caso o navio já tenha concluído ou precise de sair."""
    cais = obter_cais(estado, cais_id)
    if cais is None:
        return False, "Cais inválido."
    if not cais["ocupado"] or cais["navio_id"] is None:
        return False, "Este cais já está livre."

    navio = obter_navio(estado, cais["navio_id"])
    if navio is not None and navio["contentores_restantes"] > 0:
        return False, "O navio ainda tem operações pendentes antes de desatracar."

    if navio is not None:
        navio["estado"] = "Concluído"
        navio["cais_id"] = None
    cais["ocupado"] = False
    cais["navio_id"] = None
    msg = f"Ciclo {estado['ciclo']}: {cais['nome']} libertado."
    estado["historico"].append(msg)
    return True, msg


def executar_ciclo_portuario(estado: dict[str, Any]) -> list[str]:
    """
    Avança um ciclo operacional do porto:
    - Movimenta contentores nos cais ocupados
    - Calcula receitas e custos operacionais/armazenamento/espera
    - Liberta cais de navios concluídos
    - Atualiza tempo de espera dos navios em fila
    """
    eventos: list[str] = []
    receita_ciclo = 0.0
    custo_ciclo = 0.0
    movimentos_ciclo = 0

    for cais in estado["cais"]:
        if not cais["ocupado"] or cais["navio_id"] is None:
            continue

        cais["ciclos_ocupado"] += 1
        custo_ciclo += CUSTO_OPERACIONAL_CAIS_CICLO
        navio = obter_navio(estado, cais["navio_id"])
        if navio is None:
            continue

        capacidade_op = cais["gruas"] * MOVIMENTACAO_POR_GRUA
        if navio["operacao"] == "Descarga":
            movidos = min(capacidade_op, navio["contentores_restantes"])
            for _ in range(movidos):
                adicionar_contentor_patio(estado, navio["tipo_carga"], origem=navio["id"])
        else:
            # Carga: tenta usar contentores do armazém, ou carga direta do terminal
            movidos = min(capacidade_op, navio["contentores_restantes"])
            removidos = 0
            for idx in range(len(estado["contentores"]) - 1, -1, -1):
                if removidos >= movidos:
                    break
                if estado["contentores"][idx]["tipo"] == navio["tipo_carga"]:
                    estado["contentores"].pop(idx)
                    removidos += 1

        navio["contentores_restantes"] -= movidos
        movimentos_ciclo += movidos
        receita_ciclo += movidos * TIPOS_CONTENTOR[navio["tipo_carga"]]["receita"]

        if navio["contentores_restantes"] <= 0:
            navio["estado"] = "Concluído"
            navio["cais_id"] = None
            cais["ocupado"] = False
            cais["navio_id"] = None
            estado["financas"]["navios_concluidos"] += 1
            eventos.append(
                f"{navio['id']} ({navio['nome']}) concluiu operações no {cais['nome']} e desatracou."
            )

    # Custo de armazenamento de contentores no pátio
    for cnt in estado["contentores"]:
        custo_ciclo += TIPOS_CONTENTOR[cnt["tipo"]]["custo_armazem"]

    # Penalização e contagem de espera na fila
    em_fila = [n for n in estado["navios"] if n["estado"] == "Em Fila"]
    for navio in em_fila:
        navio["ciclos_espera"] += 1
        custo_ciclo += CUSTO_ESPERA_NAVIO_CICLO

    estado["financas"]["receitas"] = round(estado["financas"]["receitas"] + receita_ciclo, 2)
    estado["financas"]["custos"] = round(estado["financas"]["custos"] + custo_ciclo, 2)
    estado["financas"]["contentores_movimentados"] += movimentos_ciclo

    resumo = (
        f"Ciclo {estado['ciclo']}: {movimentos_ciclo} contentores movidos | "
        f"+{receita_ciclo:.2f} € receita | -{custo_ciclo:.2f} € custos."
    )
    eventos.insert(0, resumo)
    estado["ciclo"] += 1

    for ev in eventos:
        estado["historico"].append(ev)
    if len(estado["historico"]) > 90:
        estado["historico"] = estado["historico"][-90:]

    return eventos


def obter_indicadores(estado: dict[str, Any]) -> dict[str, Any]:
    """Calcula métricas operacionais, eficiência e lucro do porto."""
    fin = estado["financas"]
    lucro = round(fin["receitas"] - fin["custos"], 2)
    cais_ocupados = sum(1 for c in estado["cais"] if c["ocupado"])
    total_cais = len(estado["cais"])
    ocupacao_atual = round((cais_ocupados / total_cais) * 100, 1) if total_cais else 0.0

    ciclos_decorridos = max(1, estado["ciclo"] - 1)
    soma_ciclos_cais = sum(c["ciclos_ocupado"] for c in estado["cais"])
    utilizacao_media = round(
        min(100.0, (soma_ciclos_cais / (total_cais * ciclos_decorridos)) * 100), 1
    )

    atracados = estado["estatisticas"]["total_atracados"]
    tempo_medio_espera = (
        round(estado["estatisticas"]["soma_espera_atracados"] / atracados, 2)
        if atracados > 0
        else 0.0
    )

    return {
        "ciclo": estado["ciclo"],
        "lucro": lucro,
        "receitas": fin["receitas"],
        "custos": fin["custos"],
        "contentores_movimentados": fin["contentores_movimentados"],
        "contentores_armazem": len(estado["contentores"]),
        "navios_em_fila": len(obter_fila_espera_ordenada(estado)),
        "navios_concluidos": fin["navios_concluidos"],
        "cais_ocupados": cais_ocupados,
        "total_cais": total_cais,
        "ocupacao_atual": ocupacao_atual,
        "utilizacao_media": utilizacao_media,
        "tempo_medio_espera": tempo_medio_espera,
    }
