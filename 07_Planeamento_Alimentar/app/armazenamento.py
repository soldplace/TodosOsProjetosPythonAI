"""Persistência em JSON do Plano Alimentar Semanal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.dados import DIAS_SEMANA, REFEICOES

CAMINHO_BASE = Path(__file__).resolve().parent.parent
CAMINHO_PLANO_PADRAO = CAMINHO_BASE / "data" / "plano_semanal.json"


def guardar_plano(
    plano: dict[str, Any], caminho: Path | None = None
) -> tuple[bool, str]:
    """Guarda o plano semanal num ficheiro JSON."""
    destino = caminho or CAMINHO_PLANO_PADRAO
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as ficheiro:
            json.dump(plano, ficheiro, ensure_ascii=False, indent=2)
        return True, f"Plano semanal guardado com sucesso em {destino.name}."
    except OSError as erro:
        return False, f"Erro ao guardar plano: {erro}"


def carregar_plano(
    caminho: Path | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """Carrega um plano semanal guardado e valida a estrutura de dias e refeições."""
    origem = caminho or CAMINHO_PLANO_PADRAO
    if not origem.exists():
        return None, "Não existe nenhum plano semanal guardado."
    try:
        with origem.open("r", encoding="utf-8") as ficheiro:
            dados = json.load(ficheiro)
    except (OSError, json.JSONDecodeError) as erro:
        return None, f"Ficheiro de plano inválido: {erro}"

    if not isinstance(dados, dict) or "dias" not in dados or not isinstance(dados["dias"], dict):
        return None, "Estrutura do ficheiro incompatível."

    # Garante que todos os dias e refeições existem
    for dia in DIAS_SEMANA:
        if dia not in dados["dias"] or not isinstance(dados["dias"][dia], dict):
            return None, f"Falta o dia '{dia}' no ficheiro guardado."
        for ref in REFEICOES:
            if ref not in dados["dias"][dia] or not isinstance(dados["dias"][dia][ref], list):
                dados["dias"][dia][ref] = []

    return dados, "Plano semanal carregado com sucesso."
