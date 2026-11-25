# Guia de Apresentação — Projeto 01: Empire

## 1. Explicação Geral da Aplicação
O **Empire** é um jogo de estratégia por turnos desenvolvido em Python com interface gráfica `tkinter`. O jogador controla o *Império Lusitano* numa grelha 5×5 de territórios, competindo contra dois reinos adversários (*Reino de Valória* e *Império de Kael*) e territórios neutros.

## 2. Funcionamento das Principais Funcionalidades
- **Mapa Interativo**: Desenhado com `tkinter.Canvas`. Ao clicar numa região, o painel lateral exibe o proprietário, tipo de terreno, guarnição e produção.
- **Gestão Económica**: Cada território gera ouro, madeira, ferro e alimentos por turno, consoante o tipo (Planície, Floresta, Montanha, Aldeia ou Fortaleza).
- **Exército e Combate**: O jogador recruta tropas nos seus territórios, move-as entre regiões adjacentes e ataca vizinhos inimigos ou neutros.
- **Melhorias e Tecnologias**: Melhorias (Mercado, Quintas, Forjas, Muralhas) aumentam rendimentos ou força militar; tecnologias desbloqueiam bónus permanentes com pré-requisitos.
- **Persistência**: Guarda e carrega todo o estado da partida em `data/empire_save.json`.

## 3. Estruturas de Dados Utilizadas
- **Dicionário principal `estado`**: guarda `turno`, `estado_jogo`, `recursos`, `melhorias`, `tecnologias`, `territorios` e `registo`.
- **Lista `territorios`**: lista de 25 dicionários, cada um com `id`, `linha`, `coluna`, `nome`, `tipo`, `dono`, `guarnicao`, `producao` e `defesa_base`.
- **Dicionários de configuração** em `app/dados.py`: `FACCOES`, `TIPOS_TERRITORIO`, `MELHORIAS_DISPONIVEIS` e `TECNOLOGIAS_DISPONIVEIS`, evitando valores mágicos espalhados pelo código.

## 4. Principais Funções e Ficheiros
- [`main.py`](../main.py): inicia a aplicação.
- [`app/dados.py`](../app/dados.py): constantes, definições de terrenos, melhorias e tecnologias.
- [`app/logica.py`](../app/logica.py): `criar_novo_jogo`, `sao_adjacentes`, `recrutar_soldados`, `mover_tropas`, `atacar_territorio`, `construir_melhoria`, `investigar_tecnologia`, `terminar_turno` e `verificar_fim_de_jogo`.
- [`app/armazenamento.py`](../app/armazenamento.py): `guardar_partida` e `carregar_partida`.
- [`app/interface.py`](../app/interface.py): classe `AplicacaoEmpire` que desenha o mapa e liga os botões às funções da lógica.

---

## 5. Possíveis Perguntas na Apresentação e Respostas

1. **Como é que o programa sabe se dois territórios são vizinhos?**
   A função `sao_adjacentes` calcula `abs(t1["linha"] - t2["linha"]) + abs(t1["coluna"] - t2["coluna"]) == 1`. Se a soma das diferenças for exatamente 1, os territórios partilham um lado na grelha (adjacência ortogonal, sem diagonais).

2. **Por que razão separaste `logica.py` de `interface.py`?**
   Para separar as regras do jogo da parte visual. Assim, a lógica pode ser testada automaticamente com `unittest` sem precisar de abrir janelas gráficas, e o código fica mais fácil de manter.

3. **Como funciona o cálculo de combate?**
   Multiplica-se o número de tropas enviadas pelo fator de ataque do jogador (melhorias de Forjas e tecnologias) e por um fator aleatório entre `0.90` e `1.15`. Compara-se com a guarnição defensora multiplicada pelo bónus de terreno. Quem tiver maior força vence e as baixas são calculadas proporcionalmente.

4. **O que acontece se o jogador não tiver ouro ou alimentos suficientes para pagar a manutenção?**
   Na função `terminar_turno`, os recursos em falta ficam a zero e ocorre uma deserção de cerca de 20% dos soldados das guarnições do jogador (mantendo pelo menos 1 soldado por território).

5. **Como funciona a inteligência artificial dos inimigos?**
   Na função `_executar_turno_ia`, cada reino inimigo recolhe recursos conforme o número de territórios que possui, recruta tropas para o território mais fraco e verifica se algum território seu tem superioridade numérica (pelo menos 25% mais tropas disponíveis do que o alvo adjacente) para lançar um ataque.

6. **Como garantiste que os caminhos dos ficheiros funcionam em qualquer pasta?**
   Em `armazenamento.py`, o caminho base é calculado dinamicamente com `Path(__file__).resolve().parent.parent`, apontando sempre para a pasta `data/` dentro do próprio projeto.

7. **O que acontece se o utilizador tentar carregar um ficheiro de gravação corrompido ou inexistente?**
   A função `carregar_partida` verifica se o ficheiro existe e utiliza blocos `try/except (OSError, json.JSONDecodeError)` bem como validação das chaves obrigatórias, devolvendo uma mensagem de erro clara sem encerrar o programa.

8. **Como funcionam os pré-requisitos das tecnologias?**
   Cada tecnologia em `TECNOLOGIAS_DISPONIVEIS` tem uma chave `"requisito"`. Antes de desbloquear uma tecnologia, `investigar_tecnologia` verifica se o requisito já está presente na lista `estado["tecnologias"]`.

9. **Como o Canvas identifica qual território foi clicado?**
   No método `_ao_clicar_mapa`, as coordenadas `(evento.x, evento.y)` do rato são convertidas em índices de linha e coluna usando as mesmas dimensões de célula e margem usadas no desenho, obtendo o `id = linha * COLUNAS_MAPA + coluna`.

10. **Quais são as condições de vitória e derrota?**
    O jogador vence se conquistar todos os 25 territórios ou se eliminar os dois reinos inimigos mantendo pelo menos 20 territórios. Perde imediatamente se ficar com 0 territórios.
