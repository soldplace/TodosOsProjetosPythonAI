"""Executa os testes automatizados (unittest) de todos os sete projetos de forma isolada."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

RAIZ = Path(__file__).resolve().parent

PASTAS_PROJETOS = [
    "01_Empire",
    "02_Colonia_Marciana",
    "03_Dungeon_Quest",
    "04_Parque_Estacionamento",
    "05_Porto_Maritimo",
    "06_Quiz_Romeu_e_Julieta",
    "07_Planeamento_Alimentar",
]


def executar_todos_os_testes() -> int:
    """Corre os testes de cada projeto num subprocesso próprio e apresenta o resumo."""
    print("=" * 72)
    print("  EXECUÇÃO DOS TESTES — TODOS OS PROJETOS INTEGRADORES")
    print("=" * 72)

    resultados: list[tuple[str, bool]] = []

    for pasta in PASTAS_PROJETOS:
        caminho_projeto = RAIZ / pasta
        print(f"\n>>> A testar {pasta}...")
        if not (caminho_projeto / "tests").exists():
            print(f"  [FALHA] Pasta de testes em falta em {pasta}")
            resultados.append((pasta, False))
            continue

        processo = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
            cwd=str(caminho_projeto),
            capture_output=True,
            text=True,
            check=False,
        )
        if processo.stdout:
            print(processo.stdout.strip())
        if processo.stderr:
            print(processo.stderr.strip())

        sucesso = processo.returncode == 0
        resultados.append((pasta, sucesso))

    print("\n" + "=" * 72)
    print("  RESUMO FINAL DOS TESTES")
    print("=" * 72)
    todos_ok = True
    for pasta, ok in resultados:
        estado = "PASSOU" if ok else "FALHOU"
        if not ok:
            todos_ok = False
        print(f"  {pasta:<30} [{estado}]")

    print("=" * 72)
    return 0 if todos_ok else 1


if __name__ == "__main__":
    sys.exit(executar_todos_os_testes())
