"""Constantes e configurações do Simulador de Porto Marítimo."""

ORDEM_DIMENSOES = {
    "Pequeno": 1,
    "Médio": 2,
    "Grande": 3,
}

ORDEM_PRIORIDADES = {
    "Urgente": 3,
    "Alta": 2,
    "Normal": 1,
}

CAIS_INICIAIS = [
    {"id": "CAIS-1", "nome": "Cais 1 (Costeiro)", "capacidade_dimensao": "Pequeno", "gruas": 1},
    {"id": "CAIS-2", "nome": "Cais 2 (Comercial)", "capacidade_dimensao": "Médio", "gruas": 2},
    {"id": "CAIS-3", "nome": "Cais 3 (Atlântico)", "capacidade_dimensao": "Médio", "gruas": 2},
    {"id": "CAIS-4", "nome": "Cais 4 (Mega Terminal)", "capacidade_dimensao": "Grande", "gruas": 3},
]

TIPOS_CONTENTOR = {
    "Normal": {"receita": 120.0, "custo_armazem": 12.0, "cor": "#3498DB"},
    "Refrigerado": {"receita": 190.0, "custo_armazem": 28.0, "cor": "#1ABC9C"},
    "Perigoso": {"receita": 240.0, "custo_armazem": 38.0, "cor": "#E74C3C"},
    "Granel": {"receita": 100.0, "custo_armazem": 10.0, "cor": "#F39C12"},
}

RECEITA_ATRACACAO_BASE = 250.0
CUSTO_OPERACIONAL_CAIS_CICLO = 95.0
CUSTO_ESPERA_NAVIO_CICLO = 40.0
MOVIMENTACAO_POR_GRUA = 2  # Contentores movimentados por grua em cada ciclo

NOMES_NAVIOS_EXEMPLO = [
    "N/M Atlântico", "N/M Lusitânia", "N/M Vasco da Gama", "N/M Horizonte",
    "N/M Oceano Sul", "N/M Estrela Polar", "N/M Tagus Cargo", "N/M Albatroz",
]
