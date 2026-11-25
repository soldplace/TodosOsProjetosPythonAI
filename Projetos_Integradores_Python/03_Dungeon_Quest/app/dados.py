"""Constantes, monstros, equipamentos e definições da masmorra de Dungeon Quest."""

LINHAS_MASMORRA = 5
COLUNAS_MASMORRA = 5

MONSTROS_COMUNS = [
    {
        "nome": "Esqueleto Guardião",
        "hp": 22,
        "ataque": 7,
        "defesa": 2,
        "xp": 25,
        "ouro": 15,
        "simbolo": "💀",
    },
    {
        "nome": "Goblin Salteador",
        "hp": 18,
        "ataque": 8,
        "defesa": 1,
        "xp": 20,
        "ouro": 18,
        "simbolo": "👺",
    },
    {
        "nome": "Aranha das Sombras",
        "hp": 26,
        "ataque": 9,
        "defesa": 3,
        "xp": 32,
        "ouro": 22,
        "simbolo": "🕷️",
    },
    {
        "nome": "Cavaleiro Corrompido",
        "hp": 34,
        "ataque": 11,
        "defesa": 4,
        "xp": 45,
        "ouro": 35,
        "simbolo": "🛡️",
    },
]

CHEFE_FINAL = {
    "nome": "Malakor, Senhor da Masmorra",
    "hp": 68,
    "ataque": 14,
    "defesa": 5,
    "xp": 150,
    "ouro": 200,
    "simbolo": "🐉",
    "chefe": True,
}

ITENS_CATALOGO = [
    {
        "id": "pocao_menor",
        "nome": "Poção de Cura Menor",
        "tipo": "pocao",
        "valor": 20,
        "descricao": "Recupera 20 pontos de vida.",
    },
    {
        "id": "pocao_maior",
        "nome": "Elixir Rubro",
        "tipo": "pocao",
        "valor": 40,
        "descricao": "Recupera 40 pontos de vida.",
    },
    {
        "id": "espada_ferro",
        "nome": "Espada de Ferro",
        "tipo": "arma",
        "bonus": 4,
        "descricao": "Arma equilibrada (+4 Ataque).",
    },
    {
        "id": "lamina_arcana",
        "nome": "Lâmina Arcana",
        "tipo": "arma",
        "bonus": 8,
        "descricao": "Espada encantada (+8 Ataque).",
    },
    {
        "id": "cota_malha",
        "nome": "Cota de Malha",
        "tipo": "armadura",
        "bonus": 3,
        "descricao": "Proteção sólida (+3 Defesa).",
    },
    {
        "id": "armadura_runica",
        "nome": "Armadura Rúnica",
        "tipo": "armadura",
        "bonus": 6,
        "descricao": "Armadura forjada com runas (+6 Defesa).",
    },
]
