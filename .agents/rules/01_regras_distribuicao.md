## 1. Contexto do projeto

Este projeto é um algoritmo de distribuição desenvolvido em Python para campanhas sociais.

O software já está implementado, funcional e possui resultados previamente testados. Portanto, **não quero uma reescrita do projeto nem uma reorganização estrutural desnecessária**.

## 2. Problema atual

Atualmente, a distribuição funciona com três prioridades:

- P1: instituições que solicitam até 200 brinquedos.
- P2: instituições que solicitam de 201 a 260 brinquedos.
- P3: instituições que solicitam 261 ou mais brinquedos.

O problema é que P1 e P2 acabam sendo atendidas integralmente antes que P3 receba os brinquedos restantes.

Isso faz com que instituições que solicitam quantidades maiores recebam apenas as sobras, mesmo quando atendem um número consideravelmente maior de crianças.

Exclua a P2 totalmente e aumente o limite da P1 para 300.

---

## 3. Nova política de distribuição

### Etapa 1 — Reserva obrigatória de estoque

**15% de todas as arrecadações devem permanecer integralmente reservadas e nunca poderão ser distribuídas.**

Essa reserva deve ser calculada sobre o estoque total arrecadado, considerando as categorias existentes.

Requisitos:

- A reserva deve ser calculada separadamente por faixa etária e gênero.
- O estoque unissex também deve ter sua reserva de 15%.
- Os valores reservados não podem ser utilizados em nenhuma etapa da distribuição.
- O estoque disponível para distribuição deve corresponder aos 85% restantes.
- A reserva precisa aparecer nos relatórios de diagnóstico e na conferência final do estoque.
- O algoritmo deve evitar arredondamentos que ultrapassem o limite de estoque reservado ou distribuível.

A reserva é uma regra obrigatória, não uma preferência ou parâmetro opcional.

### Etapa 2 — Atendimento da P1

A P1 permanece como prioridade absoluta.

As instituições P1 devem continuar recebendo atendimento integral sempre que houver estoque distribuível suficiente.

A reserva de 15% não pode ser utilizada para complementar a P1.

Caso não exista estoque suficiente para atender integralmente a P1, o algoritmo deve preservar as regras de distribuição progressiva já existentes, sem consumir o estoque reservado.

---

## 3. Mínimo de atendimento para as instituições acima de 200 solicitações

A distribuição de todas as instituições que realizaram solicitações acima de 200 devem receber um mínimo de 200 brinquedos, caso haja estoque suficiente.

As instituições que solicitaram até 200 entram na P1 e não devem receber valores maiores que o solicitado.


## 4. Penalização gradual de solicitações elevadas

Quero implementar um mecanismo de redução progressiva do peso de solicitações muito grandes.

Exemplo conceitual:

Uma instituição que solicita 300 brinquedos pode ter um peso proporcional maior em relação à sua solicitação do que uma instituição que solicita 1.100.

Já para instituições que solicitaram o valor máximo (1.200) a penalização deve ser o recebimento apenas da quantidade mínima.

O objetivo é evitar que solicitações excessivamente elevadas dominem a distribuição.

### Requisito fundamental: configuração centralizada

Os parâmetros dessa penalização devem ficar em um único local, preferencialmente no arquivo de configuração da campanha:

`config/caixa_encantada/config.py`

A equipe precisa conseguir alterar facilmente a partir de qual quantidade começa a penalização.

Exemplo ilustrativo de configuração:

```python
PENALIZACAO = {
    'ativa': True,
    'inicio': 900,
    'limite': 1100,
    'intensidade': 0.20
}
```

Os valores acima são apenas exemplos iniciais. Analise a melhor forma matemática de implementar esse mecanismo e apresente a proposta antes de fixar os parâmetros definitivos.

Um requisito importante é permitir que a equipe altere:

- A quantidade a partir da qual começa a penalização.
- A quantidade máxima considerada na regra.
- A intensidade da redução.
- A possibilidade de ativar ou desativar a penalização.

Por exemplo, se amanhã a equipe decidir que a penalização deve começar em 700, basta alterar:

```python
'inicio': 700
```

Não queremos precisar modificar a função de distribuição para fazer esse ajuste.

### Comportamento esperado

A penalização deve ser gradual, sem mudanças bruscas entre solicitações próximas.

Não deve existir uma diferença desproporcional entre uma instituição que solicita 699 e outra que solicita 700.

A fórmula deve ser documentada e seus efeitos precisam ser testados com diferentes volumes de solicitação.

Não penalize instituições exclusivamente por pertencerem à P3(nova P2). A penalização deve considerar o volume solicitado, independentemente da classificação de prioridade.

---

## 5. Proporcionalidade e distribuição progressiva

A distribuição entre P2 deve buscar um percentual equilibrado de atendimento em relação à solicitação de cada instituição, considerando os pesos definidos pela penalização.

Exemplo conceitual:

Se o percentual-base de atendimento for 20%:

- Uma instituição que solicita 230 deve receber aproximadamente 20% da sua solicitação, antes dos ajustes de estoque.
- Uma instituição que solicita 1.200 pode receber um percentual menor em função da penalização.
- Instituições com solicitações intermediárias devem ter uma redução intermediária.

A distribuição precisa ser progressiva e respeitar:

- O limite de solicitação de cada instituição.
- O estoque disponível por faixa etária.
- A divisão entre feminino e masculino.
- A utilização do estoque unissex como complemento.
- A reserva obrigatória de 15%.

Não distribuir quantidades arbitrárias apenas para consumir o estoque.

A quantidade destinada a cada instituição deve ser explicável e reproduzível.