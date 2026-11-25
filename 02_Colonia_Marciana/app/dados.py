"""Constantes e configurações da simulação Colónia Marciana."""

DIAS_OBJETIVO = 30

LIMITES_RECURSOS = {
    "energia": 300,
    "agua": 300,
    "oxigenio": 300,
    "alimentos": 300,
    "materiais": 500,
}

RECURSOS_INICIAIS = {
    "energia": 120,
    "agua": 130,
    "oxigenio": 140,
    "alimentos": 120,
    "materiais": 110,
}

POPULACAO_INICIAL = 12
CAPACIDADE_BASE_CUPULA = 15

# Consumo por habitante por dia marciano (Sol)
CONSUMO_POR_HABITANTE = {
    "agua": 2,
    "oxigenio": 2,
    "alimentos": 2,
}

INFRAESTRUTURAS = {
    "painel_solar": {
        "nome": "Painéis Solares",
        "cor": "#F0A202",
        "custo_construir": {"materiais": 30},
        "custo_melhorar": {"materiais": 45},
        "energia_produzida": 25,
        "energia_consumida": 0,
        "producao": {},
        "descricao": "Produz energia elétrica (reduzida durante tempestades de poeira).",
    },
    "extrator_agua": {
        "nome": "Extratores de Água",
        "cor": "#3A86FF",
        "custo_construir": {"materiais": 35},
        "custo_melhorar": {"materiais": 50},
        "energia_produzida": 0,
        "energia_consumida": 10,
        "producao": {"agua": 18},
        "descricao": "Extrai e purifica gelo subterrâneo marciano.",
    },
    "gerador_oxigenio": {
        "nome": "Geradores de Oxigénio",
        "cor": "#4CC9F0",
        "custo_construir": {"materiais": 35},
        "custo_melhorar": {"materiais": 50},
        "energia_produzida": 0,
        "energia_consumida": 12,
        "producao": {"oxigenio": 18},
        "descricao": "Converte CO₂ atmosférico em oxigénio respirável.",
    },
    "estufa": {
        "nome": "Estufas Hidropónicas",
        "cor": "#52B788",
        "custo_construir": {"materiais": 40},
        "custo_melhorar": {"materiais": 55},
        "energia_produzida": 0,
        "energia_consumida": 10,
        "producao": {"alimentos": 18},
        "descricao": "Cultiva alimentos frescos para a população da colónia.",
    },
    "minerador": {
        "nome": "Escavadoras de Rególito",
        "cor": "#E07A5F",
        "custo_construir": {"materiais": 30},
        "custo_melhorar": {"materiais": 45},
        "energia_produzida": 0,
        "energia_consumida": 8,
        "producao": {"materiais": 16},
        "descricao": "Extrai metais e materiais de construção do solo marciano.",
    },
    "cupula": {
        "nome": "Cúpulas Habitacionais",
        "cor": "#C77DFF",
        "custo_construir": {"materiais": 60},
        "custo_melhorar": {"materiais": 75},
        "energia_produzida": 0,
        "energia_consumida": 8,
        "producao": {},
        "descricao": "Aumenta a capacidade habitacional (+10 colonos por unidade/nível).",
    },
}

ESTRUTURAS_INICIAIS = {
    "painel_solar": {"quantidade": 2, "nivel": 1},
    "extrator_agua": {"quantidade": 2, "nivel": 1},
    "gerador_oxigenio": {"quantidade": 2, "nivel": 1},
    "estufa": {"quantidade": 2, "nivel": 1},
    "minerador": {"quantidade": 1, "nivel": 1},
    "cupula": {"quantidade": 1, "nivel": 1},
}

EVENTOS_MARCIANOS = [
    {
        "id": "tempestade_poeira",
        "titulo": "Tempestade de Poeira",
        "tipo": "negativo",
        "descricao": "Poeira densa cobre os painéis solares: produção solar reduzida em 40% durante 2 dias.",
    },
    {
        "id": "falha_eletrica",
        "titulo": "Curto-Circuito na Rede",
        "tipo": "negativo",
        "descricao": "Uma sobrecarga consumiu 25 unidades de energia de reserva.",
    },
    {
        "id": "fuga_agua",
        "titulo": "Rotura numa Conduta de Água",
        "tipo": "negativo",
        "descricao": "Perderam-se 22 unidades de água antes da reparação de emergência.",
    },
    {
        "id": "descoberta_cientifica",
        "titulo": "Descoberta Científica",
        "tipo": "positivo",
        "descricao": "A equipa de investigação otimizou filtros e recuperou +25 água e +25 oxigénio.",
    },
    {
        "id": "capsula_suprimentos",
        "titulo": "Cápsula de Suprimentos da Terra",
        "tipo": "positivo",
        "descricao": "Chegou uma entrega orbital: +35 alimentos e +35 materiais de construção!",
    },
    {
        "id": "novos_colonos",
        "titulo": "Chegada de Colonos Especialistas",
        "tipo": "positivo",
        "descricao": "Se houver espaço nas cúpulas, novos colonos juntam-se à missão.",
    },
]
