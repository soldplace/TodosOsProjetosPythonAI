# Guia de Apresentação — Projeto 05: Porto Marítimo

## 1. Explicação Geral da Aplicação
O **Port Manager** simula a gestão logística e económica de um porto marítimo. O utilizador coordena a chegada de navios, a alocação eficiente dos cais, a movimentação de contentores e o equilíbrio financeiro entre receitas e custos operacionais.

## 2. Ficheiros e Estruturas Principais
- [`app/dados.py`](../app/dados.py): definições dos 4 cais, tipos de contentores, prioridades e valores financeiros em euros.
- [`app/logica.py`](../app/logica.py): registo de navios, ordenação prioritária da fila, algoritmo *best-fit* de atracação, execução de ciclos e indicadores.
- [`app/armazenamento.py`](../app/armazenamento.py): persistência em `data/porto_save.json`.
- [`app/interface.py`](../app/interface.py): desenho do porto no `Canvas` e painéis em abas (`Navios & Fila`, `Cais`, `Contentores`, `Financeiro`).

---

## 3. Possíveis Perguntas na Apresentação e Respostas

1. **Como impedes que um navio grande atraque num cais pequeno?**
   A função `cais_compativel` compara o valor numérico de cada dimensão (`Pequeno=1`, `Médio=2`, `Grande=3`) no dicionário `ORDEM_DIMENSOES`, só permitindo a atracação se `cais >= navio`.

2. **Como funciona o algoritmo de otimização de cais?**
   `atribuir_cais_otimizado` ordena primeiro a fila por prioridade e espera, e depois aplica a estratégia *best-fit*: escolhe o menor cais livre compatível para não ocupar o Mega Terminal com um navio pequeno desnecessariamente.

3. **Como é garantido que dois navios nunca ocupam o mesmo cais ao mesmo tempo?**
   Em `atracar_navio`, verifica-se `if cais["ocupado"]` antes de atribuir o navio. Enquanto `ocupado` for `True`, qualquer tentativa de atracar outro navio nesse cais é recusada.

4. **Como é ordenada a fila de espera?**
   A função `obter_fila_espera_ordenada` usa `sorted` com a chave `(-ORDEM_PRIORIDADES[n["prioridade"]], -n["ciclos_espera"], n["ciclo_chegada"])`, dando prioridade a navios urgentes e, em empate, aos que esperam há mais tempo.

5. **Por que razão existem custos para navios em fila de espera?**
   Na logística portuária real, manter navios em espera gera custos de ineficiência e penalizações (`CUSTO_ESPERA_NAVIO_CICLO`), incentivando o gestor a otimizar o uso dos cais.

6. **Como é calculada a velocidade de descarga ou carga?**
   Cada cais tem um número de gruas (`1`, `2` ou `3`). Em cada ciclo, movimenta até `cais["gruas"] * MOVIMENTACAO_POR_GRUA` contentores.

7. **O que acontece quando todos os contentores de um navio são movimentados?**
   Quando `navio["contentores_restantes"] <= 0`, o estado do navio muda para `"Concluído"`, o cais é libertado (`ocupado = False`) e o contador `navios_concluidos` é incrementado.

8. **Como é calculada a taxa média de utilização dos cais?**
   Divide-se a soma dos ciclos em que cada cais esteve ocupado pelo total possível (`total_cais * ciclos_decorridos`) e multiplica-se por 100.

9. **Qual é a diferença entre os tipos de contentores?**
   Cada tipo (`Normal`, `Refrigerado`, `Perigoso`, `Granel`) tem receita de movimentação, custo de armazenamento por ciclo e cor distintos no pátio.

10. **Como lida o programa com entradas inválidas no registo de navios?**
    `registar_navio` valida se o nome não está vazio, se a dimensão/operação/prioridade existem nos dicionários de referência e se o número de contentores está entre 1 e 40.
