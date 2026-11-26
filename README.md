# Algoritmo de Distribuição de Brinquedos (`ALG_DISTRIBUICAO`)

Algoritmo desenvolvido em Python para automatizar e auditar a distribuição de brinquedos em campanhas sociais, conciliando regras de prioridade, reserva obrigatória de estoque, meta mínima progressiva, penalização gradual de grandes solicitações e complementação por estoque unissex.

O projeto foi estruturado de forma modular para separar o **motor genérico de distribuição** (`modules/`) das **regras e bases específicas de cada campanha** (`config/`), tendo como implementação principal a campanha **Caixa Encantada**.

---

## 1. Visão geral

O objetivo do sistema é distribuir um estoque limitado de brinquedos arrecadados (segmentados por **faixa etária**, **gênero/unissex**, **região** e **localidade**) entre instituições inscritas, garantindo:

- **Previsibilidade e reprodutibilidade:** toda quantidade alocada é calculada por critérios objetivos e determinísticos.
- **Preservação de reserva estratégica:** `15%` do total arrecadado em cada categoria permanece reservado e nunca é consumido na distribuição.
- **Priorização de demandas menores (`P1`):** instituições que solicitam até `300` brinquedos recebem atendimento prioritário integral (quando há estoque distribuível).
- **Equilíbrio entre demandas maiores (`P2`):** instituições que solicitam `301` ou mais brinquedos participam de uma etapa conjunta com meta mínima progressiva (`200`) e divisão proporcional ponderada por penalização gradual.
- **Rastreabilidade completa:** geração automática de planilhas com detalhamento por instituição, faixa etária, origem do estoque (específico vs. unissex) e abas de conferência global.

---

## 2. Tecnologias e dependências

- **Linguagem:** Python 3
- **Bibliotecas externas utilizadas no projeto:**
  - `pandas` — leitura, tratamento tabular, agrupamentos e exportação para CSV/Excel.
  - `openpyxl` — engine utilizada pelo `pandas` para leitura e escrita de planilhas `.xlsx` com múltiplas abas.
  - `colorama` — formatação e coloração de logs no terminal (`modules/terminal.py`).
  - `watchdog` — monitoramento de arquivos `.py` para reinício automático em modo de desenvolvimento (`dev.py`).
- **Biblioteca padrão do Python:** `argparse`, `datetime`, `fnmatch`, `math`, `os`, `pathlib`, `re`, `subprocess`, `sys`, `threading`, `time`, `unicodedata`.

---

## 3. Estrutura do projeto

```text
ALG_DISTRIBUICAO/
├── dev.py                          # Executor com monitoramento (hot-reload) para desenvolvimento
├── config/
│   └── caixa_encantada/            # Configuracao especifica da campanha Caixa Encantada
│       ├── main.py                 # Orquestrador principal da execucao da campanha
│       ├── campanha.py             # Parametros de negocio (prioridades, reserva, minimo, penalizacao)
│       ├── categorias.py           # Mapeamento entre colunas de demanda e colunas de estoque por faixa/genero
│       ├── fontes.py               # Caminhos dos arquivos de entrada, nomes de abas e colunas esperadas
│       ├── preparacao.py           # Carregamento das bases e chamada das rotinas de classificacao
│       └── regras.py               # Regras especificas da campanha (extracao de ordem e validacao de CNPJ)
├── data/
│   └── CE/                         # Bases de entrada (inscricoes, arrecadacoes e regioes)
├── modules/                        # Nucleo generico e reutilizavel entre campanhas
│   ├── leitura.py                  # Leitura de Excel/CSV e conversao de campos numericos/texto
│   ├── validacao.py                # Validacoes estruturais de DataFrames, colunas, nulos e duplicidade
│   ├── classificacao.py            # Classificacao quantitativa, validacao geografica e agrupamentos
│   ├── distribuicao.py             # Motor matematico (reserva, igualitario, unissex, minimo e proporcional)
│   ├── relatorio.py                # Geracao de resumos diagnosticos e exportacao Excel/CSV
│   └── terminal.py                 # Padronizacao visual de logs no terminal
├── output/
│   └── Caixa Encantada 2026/       # Saidas geradas (distribuicao.xlsx, distribuicao.csv e backup_anterior/)
└── test/                           # Scripts de testes modulares e de integracao
    ├── classificacao/
    │   ├── estoque.py
    │   ├── prioridade.py
    │   └── regiao_geo.py
    └── distribuicao/
        ├── estruturar_estoque.py
        ├── igualitario.py
        └── preparar_insti.py
```

