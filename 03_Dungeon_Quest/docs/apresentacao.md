# Guia de Apresentação — Projeto 03: Dungeon Quest

## 1. Explicação Geral da Aplicação
O **Dungeon Quest** é um RPG de exploração de masmorras desenvolvido em Python e Tkinter. O jogador guia um aventureiro por uma grelha de 25 salas, enfrentando monstros em combates por turnos, recolhendo tesouros, equipando armas e armaduras e evoluindo de nível até derrotar o chefe final.

## 2. Ficheiros e Estruturas Principais
- [`app/dados.py`](../app/dados.py): catálogo de monstros, chefe final e itens (poções, armas, armaduras).
- [`app/logica.py`](../app/logica.py): geração da masmorra, movimento, combate, evolução de nível e gestão de inventário.
- [`app/armazenamento.py`](../app/armazenamento.py): leitura e escrita de `data/dungeon_save.json`.
- [`app/interface.py`](../app/interface.py): interface escura medieval com `Canvas`, barras de HP/XP, controlos direcionais/teclado e inventário.

---

## 3. Possíveis Perguntas na Apresentação e Respostas

1. **Como é representada a masmorra em memória?**
   É uma lista de 25 dicionários (5 linhas × 5 colunas). A função `obter_sala(estado, linha, coluna)` converte as coordenadas num índice linear usando `linha * COLUNAS_MASMORRA + coluna`.

2. **Como funciona a névoa de guerra no mapa?**
   Cada sala tem um campo booleano `visitada`. Enquanto for `False`, o `Canvas` desenha apenas `?` num tom escuro. Ao entrar na sala, `visitada` passa a `True` e o conteúdo real é revelado.

3. **Como é calculado o ataque e a defesa totais?**
   As funções `calcular_ataque_total` e `calcular_defesa_total` somam o atributo base da personagem ao bónus da arma ou armadura atualmente equipada.

4. **O que acontece quando o jogador equipa uma nova arma?**
   Em `usar_ou_equipar_item`, a nova arma é retirada do inventário e colocada em `heroi["arma"]`, enquanto a arma anteriormente equipada regressa ao inventário para não se perder.

5. **Por que usaste um ciclo `while` na função `_adicionar_xp`?**
   Porque se um inimigo (como o Chefe) der XP suficiente para subir mais do que um nível de uma só vez, o `while heroi["xp"] >= heroi["xp_proximo"]` garante que todos os níveis merecidos são processados corretamente.

6. **Como funciona a opção de fugir do combate?**
   `fugir_combate` bloqueia a fuga se o inimigo for o Chefe Final. Contra monstros comuns, rola um dado de 6 lados: com 3 ou mais, o herói regressa a `posicao_anterior`; caso contrário, falha e sofre um contra-ataque.

7. **Para que serve a função `defender_em_combate`?**
   Permite recuperar 3 pontos de vida de fôlego e ativa a flag `defendendo`, que multiplica a defesa do herói por `1.8` durante o contra-ataque imediato do monstro.

8. **Como garantiste que nunca há dano zero ou negativo em combate?**
   Tanto no ataque do herói como no contra-ataque do monstro utiliza-se `max(1, ...)` para assegurar que qualquer golpe bem-sucedido causa pelo menos 1 ponto de dano.

9. **Como funcionam os atalhos de teclado?**
   O método `_configurar_teclas` associa as setas `<Up>`, `<Down>`, `<Left>` e `<Right>` da janela principal diretamente ao método `_acao_mover`.

10. **Como testaste a lógica de combate que envolve dados aleatórios?**
    As funções de combate aceitam parâmetros opcionais (`dado_heroi`, `dado_monstro`, `dado_fuga`). Nos testes com `unittest`, passamos valores fixos para verificar exatamente os cálculos de dano, fuga, subida de nível e vitória.
