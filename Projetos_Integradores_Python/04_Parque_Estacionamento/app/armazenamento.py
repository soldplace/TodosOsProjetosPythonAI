"""Persistência em JSON do Simulador de Parque de Estacionamento."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CAMINHO_BASE = Path(__file__).resolve().parent.parent
CAMINHO_GRAVACAO_PADRAO = CAMINHO_BASE / "data" / "parque_save.json"


def guardar_parque(
    estado: dict[str, Any], caminho: Path | None = None
) -> tuple[bool, str]:
    """Guarda o estado do parque e o histórico num ficheiro JSON."""
    destino = caminho or CAMINHO_GRAVACAO_PADRAO
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as ficheiro:
            json.dump(estado, ficheiro, ensure_ascii=False, indent=2)
        return True, f"Estado do parque guardado em {destino.name}."
    except OSError as erro:
        return False, f"Erro ao guardar dados do parque: {erro}"


def carregar_parque(
    caminho: Path | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """Carrega o estado do parque a partir de um ficheiro JSON."""
    origem = caminho or CAMINHO_GRAVACAO_PADRAO
    if not origem.exists():
        return None, "Não existe nenhum ficheiro de parque guardado."
    try:
        with origem.open("r", encoding="utf-8") as ficheiro:
            dados = json.load(ficheiro)
    except (OSError, json.JSONDecodeError) as erro:
        return None, f"Ficheiro de gravação inválido: {erro}"

    obrigatorias = {"capacidade", "tarifa_hora", "relogio", "lugares", "historico"}
    if not isinstance(dados, dict) or not obrigatorias.issubset(dados.keys()):
        return None, "Estrutura do ficheiro incompatível."
    return dados, "Estado do parque carregado com sucesso."
