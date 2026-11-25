# Guia de Apresentação — Projeto 07: Planeamento Alimentar Semanal

## 1. Explicação Geral da Aplicação
O **Planeamento Alimentar Semanal** é uma aplicação exclusivamente de consola em Python que permite planear as 5 refeições diárias durante os 7 dias da semana, consultar uma base de 24 alimentos com valores de referência aproximados por 100g, calcular totais nutricionais e exportar/importar o plano em JSON.

## 2. Ficheiros e Estruturas Principais
- [`app/dados.py`](../app/dados.py): constantes `DIAS_SEMANA`, `REFEICOES`, `NOTA_NUTRICIONAL` e lista `ALIMENTOS_PREDEFINIDOS`.
- [`app/logica.py`](../app/logica.py): operações CRUD sobre refeições, cálculos proporcionais por porção, totais diários/semanais e deteção de refeições vazias.
- [`app/armazenamento.py`](../app/armazenamento.py): persistência e validação de `data/plano_semanal.json`.
- [`app/interface.py`](../app/interface.py): menus interativos de consola, validação segura de inputs e impressão de tabelas e gráficos ASCII.

---

## 3. Possíveis Perguntas na Apresentação e Respostas

1. **Como é estruturado o plano semanal em memória?**
   É um dicionário `{"dias": {...}}` onde cada um dos 7 dias aponta para outro dicionário com as 5 refeições, e cada refeição guarda uma lista de dicionários `{"alimento_id", "nome", "gramas"}`.

2. **Como são calculados os valores nutricionais para qualquer quantidade em gramas?**
   A função `calcular_nutrientes_porcao` divide a quantidade por `100.0` (`fator = gramas / 100.0`) e multiplica pelas calorias, proteínas, hidratos e gorduras de referência por 100g, arredondando a uma casa decimal.

3. **O que acontece se o utilizador adicionar o mesmo alimento duas vezes à mesma refeição?**
   Em `adicionar_alimento_refeicao`, o programa verifica se o `alimento_id` já existe naquela refeição e, se existir, soma as novas gramas ao registo existente em vez de duplicar a linha.

4. **Como é garantido que a substituição completa de uma refeição não apaga dados se um novo alimento for inválido?**
   A função `substituir_refeicao` valida primeiro todos os pares `(alimento_id, gramas)` numa lista temporária `itens_validados`; só se todos forem válidos é que substitui `plano["dias"][dia][refeicao]`.

5. **Como funciona a validação de entradas na consola?**
   As funções auxiliares `_ler_inteiro` e `_ler_gramas` usam ciclos `while True` com `try/except ValueError`, verificam os limites mínimo/máximo e permitem cancelar com `'c'`.

6. **Por que razão a aplicação indica que os valores nutricionais são aproximados?**
   Porque, para fins educativos e sem acesso a uma base de composição química certificada em tempo real, os valores são referências aproximadas por 100g, evitando atribuí-los incorretamente a fontes oficiais como o INSA.

7. **Como funciona a comparação visual entre os dias da semana?**
   No relatório semanal, encontra-se o valor máximo de calorias entre os 7 dias (`max_kcal`) e desenha-se uma barra proporcional com caracteres `#` até 18 colunas de largura.

8. **Como é calculada a distribuição do prato nutricional?**
   Soma-se o total em gramas dos três macronutrientes (`proteinas + hidratos + gorduras`) e calcula-se a percentagem de cada um para mostrar o equilíbrio da alimentação.

9. **Como o programa identifica refeições por planear?**
   `identificar_refeicoes_nao_planeadas` percorre os 7 dias e as 5 refeições (35 combinações) e recolhe todos os pares `(dia, refeicao)` cuja lista de alimentos esteja vazia.

10. **O que acontece se o ficheiro JSON carregado tiver um formato incorreto ou um dia em falta?**
    `carregar_plano` captura `OSError` e `json.JSONDecodeError`, verifica a presença da chave `"dias"` e valida cada dia de `DIAS_SEMANA`, devolvendo uma mensagem de erro clara se o ficheiro estiver corrompido.
