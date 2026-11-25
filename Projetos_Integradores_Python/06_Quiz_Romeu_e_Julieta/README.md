# Quiz Adaptativo — Romeu e Julieta

## Objetivo
Jogo educativo em Python com interface Tkinter sobre a obra *Romeu e Julieta*, de William Shakespeare, desenvolvido para Aplicações Informáticas B (12.º ano). O quiz adapta dinamicamente a dificuldade das perguntas ao desempenho do jogador.

## Funcionalidades
- **24 perguntas originais** sobre *Romeu e Julieta*, distribuídas pelas 5 categorias (`Personagens`, `Enredo`, `Acontecimentos`, `Temas da obra`, `Contexto literário`) e 3 níveis (`Fácil`, `Média`, `Difícil`).
- **Algoritmo adaptativo real**: ajusta a dificuldade para cima após acertos consistentes e para baixo após erros seguidos.
- **Sistema de pontuação com sequências**: pontos por dificuldade + bónus crescente para respostas certas consecutivas.
- **Feedback imediato**: indica a resposta correta e apresenta uma explicação literária após cada pergunta.
- **Interface roxa e colorida** inspirada em plataformas educativas modernas.
- **Classificações persistentes** em `data/classificacoes.json` ordenadas por pontuação.

## Tecnologias Utilizadas
- Python 3.10+
- Biblioteca padrão: `tkinter`, `tkinter.ttk`, `random`, `datetime`, `json`, `pathlib`, `unittest`

## Estrutura dos Ficheiros
```
06_Quiz_Romeu_e_Julieta/
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
1. Introduz o teu nome no ecrã inicial e clica em **▶ Começar Quiz**.
2. Lê a pergunta e escolhe uma das quatro opções coloridas.
3. Observa a explicação e a evolução da dificuldade até ao fim das 10 perguntas.
4. Consulta a tua posição no quadro final de classificações.

## Como Executar os Testes
```bash
python3 -m unittest discover -s tests -v
```
