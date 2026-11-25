"""Constantes, configurações iniciais e definições de dados do jogo Empire."""

LINHAS_MAPA = 5
COLUNAS_MAPA = 5
TOTAL_TERRITORIOS = LINHAS_MAPA * COLUNAS_MAPA
OBJETIVO_TERRITORIOS_VITORIA = 20  # 80% do mapa

RECURSOS_INICIAIS_JOGADOR = {
    "ouro": 180,
    "madeira": 120,
    "ferro": 80,
    "alimentos": 150,
}

CUSTO_RECRUTAR_SOLDAO = {
    "ouro": 10,
    "alimentos": 5,
    "ferro": 2,
}

MANUTENCAO_POR_SOLDADO = {
    "ouro": 1,
    "alimentos": 1,
}

FACCOES = {
    "jogador": {
        "nome": "Império Lusitano (Tu)",
        "cor": "#2E86AB",
        "cor_borda": "#A9D6E5",
    },
    "inimigo_1": {
        "nome": "Reino de Valória",
        "cor": "#C0392B",
        "cor_borda": "#F5B7B1",
    },
    "inimigo_2": {
        "nome": "Império de Kael",
        "cor": "#8E44AD",
        "cor_borda": "#D7BDE2",
    },
    "neutro": {
        "nome": "Território Neutro",
        "cor": "#6E7B85",
        "cor_borda": "#BDC3C7",
    },
}

TIPOS_TERRITORIO = {
    "Planície": {
        "ouro": 12,
        "madeira": 6,
        "ferro": 4,
        "alimentos": 20,
        "defesa": 1.0,
        "simbolo": "🌾",
    },
    "Floresta": {
        "ouro": 10,
        "madeira": 20,
        "ferro": 5,
        "alimentos": 10,
        "defesa": 1.15,
        "simbolo": "🌲",
    },
    "Montanha": {
        "ouro": 15,
        "madeira": 4,
        "ferro": 18,
        "alimentos": 5,
        "defesa": 1.35,
        "simbolo": "⛰️",
    },
    "Aldeia": {
        "ouro": 22,
        "madeira": 10,
        "ferro": 6,
        "alimentos": 16,
        "defesa": 1.1,
        "simbolo": "🏘️",
    },
    "Fortaleza": {
        "ouro": 18,
        "madeira": 8,
        "ferro": 14,
        "alimentos": 10,
        "defesa": 1.5,
        "simbolo": "🏰",
    },
}

NOMES_TERRITORIOS = [
    "Vale Dourado", "Bosque Norte", "Pico Ferro", "Porto Bruma", "Serra Alta",
    "Campos Verdes", "Pinhal Real", "Minas Fundo", "Vila Nova", "Bastião Sul",
    "Planície Central", "Mata Antiga", "Rochedo Cinza", "Aldeia do Rio", "Forte Pedra",
    "Prado Leste", "Floresta Sombria", "Monte Rubro", "Várzea Clara", "Cidadela",
    "Costa Serena", "Bosque Sul", "Serra Negra", "Vila Prata", "Trono de Kael",
]

MELHORIAS_DISPONIVEIS = {
    "mercado": {
        "nome": "Mercado Imperial",
        "categoria": "Económica",
        "descricao": "+25% na produção de ouro por nível.",
        "custo": {"ouro": 80, "madeira": 60, "ferro": 20},
        "nivel_max": 3,
    },
    "quinta": {
        "nome": "Quintas Reais",
        "categoria": "Económica",
        "descricao": "+25% na produção de alimentos e madeira por nível.",
        "custo": {"ouro": 70, "madeira": 50, "ferro": 20},
        "nivel_max": 3,
    },
    "forja": {
        "nome": "Forjas de Guerra",
        "categoria": "Militar",
        "descricao": "+15% de força de ataque e +10 de ferro por turno.",
        "custo": {"ouro": 90, "madeira": 40, "ferro": 60},
        "nivel_max": 3,
    },
    "muralhas": {
        "nome": "Engenharia de Muralhas",
        "categoria": "Militar",
        "descricao": "+15% de defesa em todos os teus territórios por nível.",
        "custo": {"ouro": 85, "madeira": 70, "ferro": 50},
        "nivel_max": 3,
    },
}

TECNOLOGIAS_DISPONIVEIS = {
    "agricultura": {
        "nome": "Agricultura Avançada",
        "descricao": "Aumenta em 20% toda a produção de alimentos.",
        "custo": {"ouro": 100, "madeira": 60, "ferro": 20},
        "requisito": None,
    },
    "metalurgia": {
        "nome": "Metalurgia Refinada",
        "descricao": "Aumenta em 25% a produção de ferro e +10% ataque.",
        "custo": {"ouro": 120, "madeira": 40, "ferro": 50},
        "requisito": None,
    },
    "taticas_cerco": {
        "nome": "Táticas de Cerco",
        "descricao": "Reduz o bónus defensivo inimigo e dá +20% ataque.",
        "custo": {"ouro": 160, "madeira": 80, "ferro": 80},
        "requisito": "metalurgia",
    },
    "logistica": {
        "nome": "Logística Imperial",
        "descricao": "Reduz o custo de manutenção de ouro e alimentos em 30%.",
        "custo": {"ouro": 150, "madeira": 70, "ferro": 40},
        "requisito": "agricultura",
    },
}