---

## 4. Funcionamento (fluxo de execução)

O fluxo orquestrado por `config/caixa_encantada/main.py` segue cinco grandes etapas:

### Etapa 1 — Leitura e tratamento das bases (`preparacao.carregar_bases`)
- Lê a planilha de **inscrições** (`Inscrições`), a tabela de **regiões** (`Regiao.csv`) e a planilha de **arrecadações** (`Arrecadações`) com os caminhos e colunas definidos em `config/caixa_encantada/fontes.py`.
- Converte as colunas de estoque para valores numéricos inteiros (`leitura.numericos`), tratando células vazias como `0`.

### Etapa 2 — Classificação e preparação dos grupos (`preparacao.classificar_inscricoes` e `distribuicao`)
- Soma a demanda total de cada instituição nas categorias configuradas (`0-3`, `4-7`, `8-12`, feminino e masculino).
- Classifica cada instituição em **P1** ou **P2** conforme `PRIORIDADES_QTDE`.
- Extrai a ordem de inscrição a partir do nome do beneficiário (`regras.extrair_ordem_insc`) e valida matematicamente o CNPJ (`regras.validar_cnpj`). *Observação:* CNPJs inválidos ou ausentes não excluem a instituição; apenas posicionam-na após instituições com CNPJ válido em desempates de mesma ordem.
- Classifica geograficamente inscrições e arrecadações (`classificacao.classificar_geografia`), normalizando acentos/caixa e identificando `capital` vs. `interior`.
- Organiza os grupos priorizando regiões do interior antes da região da capital (`classificacao.organizar_por_regiao` e `preparar_grupos_geograficos`), consolidando depois na lista ordenada de distribuição (`distribuicao.preparar_grupos_distribuicao`).
- Estrutura o estoque arrecadado (`distribuicao.estruturar_estoque`) e consolida demanda e estoque por faixa etária e gênero (`resumir_demanda_estoque` e `comparar_solicitado_estoque`).

### Etapa 3 — Reserva obrigatória (`distribuicao.separar_reserva_estoque`)
- Separa `15%` do estoque bruto arrecadado por faixa etária e categoria (`feminino`, `masculino` e `unissex`), liberando apenas os `85%` restantes para a distribuição.

### Etapa 4 — Distribuição (`distribuicao.distribuir_todas_prioridades`)
- Executa **P1** (`0–300`) e, com o estoque distribuível restante, executa **P2** (`301+`).
- Calcula automaticamente o `Percentual Atendimento` e registra o `Peso Penalizacao` aplicado a cada instituição.

### Etapa 5 — Diagnóstico e exportação (`relatorio`)
- Gera as tabelas de conferência (`gerar_resumos_diagnostico`) com saldo bruto, reservado, distribuível, consumido e restante distribuível.
- Exporta os resultados em Excel multi-aba e CSV (`exportar_resultados`).

---

## 5. Regras de distribuição e lógica matemática

### 5.1. Prioridades (`P1` e `P2`)
- **P1 (`0` a `300` brinquedos solicitados):** prioridade absoluta sobre o estoque distribuível (`85%`). Recebe atendimento integral sempre que houver estoque disponível por faixa etária e gênero. Se alguma faixa/gênero não comportar atendimento integral, aplica-se a distribuição igualitária progressiva (`distribuir_igualitario`) sem jamais utilizar os `15%` reservados.
- **P2 (`301` ou mais brinquedos solicitados):** todas as instituições acima de 300 participam juntas de uma etapa única composta por duas sub-etapas (meta mínima progressiva + distribuição proporcional ponderada).

