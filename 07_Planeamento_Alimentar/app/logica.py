"""Lógica do planeamento alimentar semanal e cálculos nutricionais."""

from __future__ import annotations

from typing import Any

from app.dados import ALIMENTOS_PREDEFINIDOS, DIAS_SEMANA, REFEICOES


def criar_plano_vazio() -> dict[str, Any]:
    """Cria uma estrutura vazia para os 7 dias da semana e 5 refeições por dia."""
    dias = {
        dia: {ref: [] for ref in REFEICOES}
        for dia in DIAS_SEMANA
    }
    return {"dias": dias}


def obter_alimento_por_id(alimento_id: int) -> dict[str, Any] | None:
    """Procura um alimento na base de dados pelo seu identificador."""
    for item in ALIMENTOS_PREDEFINIDOS:
        if item["id"] == alimento_id:
            return item
    return None


def pesquisar_alimentos(termo: str = "") -> list[dict[str, Any]]:
    """Devolve alimentos que contenham o termo pesquisado no nome."""
    filtro = termo.strip().lower()
    if not filtro:
        return list(ALIMENTOS_PREDEFINIDOS)
    return [a for a in ALIMENTOS_PREDEFINIDOS if filtro in a["nome"].lower()]


def calcular_nutrientes_porcao(alimento: dict[str, Any], gramas: float) -> dict[str, float]:
    """Calcula calorias, proteínas, hidratos e gorduras para uma quantidade em gramas."""
    fator = gramas / 100.0
    return {
        "calorias": round(alimento["calorias"] * fator, 1),
        "proteinas": round(alimento["proteinas"] * fator, 1),
        "hidratos": round(alimento["hidratos"] * fator, 1),
        "gorduras": round(alimento["gorduras"] * fator, 1),
    }


def _validar_dia_refeicao(dia: str, refeicao: str) -> tuple[bool, str]:
    if dia not in DIAS_SEMANA:
        return False, "Dia da semana inválido."
    if refeicao not in REFEICOES:
        return False, "Refeição inválida."
    return True, ""


def adicionar_alimento_refeicao(
    plano: dict[str, Any],
    dia: str,
    refeicao: str,
    alimento_id: int,
    gramas: float,
) -> tuple[bool, str]:
    """Adiciona um alimento com quantidade em gramas a uma refeição."""
    ok_dr, msg_dr = _validar_dia_refeicao(dia, refeicao)
    if not ok_dr:
        return False, msg_dr
    if not isinstance(gramas, (int, float)) or gramas <= 0 or gramas > 5000:
        return False, "A quantidade em gramas deve ser superior a 0 e até 5000g."

    alimento = obter_alimento_por_id(alimento_id)
    if alimento is None:
        return False, "Alimento não encontrado na base de dados."

    lista = plano["dias"][dia][refeicao]
    # Se já existir o mesmo alimento na refeição, acumula as gramas
    for entrada in lista:
        if entrada["alimento_id"] == alimento_id:
            entrada["gramas"] = round(entrada["gramas"] + float(gramas), 1)
            return True, (
                f"Atualizado {alimento['nome']} em {dia} ({refeicao}) para {entrada['gramas']}g."
            )

    lista.append(
        {
            "alimento_id": alimento_id,
            "nome": alimento["nome"],
            "gramas": round(float(gramas), 1),
        }
    )
    return True, f"Adicionado {gramas}g de {alimento['nome']} a {dia} ({refeicao})."


def remover_alimento_refeicao(
    plano: dict[str, Any], dia: str, refeicao: str, indice: int
) -> tuple[bool, str]:
    """Remove um alimento pelo índice na refeição especificada."""
    ok_dr, msg_dr = _validar_dia_refeicao(dia, refeicao)
    if not ok_dr:
        return False, msg_dr

    lista = plano["dias"][dia][refeicao]
    if not (0 <= indice < len(lista)):
        return False, "Índice de alimento inválido."

    removido = lista.pop(indice)
    return True, f"Removido {removido['nome']} de {dia} ({refeicao})."


