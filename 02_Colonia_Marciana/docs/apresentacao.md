# Guia de Apresentação — Projeto 02: Colónia Marciana

## 1. Explicação Geral da Aplicação
O simulador **Colónia Marciana** coloca o utilizador no comando da missão espacial Ares-1. O objetivo é gerir a produção e o consumo diário de energia, água, oxigénio, alimentos e materiais para manter a população viva durante 30 sóis marcianos.

## 2. Estruturas de Dados e Ficheiros
- [`app/dados.py`](../app/dados.py): define `DIAS_OBJETIVO`, `LIMITES_RECURSOS`, `CONSUMO_POR_HABITANTE`, `INFRAESTRUTURAS` e `EVENTOS_MARCIANOS`.
- [`app/logica.py`](../app/logica.py): concentra as regras da simulação em funções independentes da interface.
- [`app/armazenamento.py`](../app/armazenamento.py): guarda e carrega o estado em `data/colonia_save.json`.
- [`app/interface.py`](../app/interface.py): apresenta as barras de progresso, o mapa da base no `Canvas`, os cartões de construção e o relatório diário.

---

## 3. Possíveis Perguntas na Apresentação e Respostas

1. **Como é calculado o impacto da falta de energia na colónia?**
   Se a energia produzida somada à reserva for inferior ao consumo das estruturas, a reserva vai a zero e calcula-se `eficiencia = max(0.35, energia_disp / consumo)`, reduzindo proporcionalmente a produção de água, oxigénio, alimentos e materiais nesse Sol.

2. **Como funciona o efeito da tempestade de poeira?**
   Quando ocorre o evento `tempestade_poeira`, o campo `dias_tempestade` é definido para 2. Enquanto for maior que zero, `calcular_balanco_previsto` aplica um fator de `0.60` aos painéis solares (-40% de energia).

3. **Como é garantido que os recursos não ficam negativos nem ultrapassam o armazenamento máximo?**
   Nas subtrações verifica-se se há recurso suficiente (caso contrário fica a `0`) e nas adições utiliza-se `min(LIMITES_RECURSOS[rec], valor)`.

4. **Por que razão existem duas ações distintas: Construir e Melhorar?**
   Construir aumenta a `quantidade` de unidades (aumentando também o consumo energético linearmente), enquanto melhorar sobe o `nivel` (aumentando a produtividade em +35% por nível com apenas +15% no consumo de energia).

5. **Como funciona a capacidade habitacional?**
   A função `calcular_capacidade_habitacional` soma uma base fixa (15) ao produto `quantidade * nivel * 8` das Cúpulas Habitacionais. Não é possível acolher colonos acima desse limite.

6. **Como se determina a vitória e a derrota?**
   Se `populacao <= 0` ou `moral <= 0`, a missão termina em derrota. Se a colónia sobreviver até ao fim do Sol 30 (`dia >= 30`), declara-se vitória com resumo estatístico.

7. **Qual é a vantagem de calcular o balanço previsto antes de avançar o dia?**
   Permite mostrar na interface o saldo líquido (`+X/sol` ou `-X/sol`) em tempo real, ajudando o jogador a antecipar faltas de recursos antes de avançar o Sol.

8. **Por que usaste `copy.deepcopy(ESTRUTURAS_INICIAIS)` ao criar uma nova colónia?**
   Porque `ESTRUTURAS_INICIAIS` contém dicionários aninhados. Uma cópia superficial (`dict(...)`) partilharia as referências internas entre partidas; `deepcopy` garante independência total.

9. **Como o programa lida com testes automatizados sem depender da sorte dos eventos aleatórios?**
   As funções `aplicar_evento_aleatorio` e `avancar_dia` aceitam parâmetros opcionais (`evento_forcado` e `permitir_evento`), permitindo testar cenários determinísticos com `unittest`.

10. **O que acontece se o utilizador tentar carregar um ficheiro JSON corrompido?**
    `carregar_colonia` captura `OSError` e `json.JSONDecodeError`, valida as chaves principais e devolve `(None, mensagem_de_erro)` para que a interface mostre um aviso amigável sem encerrar.