### 5.2. Reserva obrigatória de 15%
Para cada faixa etária e categoria (`feminino`, `masculino`, `unissex`):

$$\text{Reservado} = \min\Big(E_{\text{bruto}},\ \lceil E_{\text{bruto}} \times 0{,}15 \rceil\Big), \qquad E_{\text{distribuível}} = E_{\text{bruto}} - \text{Reservado}$$

- O arredondamento para cima (`math.ceil`) assegura que **ao menos 15%** de cada categoria permaneça reservado e que o estoque distribuível nunca ultrapasse o limite disponível.
- **Exemplo:** em `0-3 feminino` com `9.370` unidades arrecadadas, $\lceil 9370 \times 0{,}15 \rceil = 1.406$ ficam reservados (`15,01%`) e `7.964` ficam disponíveis para distribuição.

### 5.3. Meta mínima progressiva de 200 (`Sub-etapa 2A` da P2)
- Os `200` brinquedos atuam como **meta mínima progressiva**, e não como garantia absoluta (pois o saldo disponível após P1 pode ser inferior a $200 \times N_{\text{P2}}$).
- **Passe 1 (por perfil):** para cada instituição da P2, a meta de `200` é dividida proporcionalmente ao seu próprio perfil de solicitações nas 6 categorias `(faixa, gênero)`. Em seguida, o estoque disponível avança de forma igualitária progressiva em cada categoria (e no complemento unissex) até aproximar todas as instituições dessas metas sem ultrapassar o solicitado nem o estoque da faixa.
- **Passe 2 (compensação entre faixas):** se alguma instituição ficou abaixo de `200` por falta de estoque em uma faixa específica (por exemplo, `0-3`), o algoritmo tenta aproximá-la da meta usando apenas faixas onde ela ainda possua solicitação pendente e onde ainda exista estoque disponível, sem jamais superar `200` no total da Sub-etapa 2A.

### 5.4. Penalização gradual de solicitações elevadas
A penalização reduz progressivamente o peso de instituições com volumes muito altos na etapa proporcional (`Sub-etapa 2B`), com base no **volume total solicitado** $S$:

$$w(S) = \begin{cases} 1{,}0 & \text{se } \text{penalização desativada ou } S \le \text{inicio} \\ 1{,}0 - \text{intensidade} \times \dfrac{S - \text{inicio}}{\text{limite} - \text{inicio}} & \text{se } \text{inicio} < S < \text{limite} \\ \max(0{,}0,\ 1{,}0 - \text{intensidade}) & \text{se } S \ge \text{limite} \end{cases}$$

Com a configuração padrão (`inicio = 700`, `limite = 1200`, `intensidade = 1.0`):

| Solicitação Total ($S$) | Peso $w(S)$ | Comportamento |
|---:|---:|---|
| `301` a `700` | `1,0000` | Sem penalização |
| `701` | `0,9980` | Início gradual sem degrau |
| `900` | `0,6000` | Redução intermediária ($1 - 200/500$) |
| `1.100` | `0,2000` | Redução acentuada ($1 - 400/500$) |
| `1.199` | `0,0020` | Transição suave próxima ao limite |
| `1.200` | `0,0000` | Penalidade máxima: recebe `0` na etapa proporcional acima do mínimo (ficando em até `200`, se o estoque permitir) |

### 5.5. Distribuição proporcional ponderada e redistribuição de cotas (`Sub-etapa 2B` da P2)
Para cada faixa etária e gênero com saldo disponível $E_{\text{restante}}$ após a meta mínima:

1. Considera apenas instituições ativas ($r_i > 0$ e $w_i > 0$), onde $r_i$ é a solicitação restante da instituição naquela categoria.
2. Calcula a cota exata de cada instituição proporcionalmente à demanda ponderada $r_i \cdot w_i$:
   $$q_i = E_{\text{restante}} \times \frac{r_i \cdot w_i}{\sum_{j \in \text{ativas}} r_j \cdot w_j}$$
