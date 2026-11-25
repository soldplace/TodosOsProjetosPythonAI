"""Persistência em JSON para o jogo Empire."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CAMINHO_BASE = Path(__file__).resolve().parent.parent
CAMINHO_GRAVACAO_PADRAO = CAMINHO_BASE / "data" / "empire_save.json"


def guardar_partida(
    estado: dict[str, Any], caminho: Path | None = None
) -> tuple[bool, str]:
    """Guarda o estado da partida num ficheiro JSON."""
    destino = caminho or CAMINHO_GRAVACAO_PADRAO
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as ficheiro:
            json.dump(estado, ficheiro, ensure_ascii=False, indent=2)
        return True, f"Partida guardada com sucesso em {destino.name}."
    except OSError as erro:
        return False, f"Erro ao guardar partida: {erro}"


def carregar_partida(
    caminho: Path | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """Carrega uma partida guardada de um ficheiro JSON com validação básica."""
    origem = caminho or CAMINHO_GRAVACAO_PADRAO
    if not origem.exists():
        return None, "Não existe nenhuma partida guardada."
    try:
        with origem.open("r", encoding="utf-8") as ficheiro:
            dados = json.load(ficheiro)
    except (OSError, json.JSONDecodeError) as erro:
        return None, f"Ficheiro de gravação inválido ou corrompido: {erro}"

    chaves_obrigatorias = {"turno", "estado_jogo", "recursos", "territorios", "melhorias", "tecnologias"}
    if not isinstance(dados, dict) or not chaves_obrigatorias.issubset(dados.keys()):
        return None, "Estrutura do ficheiro de gravação incompatível."

    return dados, "Partida carregada com sucesso."
