## Regra de comentários

Os comentários do código devem:

1. Estar em português do Brasil.
2. Não possuirem acentuação ou caracteres especiais como (ç)
3. Precisam ser diretos
4. Devem estar presentes em toda função
5. Devem manter o padrão de comentários já existentes no projeto
6. Precisam explicar partes relevantes do código. 

## Regra de trabalho obrigatória

Antes de executar qualquer alteração no código:

1. Analise o código existente e compreenda o funcionamento das funcionalidades envolvidas.
2. Apresente o que pretende alterar, por que a alteração é necessária e quais arquivos serão afetados.
3. Explique a lógica matemática de qualquer mudança no algoritmo, incluindo exemplos práticos.
4. Aguarde minha aprovação explícita antes de modificar os arquivos.

Durante a implementação:

- Trabalhe em pequenas etapas, sem executar uma refatoração completa de uma só vez.
- Após cada etapa, apresente as alterações realizadas e os resultados dos testes.
- Não avance para a próxima etapa sem minha aprovação.
- Não tome decisões sobre regras de negócio, critérios de distribuição ou parâmetros sem minha autorização.
- Se identificar uma inconsistência ou uma oportunidade de melhoria fora do escopo, apresente a sugestão separadamente e aguarde autorização.

**Autonomia para analisar e propor; aprovação obrigatória para implementar.**

A prioridade é preservar o funcionamento do software, garantir a correção matemática da distribuição e manter o código reutilizável e de fácil manutenção.

## Preservação das regras existentes

Não alterar as seguintes funcionalidades sem necessidade comprovada:

- Classificação quantitativa das instituições.
- Ordenação por ordem de inscrição.
- Validação matemática do CNPJ.
- Classificação geográfica.
- Identificação de capital e interior.
- Mapeamento de municípios e regiões.
- Tratamento de estoque feminino, masculino e unissex.
- Complementação da demanda com brinquedos unissex.
- Distribuição por faixa etária.
- Geração dos resultados por instituição.
- Relatórios e exportações existentes.
- Validações de consistência.

A ordem de inscrição e a validade matemática do CNPJ devem continuar sendo respeitadas na P1 e nas demais etapas em que a ordenação for necessária.

O CNPJ inválido ou ausente não deve excluir uma instituição.

O estoque unissex não pode ser contabilizado duas vezes: cada unidade física só pode complementar uma única demanda.

A distribuição deve continuar considerando as regiões e localidades, sem criar preferência geográfica indevida entre P2 e P3.