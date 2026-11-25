# Projetos Integradores em Python — Aplicações Informáticas B (12.º Ano)

Conjunto de sete aplicações independentes desenvolvidas em Python 3 (utilizando apenas a biblioteca padrão, `tkinter` / `tkinter.ttk` para interfaces gráficas e modo de consola para o planeamento alimentar), com separação modular entre lógica, dados, armazenamento, interface, documentação e testes automatizados.

## Lista dos Sete Projetos

| N.º | Pasta | Projeto | Tipo de Interface |
|-----|-------|---------|-------------------|
| 01 | `01_Empire/` | **Empire** — Jogo de Decisão e Estratégia sobre Conquista Territorial | Gráfica (Tkinter + Canvas) |
| 02 | `02_Colonia_Marciana/` | **Colónia Marciana** — Simulador de Gestão de uma Colónia em Marte | Gráfica (Tkinter + Canvas) |
| 03 | `03_Dungeon_Quest/` | **Dungeon Quest** — Aventura RPG em Masmorras | Gráfica (Tkinter + Canvas) |
| 04 | `04_Parque_Estacionamento/` | **Parking Manager** — Simulador de Parque de Estacionamento | Gráfica (Tkinter + Canvas) |
| 05 | `05_Porto_Maritimo/` | **Port Manager** — Simulador de um Porto Marítimo | Gráfica (Tkinter + Canvas) |
| 06 | `06_Quiz_Romeu_e_Julieta/` | **Quiz Adaptativo** — Romeu e Julieta (William Shakespeare) | Gráfica (Tkinter) |
| 07 | `07_Planeamento_Alimentar/` | **Planeamento Alimentar Semanal** | Consola |

## Estrutura Geral
```
Projetos_Integradores_Python/
├── README.md
├── menu.py
├── testar_todos.py
├── 01_Empire/
├── 02_Colonia_Marciana/
├── 03_Dungeon_Quest/
├── 04_Parque_Estacionamento/
├── 05_Porto_Maritimo/
├── 06_Quiz_Romeu_e_Julieta/
└── 07_Planeamento_Alimentar/
```

Cada pasta é completamente autónoma e inclui:
- `main.py` para execução independente;
- `app/` com `dados.py`, `logica.py`, `armazenamento.py` e `interface.py`;
- `data/` para ficheiros de gravação JSON;
- `docs/` com `algoritmos.md` (análise, pseudocódigo e fluxogramas Mermaid) e `apresentacao.md` (guia e perguntas de defesa);
- `tests/` com testes unitários em `unittest`.

## Como Executar

### 1. Através do Menu Principal
```bash
python3 menu.py
```

### 2. Diretamente por Projeto (Execução Independente)
Exemplo para o Projeto 01:
```bash
cd 01_Empire
python3 main.py
```

## Como Executar Todos os Testes
Na pasta `Projetos_Integradores_Python/`:
```bash
python3 testar_todos.py
```
