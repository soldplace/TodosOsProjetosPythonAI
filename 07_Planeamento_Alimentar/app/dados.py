"""Constantes, dias, refeições e base de dados de alimentos (valores de referência aproximados por 100g)."""

DIAS_SEMANA = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]

REFEICOES = [
    "Pequeno-almoço",
    "Lanche da manhã",
    "Almoço",
    "Lanche da tarde",
    "Jantar",
]

NOTA_NUTRICIONAL = (
    "Nota: Os valores nutricionais apresentados são valores de referência aproximados por 100g "
    "para fins educativos."
)

# Valores de referência aproximados por 100g de alimento
ALIMENTOS_PREDEFINIDOS = [
    {"id": 1, "nome": "Aveia (flocos)", "calorias": 370.0, "proteinas": 13.0, "hidratos": 60.0, "gorduras": 7.0},
    {"id": 2, "nome": "Pão integral", "calorias": 245.0, "proteinas": 9.0, "hidratos": 43.0, "gorduras": 3.5},
    {"id": 3, "nome": "Leite meio-gordo", "calorias": 47.0, "proteinas": 3.3, "hidratos": 4.8, "gorduras": 1.6},
    {"id": 4, "nome": "Iogurte natural", "calorias": 60.0, "proteinas": 4.2, "hidratos": 4.5, "gorduras": 2.8},
    {"id": 5, "nome": "Ovo cozido", "calorias": 155.0, "proteinas": 13.0, "hidratos": 1.1, "gorduras": 11.0},
    {"id": 6, "nome": "Queijo fresco", "calorias": 98.0, "proteinas": 11.0, "hidratos": 3.0, "gorduras": 4.5},
    {"id": 7, "nome": "Banana", "calorias": 89.0, "proteinas": 1.1, "hidratos": 22.8, "gorduras": 0.3},
    {"id": 8, "nome": "Maçã", "calorias": 52.0, "proteinas": 0.3, "hidratos": 13.8, "gorduras": 0.2},
    {"id": 9, "nome": "Laranja", "calorias": 47.0, "proteinas": 0.9, "hidratos": 11.8, "gorduras": 0.1},
    {"id": 10, "nome": "Peito de frango grelhado", "calorias": 165.0, "proteinas": 31.0, "hidratos": 0.0, "gorduras": 3.6},
    {"id": 11, "nome": "Bife de peru grelhado", "calorias": 145.0, "proteinas": 29.0, "hidratos": 0.0, "gorduras": 2.8},
    {"id": 12, "nome": "Salmão grelhado", "calorias": 208.0, "proteinas": 20.0, "hidratos": 0.0, "gorduras": 13.0},
    {"id": 13, "nome": "Atum ao natural", "calorias": 116.0, "proteinas": 26.0, "hidratos": 0.0, "gorduras": 1.0},
    {"id": 14, "nome": "Arroz cozido", "calorias": 130.0, "proteinas": 2.7, "hidratos": 28.0, "gorduras": 0.3},
    {"id": 15, "nome": "Massa cozida", "calorias": 155.0, "proteinas": 5.5, "hidratos": 30.5, "gorduras": 0.9},
    {"id": 16, "nome": "Batata cozida", "calorias": 86.0, "proteinas": 1.9, "hidratos": 20.0, "gorduras": 0.1},
    {"id": 17, "nome": "Feijão cozido", "calorias": 127.0, "proteinas": 8.7, "hidratos": 22.8, "gorduras": 0.5},
    {"id": 18, "nome": "Grão-de-bico cozido", "calorias": 164.0, "proteinas": 8.9, "hidratos": 27.4, "gorduras": 2.6},
    {"id": 19, "nome": "Brócolos cozidos", "calorias": 35.0, "proteinas": 2.4, "hidratos": 7.2, "gorduras": 0.4},
    {"id": 20, "nome": "Cenoura cozida", "calorias": 35.0, "proteinas": 0.8, "hidratos": 8.2, "gorduras": 0.2},
    {"id": 21, "nome": "Salada mista (alface/tomate)", "calorias": 18.0, "proteinas": 1.0, "hidratos": 3.4, "gorduras": 0.2},
    {"id": 22, "nome": "Sopa de legumes", "calorias": 42.0, "proteinas": 1.5, "hidratos": 6.8, "gorduras": 1.0},
    {"id": 23, "nome": "Azeite virgem extra", "calorias": 884.0, "proteinas": 0.0, "hidratos": 0.0, "gorduras": 100.0},
    {"id": 24, "nome": "Amêndoas", "calorias": 579.0, "proteinas": 21.0, "hidratos": 21.6, "gorduras": 49.9},
]
