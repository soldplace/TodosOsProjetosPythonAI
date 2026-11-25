# Colónia Marciana — Simulador de Gestão em Marte

## Objetivo
Simulador de gestão de sobrevivência espacial em Python com Tkinter, desenvolvido para a disciplina de Aplicações Informáticas B (12.º ano). O jogador administra a base **Ares-1** durante 30 dias marcianos (Sols).

## Descrição
A aplicação simula o equilíbrio entre produção energética, suporte de vida (água, oxigénio, alimentos), extração de materiais, crescimento populacional, infraestruturas e eventos aleatórios típicos de uma missão em Marte.

## Funcionalidades
- **Gestão de 5 recursos** (Energia, Água, Oxigénio, Alimentos e Materiais) com barras de progresso e saldo previsto por Sol.
- **Gestão populacional** com capacidade habitacional limitada pelas Cúpulas e índice de moral.
- **6 tipos de infraestruturas** que podem ser construídas e melhoradas até nível 5.
- **Eventos aleatórios**: tempestades de poeira, falhas elétricas, roturas de água, descobertas científicas, cápsulas de suprimentos e chegada de colonos.
- **Vista visual da base marciana** em `tkinter.Canvas` atualizada dinamicamente.
- **Condições de vitória (30 Sóis)** e derrota (colapso populacional ou de moral), com estatísticas finais.
- **Persistência em JSON** em `data/colonia_save.json`.

## Tecnologias Utilizadas
- Python 3.10+
- Biblioteca padrão: `tkinter`, `tkinter.ttk`, `random`, `copy`, `json`, `pathlib`, `unittest`

## Estrutura dos Ficheiros
```
02_Colonia_Marciana/
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
1. Analisa o balanço diário (`+X/sol` ou `-X/sol`) junto às barras de recursos.
2. Constrói ou melhora infraestruturas no painel direito antes de terminar o dia.
3. Clica em **Avançar Sol ▶** para executar a produção, consumo e possíveis eventos aleatórios.
4. Sobrevive 30 Sóis mantendo a população e a moral acima de 0.

## Como Executar os Testes
```bash
python3 -m unittest discover -s tests -v
```