3. **Redistribuição de cotas:** se alguma instituição obtiver $q_i \ge r_i$, ela recebe exatamente $r_i$ (100% da sua demanda restante na categoria) e o excedente da cota é recalculado em nova rodada entre as demais instituições ativas.
4. Quando nenhuma instituição atinge o teto na rodada, cada uma recebe $\lfloor q_i \rfloor$ e as unidades inteiras residuais são distribuídas uma a uma às maiores frações decimais (desempatando pela ordem de classificação: inscrição, CNPJ válido e ordem geográfica).
5. Caso restem apenas instituições com $w_i = 0$ (como solicitações máximas de `1.200`), o saldo excedente não é alocado arbitrariamente e permanece registrado como `Restante Distribuivel`.

### 5.6. Uso do estoque unissex (sem consumo duplo)
Em cada faixa etária (`0-3`, `4-7`, `8-12`):
- Primeiro são distribuídos os estoques específicos `feminino` e `masculino`.
- O estoque `unissex` atua apenas sobre os déficits restantes (`falta_fem` e `falta_masc`), dividindo-se proporcionalmente entre os dois gêneros (`distribuir_unissex`) e sendo abatido diretamente de `estoque_atual[faixa]['unissex']`.
- Cada unidade física unissex complementa uma única demanda (feminina ou masculina), garantindo que `consumo_especifico + consumo_unissex == total_distribuido`.

---

## 6. Configuração da campanha (`config/caixa_encantada/campanha.py`)

Os principais parâmetros de negócio ficam centralizados em `config/caixa_encantada/campanha.py` e não exigem alterações nas funções de `modules/`:

```python
# Prioridades quantitativas
PRIORIDADES_QTDE = {
    1: {'min': 0, 'max': 300},
    2: {'min': 301, 'max': None}
}

# Reserva obrigatoria de estoque
RESERVA = {
    'ativa': True,
    'percentual': 0.15,
    'arredondamento': 'cima'  # 'cima' usa math.ceil; outro valor usa math.floor
}

# Meta minima progressiva de atendimento
MINIMO_ATENDIMENTO = {
    'ativo': True,
    'quantidade': 200,
    'prioridades': [2]
}

# Penalizacao gradual de solicitacoes elevadas
PENALIZACAO = {
    'ativa': True,
    'inicio': 700,
    'limite': 1200,
    'intensidade': 1.0
}
```

Exemplos de ajustes rápidos via configuração:
- **Alterar início da penalização para `900`:** mudar apenas `'inicio': 900` em `PENALIZACAO`.
- **Desativar a penalização:** mudar `'ativa': False` em `PENALIZACAO`.
- **Desativar o mínimo progressivo:** mudar `'ativo': False` em `MINIMO_ATENDIMENTO`.
- **Alterar percentual de reserva:** mudar `'percentual'` ou desativar com `'ativa': False` em `RESERVA`.

Outros arquivos da pasta `config/caixa_encantada/`:
- `categorias.py`: mapeia cada faixa (`0-3`, `4-7`, `8-12`) para suas colunas de demanda e estoque (`F 0-3` / `Fem 0-3`, `Uni 0-3`, etc.).
- `fontes.py`: define os arquivos em `data/CE/` (`Conjunto de Dados - CE 26.xlsx`, `BASE_DADOS_CE_2025.xlsx`, `Regiao.csv`), nomes das abas e listas de colunas lidas.
- `regras.py`: define `extrair_ordem_insc` (regex no prefixo numérico de `Beneficiario`) e `validar_cnpj` (cálculo dos dígitos verificadores).

---

## 7. Execução

Execute os comandos a partir da raiz do projeto (`ALG_DISTRIBUICAO/`).

### Execução principal da campanha
```powershell
python -m config.caixa_encantada.main
```

### Execução em modo desenvolvimento (hot-reload ao salvar arquivos `.py`)
```powershell
python dev.py config/caixa_encantada/main.py
```
*(Sem argumentos, `python dev.py` exibe um menu interativo listando os scripts `.py` disponíveis.)*

