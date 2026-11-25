# Guia de Apresentação — Projeto 06: Quiz Adaptativo Romeu e Julieta

## 1. Explicação Geral da Aplicação
O **Quiz Adaptativo — Romeu e Julieta** é um jogo educativo em Python com interface Tkinter inspirada no Kahoot e no Duolingo. Avalia conhecimentos sobre a tragédia de William Shakespeare através de 24 perguntas originais organizadas em cinco categorias e três níveis de dificuldade.

## 2. Ficheiros e Estruturas Principais
- [`app/dados.py`](../app/dados.py): lista `PERGUNTAS` com 24 dicionários (id, categoria, dificuldade, pergunta, 4 opções, índice correto e explicação).
- [`app/logica.py`](../app/logica.py): gestão da sessão, algoritmo adaptativo (`_adaptar_dificuldade`), pontuação com bónus e seleção de perguntas sem repetição.
- [`app/armazenamento.py`](../app/armazenamento.py): leitura, ordenação e gravação das classificações em `data/classificacoes.json`.
- [`app/interface.py`](../app/interface.py): ecrãs de entrada, pergunta com botões coloridos e quadro de classificações.

---

## 3. Possíveis Perguntas na Apresentação e Respostas

1. **Como funciona na prática o algoritmo adaptativo?**
   O jogador inicia no nível `Média`. Sempre que responde corretamente a 2 perguntas seguidas (ou acerta as últimas 3), o nível sobe até `Difícil`. Se errar 2 seguidas (ou tiver fraco desempenho recente), o nível desce até `Fácil`.

2. **Como garantes que nunca sai a mesma pergunta duas vezes na mesma ronda?**
   Cada pergunta respondida tem o seu `id` guardado na lista `estado["ids_usadas"]`. A função `selecionar_proxima_pergunta` filtra sempre `p["id"] not in usadas`.

3. **E se o jogador responder a todas as perguntas disponíveis de um determinado nível?**
   `selecionar_proxima_pergunta` ordena os níveis pela menor distância ao nível atual (`abs(NIVEIS_DIFICULDADE.index(n) - idx_nivel)`), escolhendo automaticamente o nível mais próximo que ainda tenha perguntas disponíveis.

4. **Como é calculada a pontuação?**
   As respostas certas dão pontos base consoante a dificuldade (`Fácil`: 100, `Média`: 150, `Difícil`: 220) mais um bónus de `25` pontos multiplicado pela sequência de acertos consecutivos menos um.

5. **Por que razão a sequência de acertos é reiniciada quando muda o nível?**
   Ao subir de dificuldade em `_adaptar_dificuldade`, reinicia-se `sequencia_acertos = 0` apenas para evitar que uma única resposta certa logo a seguir volte a tentar subir imediatamente; no entanto, o contador máximo de sequência (`melhor_sequencia`) fica registado para a classificação. (Nota: na verdade no código `sequencia_acertos` zera ao subir — boa observação para explicar exatamente o que o código faz!).

6. **Como são ordenadas as classificações no quadro final?**
   Em `armazenamento.py`, `sorted(lista, key=lambda r: (-r.get("pontuacao", 0), -r.get("acertos", 0)))` ordena primeiro por pontuação decrescente e, em caso de empate, pelo maior número de acertos.

7. **O que acontece se um aluno fechar e abrir o programa? Os recordes mantêm-se?**
   Sim, porque cada ronda terminada grava o registo no ficheiro `data/classificacoes.json`, que é lido sempre que se consulta a tabela de classificações.

8. **Como estão estruturadas as perguntas na memória?**
   Cada pergunta é um dicionário com chaves padronizadas (`id`, `categoria`, `dificuldade`, `pergunta`, `opcoes`, `indice_correto`, `explicacao`), facilitando a filtragem e a validação automática nos testes.

9. **Como foi validado o conteúdo literário das perguntas?**
   Os testes verificam a estrutura (4 opções, 5 categorias, 3 níveis e explicação preenchida), e as perguntas baseiam-se apenas nos acontecimentos, personagens, temas e contexto isabelino da obra de Shakespeare, sem citações extensas protegidas.

10. **Como impediste que o jogador carregue várias vezes na mesma resposta para somar pontos?**
    No método `_ao_responder`, logo no primeiro instante todos os 4 botões de opção são desativados (`state=tk.DISABLED`) antes de mostrar o feedback e o botão "Próxima".
