# 05 — Modelo de Dados

> **Baseline:** 21/07/2026 | Este documento descreve as classes efetivamente implementadas. Não existe banco de dados.

## Visão geral

```text
PDF
 └── Word[]
      └── PhysicalLine[]
           └── StatementLayout.parse(...)
                └── ParseResult
                     ├── StatementEntry[]
                     ├── rejected_lines[]
                     ├── metadata
                     └── definição dinâmica da saída
```

## Entidades implementadas

### `Word`

Representa uma palavra extraída do PDF.

| Campo | Tipo | Finalidade |
|---|---|---|
| `text` | `str` | texto original |
| `x0`, `x1` | `float` | limites horizontais |
| `top`, `bottom` | `float` | limites verticais |
| `page` | `int` | página iniciando em 1 |

### `PhysicalLine`

Representa palavras agrupadas por proximidade vertical.

| Campo | Tipo | Finalidade |
|---|---|---|
| `words` | `list[Word]` | palavras ordenadas horizontalmente |
| `page` | `int` | página de origem |
| `top` | `float` | posição vertical média |
| `text` | propriedade | texto reconstruído da linha |

### `StatementEntry`

Representa lançamento, linha informativa de saldo ou registro que exige revisão.

| Campo | Tipo | Regra |
|---|---|---|
| `transaction_date` | `date | None` | data contábil; herança depende do layout |
| `effective_date` | `date | datetime | None` | usado principalmente pela Caixa |
| `description` | `str` | descrição normalizada |
| `document_number` | `str | None` | texto; preserva zeros à esquerda |
| `credit` | `Decimal | None` | crédito positivo |
| `debit` | `Decimal | None` | débito positivo na coluna própria |
| `movement` | `Decimal | None` | crédito positivo ou débito negativo |
| `balance` | `Decimal | str | None` | decimal ou saldo textual Caixa com C/D |
| `page` | `int` | página de origem |
| `source_text` | `str` | evidência textual mínima |
| `extra_fields` | `dict[str, Any]` | campos adicionais |
| `warnings` | `list[str]` | motivos de revisão |
| `balance_only` | `bool` | linha de saldo sem movimento, como `SALDO DIA` |

`needs_review` é verdadeiro quando há alertas, data ausente ou movimento ausente em linha que não seja `balance_only`.

### `ParseResult`

| Campo | Tipo | Finalidade |
|---|---|---|
| `source` | `Path` | PDF de origem |
| `entries` | `list[StatementEntry]` | registros interpretados |
| `rejected_lines` | `list[tuple[int,str,str]]` | página, texto e motivo |
| `metadata` | `dict[str, Any]` | banco provável, páginas e contagens |
| `detected_extra_fields` | `list[str]` | ordem de campos adicionais |
| `output_fields` | `list[str]` | chaves e ordem do Excel |
| `field_labels` | `dict[str,str]` | rótulos exibidos por layout |

## Conceitos não implementados como entidades

`DocumentoFonte`, `PaginaFonte`, `EsquemaDetectado`, `CampoDetectado` e `Alerta` tipado foram considerados no planejamento inicial, mas não existem como classes na baseline. Suas responsabilidades estão distribuídas entre `ParseResult`, `PhysicalLine`, configurações dos layouts e mensagens em `warnings`.

## Invariantes

- moeda usa `Decimal` durante parsing;
- débito é positivo em `debit` e negativo em `movement`;
- crédito é positivo em `credit` e `movement`;
- identificadores não são convertidos para número;
- ausência é `None`, não texto vazio artificial;
- página e texto de origem acompanham cada registro;
- saldo só é associado quando o layout encontra evidência;
- linha `balance_only` pode ter movimento ausente sem ser erro.

## Esquemas por layout

| Layout | `output_fields` |
|---|---|
| Santander | `date, description, document, credit, debit, movement, balance` |
| Itaú | `date, description, credit, debit, movement, balance` |
| Inter | `date, description, credit, debit, movement, balance` |
| Caixa | `date, effective_date, document, description, movement, balance` |
| Genérico | definido conforme cabeçalhos reconhecidos |

## Projeção no Excel

### `Lançamentos`

Campos definidos pelo layout, depois campos extras, `Página de origem` e `Status`. Datas e moedas usam tipos nativos do Excel. Exceção aprovada: saldo Caixa permanece texto com C/D.

### `Conferência`

Página, tipo, texto original e motivo. Contém entradas com `needs_review` e linhas rejeitadas.

### `Metadados`

Arquivo de origem, horário de processamento e pares fornecidos pelo layout.

## Evolução recomendada

- criar tipos estáveis para código/severidade de alerta;
- introduzir objeto explícito de assinatura/versão do layout;
- separar saldo textual de saldo numérico sem quebrar a saída Caixa;
- formalizar esquema de campos extras;
- avaliar objeto `DocumentContext` apenas quando houver necessidade comprovada.