### Execução dos scripts de teste existentes
```powershell
python -m test.classificacao.prioridade
python -m test.classificacao.estoque
python -m test.classificacao.regiao_geo
python -m test.distribuicao.estruturar_estoque
python -m test.distribuicao.igualitario
python -m test.distribuicao.preparar_insti
```

---

## 8. Resultados gerados

Ao concluir a execução, `relatorio.exportar_resultados` grava os arquivos em `output/<NOME> <ANO>/` (para 2026: `output/Caixa Encantada 2026/`):

1. **`distribuicao.csv`** (separador `;`, codificação `utf-8-sig`): tabela consolidada com **50 colunas** contendo todas as instituições válidas, identificação de prioridade/região/localidade/ordem/CNPJ, detalhamento por faixa (`Solicitado`, `Distribuido` específico, `Distribuido Unissex`, `Atendido`, `Falta`), totais gerais (`Solicitado Total`, `Atendido Total`, `Falta Total`), `Percentual Atendimento` e `Peso Penalizacao`.
2. **`distribuicao.xlsx`**: planilha Excel com **4 abas**:
   - `Distribuicao`: os mesmos registros detalhados das instituições exportados no CSV.
   - `Resumo_Geral`: indicadores consolidados (`Total Arrecadado (Bruto)`, `Total Reservado (15% - Intacto)`, `Total Disponivel para Distribuicao (85%)`, `Total Distribuido`, `Estoque Restante Distribuivel (Nao inclui reserva)`, `Demanda Total P1/P2` e `Quantidade Atendida P1/P2`).
   - `Resumo_Estoque`: conferência por faixa etária (`0-3`, `4-7`, `8-12`) e categoria (`feminino`, `masculino`, `unissex`), exibindo `Arrecadado Bruto`, `Reservado (15%)`, `Disponivel Distribuicao (85%)`, `Consumido` e `Restante Distribuivel`.
   - `Resumo_Prioridades`: consolidado por prioridade (`Instituicoes`, `Solicitado Total`, `Atendido Total`, `Falta Total` e `Percentual Atendimento (%)`).

### Resultados observados na base `Caixa Encantada 2026`
- **Total de instituições processadas:** `736` (`404` em P1 e `332` em P2).
- **Estoque bruto arrecadado:** `126.848` brinquedos.
- **Reserva obrigatória (15% $\uparrow$):** `19.033` brinquedos (intactos).
- **Disponível para distribuição (85%):** `107.815` brinquedos.
- **Total distribuído:** `107.815` brinquedos (`58.082` para P1 — `91,13%` da demanda P1; `49.733` para P2 — `21,72%` da demanda P2), com `0` de restante distribuível.

*(Nota: o diretório `output/Caixa Encantada 2026/backup_anterior/` preserva cópia dos arquivos anteriores à aplicação das novas regras.)*

---

## 9. Reutilização em outras campanhas

Como toda a lógica matemática está isolada em `modules/`, adaptar o sistema para uma nova campanha exige apenas criar uma nova pasta em `config/<nova_campanha>/` seguindo o padrão de `config/caixa_encantada/`:

1. **`fontes.py`:** apontar para as planilhas e colunas da nova campanha.
2. **`categorias.py`:** definir as faixas etárias e o mapeamento de colunas de demanda e estoque (`feminino`, `masculino`, `unissex`).
3. **`campanha.py`:** configurar `NOME`, `ANO`, `CAPITAL`, `PRIORIDADES_QTDE`, `RESERVA`, `MINIMO_ATENDIMENTO` e `PENALIZACAO` de acordo com a política da nova campanha (podendo inclusive desativar reserva, mínimo ou penalização sem alterar `modules/distribuicao.py`).
4. **`regras.py` e `preparacao.py`:** ajustar extração de ordem/identificadores caso o formato da planilha mude e reutilizar `leitura` e `classificacao`.
5. **`main.py`:** manter a orquestração chamando as funções genéricas de `modules/`.
