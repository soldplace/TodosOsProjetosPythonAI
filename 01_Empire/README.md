# Empire — Jogo de Decisão e Estratégia Territorial

## Objetivo
Simulador de estratégia por turnos desenvolvido em Python (com interface Tkinter) no âmbito da disciplina de Aplicações Informáticas B (12.º ano). O jogador governa o Império Lusitano e procura expandir o seu domínio num continente dividido em 25 territórios.

## Descrição
O jogo combina gestão económica (ouro, madeira, ferro e alimentos), recrutamento e movimentação militar, combate tático entre territórios adjacentes, construção de melhorias, investigação tecnológica e adversários controlados pelo computador.

## Funcionalidades
- **Mapa estratégico em grelha 5x5** desenhado em `tkinter.Canvas`, com cores por facção, símbolos de terreno e contagem de tropas.
- **Gestão de recursos**: ouro, madeira, ferro e alimentos com produção por território e custos de manutenção do exército.
- **Operações militares**: recrutamento, movimentação entre territórios aliados adjacentes e combate por turnos considerando terreno, melhorias, tecnologias e aleatoriedade controlada.
- **Desenvolvimento**: melhorias económicas e militares até nível 3 e árvore de tecnologias desbloqueáveis.
- **Inteligência Artificial simples**: dois reinos rivais (Reino de Valória e Império de Kael) que recolhem recursos, recrutam tropas e atacam alvos vulneráveis.
- **Condições de vitória e derrota**: vitória ao conquistar todos os territórios ou ao eliminar os impérios rivais controlando pelo menos 20 territórios; derrota se perder todos os territórios.
- **Persistência em JSON**: guardar e carregar partidas na pasta `data/`.

## Tecnologias Utilizadas
- Python 3.10+
- Biblioteca padrão: `tkinter`, `tkinter.ttk`, `random`, `math`, `json`, `pathlib`, `unittest`

## Estrutura dos Ficheiros
```
01_Empire/
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
A partir da pasta `01_Empire/`:
```bash
python3 main.py
```

## Como Utilizar
1. Clica num território azul (teu) para recrutar soldados.
2. Clica num território vizinho neutro (cinza) ou inimigo (vermelho/roxo), escolhe a origem aliada adjacente e o número de tropas e clica em **Atacar Território**.
3. Usa as abas **Melhorias** e **Tecnologias** para fortalecer a economia e o exército.
4. Clica em **Terminar Turno** para recolher recursos, pagar manutenção e deixar os adversários jogar.
5. Utiliza **Guardar** e **Carregar** no topo para gravar ou retomar uma campanha.

## Como Executar os Testes
A partir da pasta `01_Empire/`:
```bash
python3 -m unittest discover -s tests -v
```