def alterar_quantidade_alimento(
    plano: dict[str, Any], dia: str, refeicao: str, indice: int, novas_gramas: float
) -> tuple[bool, str]:
    """Altera a quantidade em gramas de um alimento existente na refeição."""
    ok_dr, msg_dr = _validar_dia_refeicao(dia, refeicao)
    if not ok_dr:
        return False, msg_dr
    if not isinstance(novas_gramas, (int, float)) or novas_gramas <= 0 or novas_gramas > 5000:
        return False, "A quantidade deve ser positiva (entre 0.1g e 5000g)."

    lista = plano["dias"][dia][refeicao]
    if not (0 <= indice < len(lista)):
        return False, "Índice de alimento inválido."

    lista[indice]["gramas"] = round(float(novas_gramas), 1)
    return True, f"Quantidade de {lista[indice]['nome']} alterada para {lista[indice]['gramas']}g."


def substituir_refeicao(
    plano: dict[str, Any],
    dia: str,
    refeicao: str,
    novos_itens: list[tuple[int, float]],
) -> tuple[bool, str]:
    """Substitui completamente os alimentos de uma refeição por uma nova lista `(alimento_id, gramas)`."""
    ok_dr, msg_dr = _validar_dia_refeicao(dia, refeicao)
    if not ok_dr:
        return False, msg_dr

    # Valida primeiro todos os novos itens antes de modificar o plano
    itens_validados: list[dict[str, Any]] = []
    for alimento_id, gramas in novos_itens:
        alimento = obter_alimento_por_id(alimento_id)
        if alimento is None:
            return False, f"Alimento ID {alimento_id} inexistente."
        if not isinstance(gramas, (int, float)) or gramas <= 0 or gramas > 5000:
            return False, f"Quantidade inválida ({gramas}g) para {alimento['nome']}."
        itens_validados.append(
            {
                "alimento_id": alimento_id,
                "nome": alimento["nome"],
                "gramas": round(float(gramas), 1),
            }
        )

    plano["dias"][dia][refeicao] = itens_validados
    return True, f"Refeição {refeicao} de {dia} substituída com {len(itens_validados)} alimento(s)."


def calcular_totais_refeicao(
    plano: dict[str, Any], dia: str, refeicao: str
) -> dict[str, float]:
    """Calcula os totais nutricionais de uma refeição."""
    totais = {"calorias": 0.0, "proteinas": 0.0, "hidratos": 0.0, "gorduras": 0.0}
    for entrada in plano["dias"].get(dia, {}).get(refeicao, []):
        alimento = obter_alimento_por_id(entrada["alimento_id"])
        if alimento is None:
            continue
        nut = calcular_nutrientes_porcao(alimento, entrada["gramas"])
        for chave in totais:
            totais[chave] = round(totais[chave] + nut[chave], 1)
    return totais


def calcular_totais_dia(plano: dict[str, Any], dia: str) -> dict[str, float]:
    """Calcula os totais nutricionais de um dia inteiro."""
    totais = {"calorias": 0.0, "proteinas": 0.0, "hidratos": 0.0, "gorduras": 0.0}
    for refeicao in REFEICOES:
        t_ref = calcular_totais_refeicao(plano, dia, refeicao)
        for chave in totais:
            totais[chave] = round(totais[chave] + t_ref[chave], 1)
    return totais


def calcular_totais_semana(plano: dict[str, Any]) -> dict[str, Any]:
    """Calcula totais semanais, médias diárias e comparação por dia."""
    totais = {"calorias": 0.0, "proteinas": 0.0, "hidratos": 0.0, "gorduras": 0.0}
    por_dia: dict[str, dict[str, float]] = {}

    for dia in DIAS_SEMANA:
        t_dia = calcular_totais_dia(plano, dia)
        por_dia[dia] = t_dia
        for chave in totais:
            totais[chave] = round(totais[chave] + t_dia[chave], 1)

    medias = {chave: round(totais[chave] / len(DIAS_SEMANA), 1) for chave in totais}
    return {
        "totais": totais,
        "medias_diarias": medias,
        "por_dia": por_dia,
    }


def identificar_refeicoes_nao_planeadas(plano: dict[str, Any]) -> list[tuple[str, str]]:
    """Devolve uma lista de pares `(dia, refeicao)` que ainda não têm alimentos."""
    vazias: list[tuple[str, str]] = []
    for dia in DIAS_SEMANA:
        for ref in REFEICOES:
            if len(plano["dias"][dia][ref]) == 0:
                vazias.append((dia, ref))
    return vazias
