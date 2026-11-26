## Relatórios e diagnóstico

Os resultados precisam permitir a conferência completa da nova política.

Incluir, quando aplicável:

- Total arrecadado.
- Total reservado (15%).
- Total disponível para distribuição (85%).
- Total distribuído.
- Estoque restante distribuível.
- Demanda total P1.
- Demanda total P2 + P3.
- Quantidade atendida por prioridade.
- Percentual de atendimento por instituição.
- Peso aplicado pela penalização.
- Quantidade solicitada e quantidade efetivamente recebida.
- Conferência do consumo de estoque feminino, masculino e unissex.

A reserva precisa ser claramente diferenciada do estoque restante não utilizado.

Não apresentar os brinquedos reservados como estoque disponível.

---

## Testes obrigatórios

Antes de considerar a alteração concluída, executar testes para verificar:

1. P1 continua sendo atendida integralmente quando existe estoque suficiente.
2. P2 e P3 agora são apenas P2.
4. Instituições maiores continuam recebendo mais brinquedos em quantidade absoluta quando sua demanda e os pesos justificarem.
5. Solicitações elevadas recebem a penalização gradual configurada.
6. Alterar o início da penalização de 900 para 700 não exige modificar o código da função.
7. A penalização pode ser desativada pela configuração.
8. Os 15% reservados permanecem intactos em todas as situações.
9. Nenhuma instituição recebe mais brinquedos do que solicitou.
10. Nenhuma categoria de estoque apresenta saldo negativo.
11. O estoque unissex não é consumido mais de uma vez.
12. O consumo total corresponde ao estoque efetivamente distribuído.
13. Os resultados continuam contendo todas as instituições válidas.
14. Os relatórios refletem corretamente os novos critérios.

Também executar cenários artificiais com instituições de diferentes tamanhos de solicitação e estoque, incluindo 230, 260, 700, 900 e 1.200 brinquedos.

---

## Restrições de implementação

- Não reescrever o algoritmo inteiro.
- Não alterar funcionalidades que não estejam relacionadas ao problema.
- Não remover validações existentes.
- Não modificar os arquivos de entrada.
- Não sobrescrever os resultados anteriores sem preservar uma cópia.
- Não considerar a implementação concluída apenas porque o código executa sem erros.
- Não presumir que a distribuição está correta sem conferir os resultados matemáticos.

Trabalhe em etapas pequenas.

Primeiro, apresente a análise do algoritmo atual e a proposta matemática para a nova distribuição. Aguarde minha aprovação antes de alterar os arquivos.

Depois implemente a reserva de 15%, teste-a isoladamente e prossiga para a distribuição conjunta P2 + P3 e a penalização gradual.

Ao final, apresente um resumo dos arquivos alterados, das regras implementadas e dos resultados dos testes.