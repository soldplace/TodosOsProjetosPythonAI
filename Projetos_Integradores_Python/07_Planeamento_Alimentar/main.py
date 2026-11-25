"""Ponto de entrada independente da aplicação de consola Planeamento Alimentar."""

from pathlib import Path
import sys

RAIZ_PROJETO = Path(__file__).resolve().parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app.interface import executar_consola


if __name__ == "__main__":
    executar_consola()
