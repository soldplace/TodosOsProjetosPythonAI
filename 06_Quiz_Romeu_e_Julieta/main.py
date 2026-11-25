"""Ponto de entrada independente do Quiz Adaptativo: Romeu e Julieta."""

from pathlib import Path
import sys

RAIZ_PROJETO = Path(__file__).resolve().parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app.interface import iniciar_interface


if __name__ == "__main__":
    iniciar_interface()
