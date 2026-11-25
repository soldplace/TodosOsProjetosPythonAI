"""Persistência em JSON para o jogo Dungeon Quest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CAMINHO_BASE = Path(__file__).resolve().parent.parent
CAMINHO_GRAVACAO_PADRAO = CAMINHO_BASE / "data" / "dungeon_save.json"


def guardar_aventura(
    estado: dict[str, Any], caminho: Path | None = None
) -> tuple[bool, str]:
    """Guarda o estado atual da aventura em ficheiro JSON."""
    destino = caminho or CAMINHO_GRAVACAO_PADRAO
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as ficheiro:
            json.dump(estado, ficheiro, ensure_ascii=False, indent=2)
        return True, f"Aventura guardada em {destino.name}."
    except OSError as erro:
        return False, f"Erro ao guardar aventura: {erro}"


def carregar_aventura(
    caminho: Path | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """Carrega uma aventura guardada de um ficheiro JSON."""
    origem = caminho or CAMINHO_GRAVACAO_PADRAO
    if not origem.exists():
        return None, "Não existe nenhuma aventura guardada."
    try:
        with origem.open("r", encoding="utf-8") as ficheiro:
            dados = json.load(ficheiro)
    except (OSError, json.JSONDecodeError) as erro:
        return None, f"Ficheiro de gravação inválido: {erro}"

    obrigatorias = {"estado_jogo", "posicao", "heroi", "salas", "em_combate"}
    if not isinstance(dados, dict) or not obrigatorias.issubset(dados.keys()):
        return None, "Estrutura de gravação incompatível."
    return dados, "Aventura carregada com sucesso."
