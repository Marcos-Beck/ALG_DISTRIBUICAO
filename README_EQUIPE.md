# Como Funciona a Distribuição de Brinquedos (Guia para a Equipe)

Este documento explica, de forma direta e sem termos técnicos de programação, como o sistema organiza as inscrições, protege a reserva de estoque e calcula quantos brinquedos cada instituição recebe.

---

## 1. O que o programa faz?

O programa cruza três informações principais da campanha:
1. **Quem pediu:** as planilhas de inscrição das instituições, com a quantidade solicitada por faixa etária (`0–3`, `4–7` e `8–12 anos`) e gênero (`Feminino` e `Masculino`).
2. **O que foi arrecadado:** a planilha de arrecadação, com o estoque de brinquedos `Feminino`, `Masculino` e `Unissex` em cada faixa etária.
3. **Onde ficam as cidades:** a tabela de regiões do estado, para identificar os municípios do interior e a capital.

A partir disso, o programa aplica regras fixas e transparentes para calcular a entrega de cada instituição e gerar a planilha final de conferência.

---

## 2. Como as instituições são organizadas antes da entrega

Antes de distribuir qualquer brinquedo, o sistema organiza todas as instituições seguindo critérios claros:

- **Divisão por tamanho do pedido (Prioridades):**
  - **Prioridade 1 (P1):** instituições que pediram **de 0 até 300 brinquedos**.
  - **Prioridade 2 (P2):** instituições que pediram **301 ou mais brinquedos**.
- **Ordem de atendimento e desempate:**
  - Respeita a **ordem de inscrição** da instituição.
  - Em caso de empate na ordem, instituições com **CNPJ válido** ficam na frente. *(Importante: quem tem CNPJ ausente ou inválido **não é excluído** da distribuição; apenas fica após quem tem CNPJ válido em caso de empate.)*
  - Na organização geográfica, municípios do **interior** são listados antes da **capital** dentro do agrupamento por região.

---

## 3. A regra da reserva obrigatória de 15% (estoque protegido)

A primeira conta que o programa faz é separar **15% de tudo o que foi arrecadado** como reserva intocável.

- Essa reserva de **15% é calculada separadamente** para cada faixa etária (`0–3`, `4–7`, `8–12`) e cada tipo (`Feminino`, `Masculino` e `Unissex`).
- Quando 15% dá um número quebrado, o sistema **arredonda a reserva para cima** (por exemplo, se `15%` der `15,15`, ficam `16` reservados). Assim, garantimos que pelo menos 15% ficam protegidos e nunca usamos mais do que os `85%` liberados.
- **Os brinquedos reservados nunca entram na distribuição**, mesmo que falte brinquedo para alguma instituição. Eles aparecem separados no relatório final para conferência.

> **Exemplo na campanha atual:** de **126.848** brinquedos arrecadados, **19.033 (15,00%)** ficam guardados na reserva e **107.815 (85,00%)** ficam disponíveis para entrega.

---

## 4. Como os brinquedos disponíveis (85%) são distribuídos

### Passo 1 — Atendimento da Prioridade 1 (pedidos de até 300 brinquedos)
- As instituições da **P1** têm prioridade absoluta sobre os `85%` disponíveis.
- Se houver estoque suficiente naquela faixa etária e gênero, cada instituição da P1 recebe **100% do que pediu**.
- Se em alguma faixa específica (por exemplo, `0–3 Masculino`) não houver brinquedos suficientes para atender todo mundo da P1 integralmente, o programa divide o que existe aos poucos, dando parcelas iguais para todas antes de avançar para a próxima rodada — garantindo que nenhuma instituição da P1 fique sem nada enquanto outra da mesma prioridade recebe tudo.

---

### Passo 2 — Atendimento da Prioridade 2 (pedidos acima de 300 brinquedos)
Tudo o que sobra após a P1 vai para a **P2**, onde todas as instituições acima de 300 participam juntas de duas etapas seguidas:

#### Etapa A — Meta mínima progressiva de 200 brinquedos
- O sistema busca aproximar **todas** as instituições da P2 de um mínimo de **200 brinquedos**, de forma equilibrada.
- Primeiro, distribui a meta de 200 proporcionalmente às faixas etárias e gêneros que a própria instituição pediu (se ela pediu metade em `4–7` e metade em `8–12`, a meta de 200 segue essa proporção).
- Se faltar estoque em uma faixa (por exemplo, `0–3`), o programa tenta compensar usando outras faixas que a instituição também pediu e que ainda tenham saldo, sem passar de 200 no total desta etapa e sem entregar nada que ela não tenha pedido.
- **Quando o estoque total não dá para entregar 200 a cada instituição** (como aconteceu na base real da campanha atual, onde o saldo restante para as 332 instituições da P2 era de 49.733 brinquedos, ou seja, cerca de 150 por instituição), a meta funciona como uma subida equilibrada: todas avançam juntas até o estoque acabar, sem favorecer arbitrariamente uma instituição em detrimento de outra.

