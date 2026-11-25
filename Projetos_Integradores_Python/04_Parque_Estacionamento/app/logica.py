"""Lógica de gestão, tarifação, validação e simulação temporal do parque."""

from __future__ import annotations

from datetime import datetime, timedelta
import math
import random
import re
from typing import Any

from app.dados import (
    CAPACIDADE_MAXIMA,
    CAPACIDADE_MINIMA,
    CAPACIDADE_PADRAO,
    CORES_VEICULOS,
    HORA_INICIAL_SIMULACAO,
    TARIFA_HORA_PADRAO,
)

# Aceita os formatos de matrícula portuguesa (ex.: AA-00-AA, 00-AA-00, 00-00-AA, AA-00-00)
PADRAO_MATRICULA = re.compile(
    r"^(?:[A-Z]{2}-\d{2}-[A-Z]{2}|\d{2}-[A-Z]{2}-\d{2}|\d{2}-\d{2}-[A-Z]{2}|[A-Z]{2}-\d{2}-\d{2})$"
)


def criar_novo_parque(
    capacidade: int = CAPACIDADE_PADRAO, tarifa_hora: float = TARIFA_HORA_PADRAO
) -> dict[str, Any]:
    """Cria o estado inicial de um parque de estacionamento."""
    if not (CAPACIDADE_MINIMA <= capacidade <= CAPACIDADE_MAXIMA):
        raise ValueError(
            f"A capacidade deve estar entre {CAPACIDADE_MINIMA} e {CAPACIDADE_MAXIMA} lugares."
        )
    if tarifa_hora <= 0:
        raise ValueError("A tarifa por hora deve ser positiva.")

    lugares = [
        {
            "numero": i + 1,
            "codigo": f"L{i + 1:02d}",
            "ocupado": False,
            "veiculo": None,
        }
        for i in range(capacidade)
    ]

    return {
        "capacidade": capacidade,
        "tarifa_hora": round(float(tarifa_hora), 2),
        "relogio": HORA_INICIAL_SIMULACAO,
        "proximo_bilhete": 1,
        "receita_total": 0.0,
        "total_entradas": 0,
        "total_saidas": 0,
        "soma_minutos_permanencia": 0,
        "lugares": lugares,
        "historico": [],
    }


def normalizar_e_validar_matricula(matricula: str) -> tuple[bool, str]:
    """Normaliza para maiúsculas e valida a matrícula segundo formatos portugueses."""
    limpa = matricula.strip().upper().replace(" ", "-")
    if not limpa:
        return False, "A matrícula não pode estar vazia."
    if not PADRAO_MATRICULA.match(limpa):
        return (
            False,
            "Formato de matrícula inválido. Usa formatos como AA-00-AA, 00-AA-00 ou 00-00-AA.",
        )
    return True, limpa


def obter_hora_atual(estado: dict[str, Any]) -> datetime:
    """Converte a string ISO do relógio da simulação num objeto datetime."""
    return datetime.fromisoformat(estado["relogio"])


def avancar_relogio(estado: dict[str, Any], minutos: int) -> tuple[bool, str]:
    """Avança o relógio interno da simulação em `minutos`."""
    if minutos <= 0:
        return False, "Os minutos a avançar têm de ser positivos."
    atual = obter_hora_atual(estado)
    nova_hora = atual + timedelta(minutes=minutos)
    estado["relogio"] = nova_hora.isoformat(timespec="seconds")
    return True, f"Relógio avançado para {nova_hora.strftime('%d/%m/%Y %H:%M')}."


def configurar_tarifa(estado: dict[str, Any], nova_tarifa: float) -> tuple[bool, str]:
    """Atualiza o preço por hora do parque."""
    if nova_tarifa <= 0:
        return False, "O preço por hora tem de ser superior a 0,00 €."
    estado["tarifa_hora"] = round(float(nova_tarifa), 2)
    return True, f"Tarifa atualizada para {estado['tarifa_hora']:.2f} €/hora."


def reconfigurar_capacidade(estado: dict[str, Any], nova_capacidade: int) -> tuple[bool, str]:
    """Altera a capacidade do parque se não houver veículos nos lugares a remover."""
    if not (CAPACIDADE_MINIMA <= nova_capacidade <= CAPACIDADE_MAXIMA):
        return (
            False,
            f"A capacidade deve situar-se entre {CAPACIDADE_MINIMA} e {CAPACIDADE_MAXIMA} lugares.",
        )

    atual = len(estado["lugares"])
    if nova_capacidade > atual:
        for i in range(atual, nova_capacidade):
            estado["lugares"].append(
                {
                    "numero": i + 1,
                    "codigo": f"L{i + 1:02d}",
                    "ocupado": False,
                    "veiculo": None,
                }
            )
    elif nova_capacidade < atual:
        for lugar in estado["lugares"][nova_capacidade:]:
            if lugar["ocupado"]:
                return (
                    False,
                    f"Não é possível reduzir para {nova_capacidade} lugares porque {lugar['codigo']} está ocupado.",
                )
        estado["lugares"] = estado["lugares"][:nova_capacidade]

    estado["capacidade"] = nova_capacidade
    return True, f"Capacidade do parque ajustada para {nova_capacidade} lugares."


def encontrar_veiculo(
    estado: dict[str, Any], termo: str
) -> tuple[dict[str, Any] | None, str]:
    """Procura um veículo estacionado por matrícula ou código de bilhete."""
    consulta = termo.strip().upper()
    if not consulta:
        return None, "Indica uma matrícula ou número de bilhete."

    for lugar in estado["lugares"]:
        if lugar["ocupado"] and lugar["veiculo"] is not None:
            v = lugar["veiculo"]
            if v["matricula"] == consulta or v["bilhete"] == consulta:
                return lugar, ""
    return None, f"Nenhum veículo encontrado com matrícula ou bilhete '{consulta}'."


