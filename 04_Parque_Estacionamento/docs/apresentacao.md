# Guia de Apresentação — Projeto 04: Parque de Estacionamento

## 1. Explicação Geral da Aplicação
O **Parking Manager** simula a operação completa de um parque de estacionamento. Dispõe de planta visual vista de cima, validação rigorosa de matrículas, emissão de bilhetes, relógio simulado independente, tarifação em euros e painel de estatísticas.

## 2. Ficheiros e Estruturas Principais
- [`app/dados.py`](../app/dados.py): constantes de capacidade, tarifa padrão e cores dos veículos.
- [`app/logica.py`](../app/logica.py): validação de matrículas, relógio simulado, atribuição de lugares, cálculo de custos e estatísticas.
- [`app/armazenamento.py`](../app/armazenamento.py): persistência em `data/parque_save.json`.
- [`app/interface.py`](../app/interface.py): planta desenhada em `Canvas`, tabela `Treeview`, controlos de entrada/saída e configuração.

---

## 3. Possíveis Perguntas na Apresentação e Respostas

1. **Como é validada a matrícula dos veículos?**
   A função `normalizar_e_validar_matricula` remove espaços, converte para maiúsculas e aplica uma expressão regular (`PADRAO_MATRICULA`) que aceita os formatos oficiais portugueses como `AA-00-AA`, `00-AA-00`, `00-00-AA` e `AA-00-00`.

2. **Como impedes que dois veículos ocupem o mesmo lugar ou que o mesmo carro entre duas vezes?**
   Antes de estacionar, `registar_entrada` chama `encontrar_veiculo` para verificar se a matrícula já existe no parque. Depois seleciona o primeiro dicionário da lista `lugares` onde `ocupado == False` e marca-o imediatamente como ocupado.

3. **Por que razão a aplicação usa um relógio simulado em vez de usar apenas `datetime.now()`?**
   Porque numa demonstração ou apresentação de alguns minutos o tempo real seria insuficiente para testar permanências de várias horas. O relógio simulado permite avançar `+15 min`, `+1 hora` ou `+3 horas` instantaneamente.

4. **Qual é a regra de arredondamento aplicada no cálculo da tarifa?**
   Usa-se `math.ceil(minutos / 60)`, cobrando por cada hora iniciada, com cobrança mínima de 1 hora mesmo que o veículo saia logo após entrar (`0` minutos).

5. **Por que existe uma função `simular_saida` separada de `registar_saida`?**
   Para permitir mostrar primeiro ao utilizador o tempo de permanência e o valor exato em euros num diálogo de confirmação antes de libertar efetivamente o lugar e somar a receita.

6. **O que acontece se o utilizador tentar reduzir a capacidade do parque quando existem carros estacionados?**
   A função `reconfigurar_capacidade` verifica os lugares finais que seriam removidos; se algum estiver ocupado, bloqueia a alteração e informa o lugar que impede a redução.

7. **Como funciona o clique direto sobre um carro na planta do parque?**
   `_ao_clicar_lugar` calcula a linha e coluna clicadas no `Canvas` e, se o lugar estiver ocupado, preenche automaticamente a caixa de pesquisa de saída com a matrícula desse veículo.

8. **Como é calculado o tempo médio de permanência?**
   O estado acumula `soma_minutos_permanencia` e `total_saidas` sempre que um carro sai. Em `obter_estatisticas`, divide-se um pelo outro (protegido contra divisão por zero quando `total_saidas == 0`).

9. **Como são guardadas as datas no ficheiro JSON?**
   Como `datetime` não é serializável diretamente em JSON, o relógio e a hora de entrada são guardados em formato texto padrão ISO 8601 (`isoformat()`), sendo reconvertidos com `datetime.fromisoformat()` sempre que necessário.

10. **Como é assegurado que erros de entrada do utilizador (como tarifa negativa ou texto) não bloqueiam a aplicação?**
    Na interface, o bloco `try/except ValueError` valida a conversão numérica, e na lógica as funções verificam os limites e devolvem `(False, mensagem_clara)` para serem mostrados em caixas de aviso.
