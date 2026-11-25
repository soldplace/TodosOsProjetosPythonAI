# Planeamento Alimentar Semanal (Consola)

## Objetivo
Aplicação de consola em Python para organizar as refeições de uma semana (Segunda-feira a Domingo), selecionar alimentos com quantidades em gramas e calcular automaticamente os respetivos valores nutricionais, desenvolvida para Aplicações Informáticas B (12.º ano).

> **Nota sobre os valores nutricionais**: Os dados da base predefinida correspondem a **valores de referência aproximados por 100g** para fins educativos, não estando vinculados a nenhuma tabela oficial específica.

## Funcionalidades
- **Planeamento semanal completo**: 7 dias (Segunda-feira a Domingo) × 5 refeições (`Pequeno-almoço`, `Lanche da manhã`, `Almoço`, `Lanche da tarde`, `Jantar`).
- **Base de dados de 24 alimentos** com pesquisa por nome e valores de calorias, proteínas, hidratos de carbono e gorduras por 100g.
- **Gestão completa de refeições**: adicionar alimentos (acumulando se repetido), alterar quantidades, remover alimentos ou substituir toda a refeição.
- **Cálculos automáticos**: totais por refeição, totais diários, totais semanais, médias diárias e distribuição percentual de macronutrientes.
- **Relatórios e comparação**: grelha semanal, gráfico de barras ASCII comparando calorias entre os dias e listagem das refeições ainda não planeadas.
- **Persistência em JSON**: guardar e carregar em `data/plano_semanal.json`.

## Tecnologias Utilizadas
- Python 3.10+
- Biblioteca padrão: `json`, `pathlib`, `unittest`

## Estrutura dos Ficheiros
```
07_Planeamento_Alimentar/
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
1. Navega pelo menu numérico da consola (`1` a `8`).
2. Consulta a tabela de alimentos (`1`) e adiciona alimentos com quantidade em gramas (`2`).
3. Edita, remove ou substitui refeições (`3`) e consulta relatórios diários (`4`) ou semanais (`5`).
4. Guarda (`6`) ou carrega (`7`) o teu plano em JSON.

## Como Executar os Testes
```bash
python3 -m unittest discover -s tests -v
```