def registar_entrada(
    estado: dict[str, Any], matricula: str, cor: str | None = None
) -> tuple[bool, str, dict[str, Any] | None]:
    """Regista a entrada de um veículo, atribui o primeiro lugar livre e emite bilhete."""
    valida, resultado = normalizar_e_validar_matricula(matricula)
    if not valida:
        return False, resultado, None

    matricula_norm = resultado
    existente, _ = encontrar_veiculo(estado, matricula_norm)
    if existente is not None:
        return (
            False,
            f"O veículo {matricula_norm} já se encontra estacionado no lugar {existente['codigo']}.",
            None,
        )

    lugar_livre = next((l for l in estado["lugares"] if not l["ocupado"]), None)
    if lugar_livre is None:
        return False, "Parque completo! Não existem lugares livres.", None

    bilhete = f"BIL-{estado['proximo_bilhete']:04d}"
    estado["proximo_bilhete"] += 1

    cor_escolhida = cor if cor else random.choice(CORES_VEICULOS)
    veiculo = {
        "matricula": matricula_norm,
        "bilhete": bilhete,
        "entrada": estado["relogio"],
        "cor": cor_escolhida,
    }

    lugar_livre["ocupado"] = True
    lugar_livre["veiculo"] = veiculo
    estado["total_entradas"] += 1

    hora_fmt = obter_hora_atual(estado).strftime("%d/%m %H:%M")
    evento = f"[{hora_fmt}] ENTRADA: {matricula_norm} -> {lugar_livre['codigo']} (Bilhete {bilhete})"
    estado["historico"].append(evento)
    return True, evento, veiculo


def calcular_custo_permanencia(
    entrada_iso: str, saida_dt: datetime, tarifa_hora: float
) -> dict[str, Any]:
    """
    Calcula tempo de permanência e valor a pagar.
    Regra de arredondamento: cobra por cada hora iniciada (arredondamento por excesso),
    com mínimo de 1 hora para permanências superiores a 0 minutos.
    """
    entrada_dt = datetime.fromisoformat(entrada_iso)
    segundos = max(0, int((saida_dt - entrada_dt).total_seconds()))
    minutos = segundos // 60
    horas_cobradas = 1 if minutos == 0 else math.ceil(minutos / 60)
    valor = round(horas_cobradas * tarifa_hora, 2)
    return {
        "minutos": minutos,
        "horas_cobradas": horas_cobradas,
        "valor": valor,
    }


def simular_saida(estado: dict[str, Any], termo: str) -> tuple[bool, str, dict[str, Any] | None]:
    """Calcula a pré-visualização da saída sem libertar o lugar ainda."""
    lugar, msg_erro = encontrar_veiculo(estado, termo)
    if lugar is None:
        return False, msg_erro, None

    v = lugar["veiculo"]
    calculo = calcular_custo_permanencia(
        v["entrada"], obter_hora_atual(estado), estado["tarifa_hora"]
    )
    resumo = {
        "lugar": lugar["codigo"],
        "matricula": v["matricula"],
        "bilhete": v["bilhete"],
        "entrada": v["entrada"],
        "minutos": calculo["minutos"],
        "horas_cobradas": calculo["horas_cobradas"],
        "valor": calculo["valor"],
    }
    return True, "", resumo


def registar_saida(estado: dict[str, Any], termo: str) -> tuple[bool, str, dict[str, Any] | None]:
    """Conclui a saída do veículo, atualiza receita/estatísticas e liberta o lugar."""
    lugar, msg_erro = encontrar_veiculo(estado, termo)
    if lugar is None:
        return False, msg_erro, None

    v = lugar["veiculo"]
    agora = obter_hora_atual(estado)
    calculo = calcular_custo_permanencia(v["entrada"], agora, estado["tarifa_hora"])

    lugar["ocupado"] = False
    lugar["veiculo"] = None

    estado["receita_total"] = round(estado["receita_total"] + calculo["valor"], 2)
    estado["total_saidas"] += 1
    estado["soma_minutos_permanencia"] += calculo["minutos"]

    hora_fmt = agora.strftime("%d/%m %H:%M")
    evento = (
        f"[{hora_fmt}] SAÍDA: {v['matricula']} ({lugar['codigo']}) | "
        f"{calculo['minutos']} min ({calculo['horas_cobradas']}h cobradas) | "
        f"Total: {calculo['valor']:.2f} €"
    )
    estado["historico"].append(evento)
    return True, evento, calculo


def obter_estatisticas(estado: dict[str, Any]) -> dict[str, Any]:
    """Devolve indicadores atuais do parque (ocupação, lugares livres, receita, média)."""
    ocupados = sum(1 for l in estado["lugares"] if l["ocupado"])
    cap = estado["capacidade"]
    livres = cap - ocupados
    taxa = round((ocupados / cap) * 100, 1) if cap > 0 else 0.0
    saidas = estado["total_saidas"]
    media_min = round(estado["soma_minutos_permanencia"] / saidas, 1) if saidas > 0 else 0.0

    return {
        "capacidade": cap,
        "ocupados": ocupados,
        "livres": livres,
        "taxa_ocupacao": taxa,
        "receita_total": estado["receita_total"],
        "total_entradas": estado["total_entradas"],
        "total_saidas": saidas,
        "tempo_medio_min": media_min,
    }
