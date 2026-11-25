# Port Manager — Simulador de Porto Marítimo

## Objetivo
Aplicação em Python com Tkinter para simular e otimizar operações portuárias (navios, cais, contentores, filas de espera e gestão financeira em euros), desenvolvida no âmbito de Aplicações Informáticas B (12.º ano).

## Funcionalidades
- **Gestão de navios**: registo manual ou aleatório com dimensão (`Pequeno`, `Médio`, `Grande`), operação (`Descarga`/`Carga`), tipo de carga e prioridade (`Normal`, `Alta`, `Urgente`).
- **Gestão de 4 cais**: capacidades distintas, impedimento de ocupação simultânea e verificação de compatibilidade de dimensão.
- **Otimização de atracação**: algoritmo *best-fit* com prioridade que atribui o menor cais compatível livre a cada navio.
- **Gestão de contentores**: inventário no pátio com tipos (`Normal`, `Refrigerado`, `Perigoso`, `Granel`), setores e expedição.
- **Gestão económica (€)**: receitas de atracação e movimentação, custos de operação de cais, armazenagem e espera em fila, cálculo de lucro.
- **Visualização em Canvas**: cais, gruas, navios atracados e contentores coloridos no pátio.
- **Persistência em JSON**: guardar e carregar em `data/porto_save.json`.

## Tecnologias Utilizadas
- Python 3.10+
- Biblioteca padrão: `tkinter`, `tkinter.ttk`, `random`, `json`, `pathlib`, `unittest`

## Estrutura dos Ficheiros
```
05_Porto_Maritimo/
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
1. Regista navios manualmente ou clica em **+ Navio Aleatório**.
2. Clica em **Otimizar Cais ⚡** (ou atraca manualmente na aba **Cais**).
3. Clica em **Executar Ciclo ▶** para operar gruas, movimentar contentores e calcular receitas/custos.
4. Gere e expede contentores na aba **Contentores** e acompanha o lucro na aba **Financeiro**.

## Como Executar os Testes
```bash
python3 -m unittest discover -s tests -v
```
