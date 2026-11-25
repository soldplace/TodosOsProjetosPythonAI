"""Persistência em JSON das classificações e histórico do Quiz Romeu e Julieta."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

CAMINHO_BASE = Path(__file__).resolve().parent.parent
CAMINHO_CLASSIFICACOES = CAMINHO_BASE / "data" / "classificacoes.json"


def carregar_classificacoes(caminho: Path | None = None) -> list[dict[str, Any]]:
    """Carrega a tabela de classificações ordenada por pontuação decrescente."""
    origem = caminho or CAMINHO_CLASSIFICACOES
    if not origem.exists():
        return []
    try:
        with origem.open("r", encoding="utf-8") as ficheiro:
            dados = json.load(ficheiro)
        if not isinstance(dados, list):
            return []
        return sorted(dados, key=lambda r: (-r.get("pontuacao", 0), -r.get("acertos", 0)))
    except (OSError, json.JSONDecodeError):
        return []


def guardar_resultado_sessao(
    estado: dict[str, Any], caminho: Path | None = None
) -> tuple[bool, list[dict[str, Any]], str]:
    """Adiciona o resultado da sessão atual à tabela de classificações e guarda em JSON."""
    destino = caminho or CAMINHO_CLASSIFICACOES
    lista = carregar_classificacoes(destino)

    novo_registo = {
        "jogador": estado["jogador"],
        "pontuacao": estado["pontuacao"],
        "acertos": estado["acertos"],
        "total_perguntas": estado["total_perguntas"],
        "melhor_sequencia": estado["melhor_sequencia"],
        "dificuldade_final": estado["dificuldade_atual"],
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    lista.append(novo_registo)
    lista_ordenada = sorted(
        lista, key=lambda r: (-r.get("pontuacao", 0), -r.get("acertos", 0))
    )[:50]

    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as ficheiro:
            json.dump(lista_ordenada, ficheiro, ensure_ascii=False, indent=2)
        return True, lista_ordenada, "Resultado guardado nas classificações."
    except OSError as erro:
        return False, lista_ordenada, f"Erro ao guardar classificação: {erro}"
