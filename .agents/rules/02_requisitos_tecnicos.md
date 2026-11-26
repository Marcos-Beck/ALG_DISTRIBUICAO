## Reutilização e arquitetura

A maioria das funcionalidades precisa continuar sendo reutilizável em outras campanhas.

Portanto:

- A lógica matemática deve ficar nos módulos genéricos, principalmente em `modules/distribuicao.py`.
- Os parâmetros específicos da Caixa Encantada devem ficar em `config/caixa_encantada/config.py`.
- As categorias e mapeamentos específicos devem continuar na configuração da campanha.
- Evitar nomes de campanhas, limites e parâmetros fixos dentro das funções genéricas.
- Não duplicar funções existentes.
- Não criar funções intermediárias que apenas chamem outras funções sem acrescentar responsabilidade.
- Não criar módulos adicionais apenas para fragmentar o fluxo.
- Manter a `main.py` como orquestradora.

Se alguma regra nova puder ser implementada como funcionalidade genérica configurável, prefira essa abordagem.

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