#### Etapa B — Divisão proporcional com redução gradual para pedidos muito altos
Quando ainda sobram brinquedos após atingir a meta de 200, o restante é dividido **proporcionalmente ao que ainda falta para cada instituição**, aplicando uma regra de **redução gradual de peso** para pedidos muito grandes:

- **Até 700 brinquedos pedidos:** peso total (`100%` / `1,0`). Não sofre redução.
- **De 701 a 1.199 brinquedos pedidos:** o peso vai diminuindo aos poucos, de maneira suave e contínua, conforme o pedido se aproxima de 1.200.
  - *Exemplo:* quem pede `700` tem peso `1,00` (`100%`); quem pede `900` tem peso `0,60` (`60%`); quem pede `1.100` tem peso `0,20` (`20%`).
  - Isso evita "degraus injustos": uma instituição que pediu `701` tem peso `0,998` — praticamente idêntico ao de quem pediu `700`.
- **Para o teto máximo de 1.200 brinquedos pedidos:** aplica-se a penalidade máxima (`peso 0` nesta etapa extra). Na prática, isso significa que quem pede `1.200` participa normalmente da **meta mínima de 200** na Etapa A, mas não recebe complementos extras na Etapa B — ficando limitada a **até 200 brinquedos** (se o estoque permitir).

#### Como funciona a redistribuição de sobras (cotas)
Se, durante a divisão proporcional de uma faixa etária, uma instituição menor atingir **100% do que ela havia pedido** naquela faixa e ainda sobrar parte da cota calculada para ela, o programa **não desperdiça** essa sobra e **não entrega mais do que ela pediu**: esse excedente é automaticamente recalculado e redistribuído entre as demais instituições que ainda têm demanda aberta naquela faixa.

---

### Passo 3 — Como entram os brinquedos Unissex
Em cada faixa etária (`0–3`, `4–7` e `8–12`):
1. Primeiro o sistema entrega os brinquedos específicos **Femininos** e **Masculinos**.
2. Só depois o estoque **Unissex** entra para cobrir o que ainda ficou faltando nas duas demandas, sendo dividido proporcionalmente ao tamanho da falta feminina e da falta masculina.
3. Cada brinquedo unissex é usado **uma única vez** (ou vai para atender um pedido feminino, ou vai para atender um pedido masculino), evitando contagem dupla.

---

## 5. Garantias matemáticas do resultado

Independentemente da quantidade arrecadada ou pedida, o algoritmo assegura que:
- **Nenhuma instituição recebe mais brinquedos do que solicitou** (nem no total, nem por faixa etária ou gênero).
- **Nenhuma categoria de estoque fica negativa.**
- **Os 15% reservados nunca são tocados.**
- **Não há entrega arbitrária:** se em alguma faixa sobrarem brinquedos que ninguém mais tem direito a receber pelas regras (por exemplo, quando todas as demais instituições elegíveis já foram 100% atendidas naquela faixa e só restam pedidos de `1.200` travados no teto mínimo), o excedente fica registrado como **Estoque Restante Distribuível**, separado da reserva.

---

## 6. Como ler os arquivos de resultado

Os resultados são salvos na pasta `output/Caixa Encantada 2026/`:

- **`distribuicao.csv`**: tabela completa linha a linha (uma linha por instituição), pronta para importação em outros sistemas.
- **`distribuicao.xlsx`**: arquivo Excel organizado em **4 abas**:
  1. **`Distribuicao`**: mostra todas as 736 instituições, com sua prioridade (`P1` ou `P2`), região, cidade, ordem de inscrição, validade do CNPJ, quanto pediu e quanto recebeu em cada faixa (`Feminino`, `Masculino` e `Unissex`), além do **Percentual de Atendimento (%)** e do **Peso da Penalização** aplicado.
  2. **`Resumo_Geral`**: resumo executivo com os totais da campanha (`Total Arrecadado`, `Total Reservado 15%`, `Total Disponível 85%`, `Total Distribuído`, `Estoque Restante Distribuível` e os totais pedidos/atendidos de `P1` e `P2`).
  3. **`Resumo_Estoque`**: conferência detalhada por faixa etária (`0–3`, `4–7`, `8–12`) e tipo (`feminino`, `masculino`, `unissex`), provando que `Consumido + Restante Distribuivel = Disponivel (85%)` e que os `15%` reservados permaneceram intactos.
  4. **`Resumo_Prioridades`**: resumo comparativo entre `P1` e `P2` (quantidade de instituições, demanda total, total atendido, falta e percentual médio de atendimento).

---

## 7. Ajustes futuros pela equipe

Se em próximas campanhas a equipe quiser alterar limites — como mudar o corte da P1 (`300`), o valor do mínimo (`200`), o ponto onde começa a penalização (por exemplo, de `700` para `800`) ou o percentual da reserva (`15%`) — basta atualizar os valores no arquivo de configuração da campanha (`config/caixa_encantada/campanha.py`), sem precisar reescrever as fórmulas de distribuição.
