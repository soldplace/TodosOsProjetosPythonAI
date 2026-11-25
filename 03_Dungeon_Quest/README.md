# Dungeon Quest — Aventura RPG

## Objetivo
Jogo RPG de exploração de masmorras em Python com Tkinter, desenvolvido para a disciplina de Aplicações Informáticas B (12.º ano). O jogador explora uma masmorra 5×5, enfrenta monstros, recolhe equipamentos e tenta derrotar o chefe final.

## Funcionalidades
- **Personagem personalizável**: nome, pontos de vida, ataque, defesa, nível, experiência, ouro e equipamentos.
- **Exploração em grelha 5×5**: salas com névoa de guerra (descobertas ao entrar), monstros, baús de tesouro, fontes curativas e câmara do chefe.
- **Combate por turnos**: ações de atacar (com dados aleatórios), defender, usar poções ou fugir (exceto contra o chefe).
- **Inventário e evolução**: armas, armaduras e poções; subida de nível automática ao acumular experiência.
- **Estética medieval escura** com tons roxos e dourados em `tkinter.Canvas`.
- **Persistência em JSON**: guardar e carregar aventuras em `data/dungeon_save.json`.

## Tecnologias Utilizadas
- Python 3.10+
- Biblioteca padrão: `tkinter`, `tkinter.ttk`, `random`, `copy`, `json`, `pathlib`, `unittest`

## Estrutura dos Ficheiros
```
03_Dungeon_Quest/
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
1. Move o herói usando os botões **Norte / Sul / Este / Oeste** ou as setas do teclado.
2. Ao encontrar um monstro, usa **Atacar**, **Defender**, **Fugir** ou utiliza uma poção do inventário.
3. Seleciona armas ou armaduras no inventário e clica em **Usar / Equipar Item Selecionado**.
4. Chega à sala `(5, 5)` e derrota **Malakor, Senhor da Masmorra** para vencer.

## Como Executar os Testes
```bash
python3 -m unittest discover -s tests -v
```
