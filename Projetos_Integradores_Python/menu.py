"""Menu principal opcional para iniciar qualquer um dos sete projetos independentes."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

RAIZ = Path(__file__).resolve().parent

PROJETOS = [
    ("1", "01_Empire", "Empire — Estratégia e Conquista Territorial (Tkinter)"),
    ("2", "02_Colonia_Marciana", "Colónia Marciana — Simulador em Marte (Tkinter)"),
    ("3", "03_Dungeon_Quest", "Dungeon Quest — Aventura RPG (Tkinter)"),
    ("4", "04_Parque_Estacionamento", "Parque de Estacionamento — Parking Manager (Tkinter)"),
    ("5", "05_Porto_Maritimo", "Porto Marítimo — Port Manager (Tkinter)"),
    ("6", "06_Quiz_Romeu_e_Julieta", "Quiz Adaptativo — Romeu e Julieta (Tkinter)"),
    ("7", "07_Planeamento_Alimentar", "Planeamento Alimentar Semanal (Consola)"),
]


def executar_projeto(pasta: str) -> None:
    """Inicia o ficheiro main.py do projeto escolhido num processo independente."""
    diretorio = RAIZ / pasta
    script = diretorio / "main.py"
    if not script.exists():
        print(f"\n  [Erro] Ficheiro não encontrado: {script}")
        return

    print(f"\n  A iniciar '{pasta}'...\n")
    try:
        subprocess.run([sys.executable, str(script)], cwd=str(diretorio), check=False)
    except OSError as erro:
        print(f"\n  [Erro] Não foi possível iniciar o projeto: {erro}")


def executar_menu() -> None:
    """Apresenta o menu de seleção dos sete projetos integradores."""
    try:
        while True:
            print("\n" + "=" * 72)
            print("  PROJETOS INTEGRADORES EM PYTHON — APLICACÕES INFORMÁTICAS B (12.º)")
            print("=" * 72)
            for codigo, _pasta, descricao in PROJETOS:
                print(f"  {codigo}. {descricao}")
            print("  T. Executar testes automatizados de todos os projetos")
            print("  0. Sair")

            escolha = input("\n  Seleciona uma opção: ").strip().upper()
            if escolha == "0":
                print("\n  Menu encerrado.\n")
                break
            if escolha == "T":
                subprocess.run([sys.executable, str(RAIZ / "testar_todos.py")], cwd=str(RAIZ), check=False)
                continue

            correspondencia = next((p for p in PROJETOS if p[0] == escolha), None)
            if correspondencia is None:
                print("  [Aviso] Opção inválida. Escolhe entre 1-7, T ou 0.")
                continue

            executar_projeto(correspondencia[1])
    except (EOFError, KeyboardInterrupt):
        print("\n\n  Menu terminado pelo utilizador.")


if __name__ == "__main__":
    executar_menu()
