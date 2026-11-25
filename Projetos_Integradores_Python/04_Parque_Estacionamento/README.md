# Parking Manager — Simulador de Parque de Estacionamento

## Objetivo
Aplicação em Python com interface Tkinter para simular a gestão operacional e financeira de um parque de estacionamento, desenvolvida para Aplicações Informáticas B (12.º ano).

## Funcionalidades
- **Planta visual vista de cima** em `tkinter.Canvas` com lugares numerados, veículos coloridos e estado livre/ocupado.
- **Validação rigorosa de matrículas** portuguesas (`AA-00-AA`, `00-AA-00`, `00-00-AA`, `AA-00-00`), impedindo duplicações e lotação excessiva.
- **Emissão automática de bilhetes** (`BIL-0001`, etc.) e atribuição do primeiro lugar livre.
- **Saída com pré-visualização**: pesquisa por matrícula ou bilhete, cálculo de tempo de permanência e valor a pagar em euros (€).
- **Simulação temporal**: relógio interno independente com avanços de `+15 min`, `+30 min`, `+1 hora` e `+3 horas`.
- **Tarifário e capacidade configuráveis** (arredondamento por excesso à hora iniciada, mínimo 1 hora).
- **Estatísticas e histórico**: taxa de ocupação, receita total, entradas/saídas e tempo médio de permanência.
- **Persistência em JSON**: guardar e carregar em `data/parque_save.json`.

## Tecnologias Utilizadas
- Python 3.10+
- Biblioteca padrão: `tkinter`, `tkinter.ttk`, `datetime`, `math`, `re`, `random`, `json`, `pathlib`, `unittest`

## Estrutura dos Ficheiros
```
04_Parque_Estacionamento/
├── main.py
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── dados.py
│   ├── logica.py
│   ├── armazenamento.py
│   └── interface.py
├── data/
│   └── .gitkeep
├── docs/
│   ├── algoritmos.md
│   └── apresentacao.md
└── tests/
    ├── __init__.py
    └── test_logica.py
```

## Como Executar
```bash
python3 main.py
```

## Como Utilizar
1. Introduz uma matrícula válida (ex.: `AB-12-CD`) e clica em **Registar Entrada**.
2. Usa os botões no topo (`+15 min`, `+1 hora`, etc.) para simular a passagem do tempo.
3. Seleciona um veículo na tabela ou na planta e clica em **Processar Saída (€)** para ver o valor a pagar e confirmar.

## Como Executar os Testes
```bash
python3 -m unittest discover -s tests -v
```
