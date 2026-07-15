# 05 — Modelo de Dados

Não haverá banco de dados na primeira versão. Este documento define o modelo lógico em memória e sua projeção no Excel.

## Entidades

### DocumentoFonte

| Campo | Tipo | Regra |
|---|---|---|
| id | texto | identificador interno da execução |
| nome_arquivo | texto | nome, sem necessidade de caminho completo no Excel |
| quantidade_paginas | inteiro | maior que zero |
| banco_detectado | texto opcional | pode ser `Desconhecido` |
| layout_detectado | texto opcional | versão/assinatura quando conhecida |
| periodo_inicial | data opcional | se identificado |
| periodo_final | data opcional | se identificado |
| processado_em | data/hora | momento local |

### PaginaFonte

| Campo | Tipo | Regra |
|---|---|---|
| numero | inteiro | inicia em 1 |
| largura/altura | decimal | sistema de coordenadas do PDF |
| possui_texto | booleano | alerta possível quando falso |
| palavras | coleção | texto e coordenadas |

### EsquemaDetectado

| Campo | Tipo | Regra |
|---|---|---|
| pagina_inicial/final | inteiro | região de validade |
| campos | coleção de CampoDetectado | inclui comuns e extras |
| confianca | decimal | evidência estrutural |

### CampoDetectado

| Campo | Tipo | Regra |
|---|---|---|
| nome_original | texto | cabeçalho do PDF |
| nome_saida | texto | nome único no Excel |
| tipo | enum | data, texto, moeda, número ou desconhecido |
| papel | enum | comum, crédito, débito, saldo ou extra |
| faixa_x | intervalo | limites horizontais aproximados |

### Lancamento

| Campo | Tipo | Regra |
|---|---|---|
| id | texto | único na execução |
| data | data opcional | pode ser herdada com evidência |
| descricao | texto | concatenação controlada de linhas |
| numero_documento | texto opcional | preservar zeros à esquerda |
| credito | decimal opcional | valor positivo; vazio em débito |
| debito | decimal opcional | valor positivo; vazio em crédito |
| movimento | decimal opcional | crédito positivo, débito negativo |
| saldo | decimal opcional | apenas com associação confiável |
| campos_extras | mapa | nome de saída → valor |
| pagina_origem | inteiro | rastreabilidade |
| texto_origem | texto | conteúdo mínimo necessário à conferência |
| confianca | decimal | resultado das evidências |
| status | enum | aceito ou conferir |

### Alerta

| Campo | Tipo | Regra |
|---|---|---|
| codigo | texto | estável para testes |
| severidade | enum | informação, aviso ou erro |
| mensagem | texto | legível ao usuário |
| pagina | inteiro opcional | origem |
| lancamento_id | texto opcional | vínculo quando existir |

## Relacionamentos

```text
DocumentoFonte 1 --- N PaginaFonte
DocumentoFonte 1 --- N EsquemaDetectado
DocumentoFonte 1 --- N Lancamento
Lancamento     1 --- N Alerta
Lancamento     1 --- N campos_extras (mapa dinâmico)
```

## Regras de transformação

### Datas

- interpretar formatos brasileiros;
- preservar ano inferido somente quando o período do documento oferecer evidência;
- gravar como data real no Excel, formatada como `dd/mm/aaaa`.

### Valores monetários

- interpretar ponto como separador de milhar e vírgula como decimal;
- interpretar marcador posterior `-` como débito quando o layout confirmar essa semântica;
- usar decimal durante cálculos;
- gravar número real no Excel, não texto formatado.

### Documento

- tratar como texto;
- `-` isolado equivale a ausente;
- não remover zeros à esquerda.

### Descrição

- unir linhas pertencentes ao mesmo lançamento com espaço;
- não incorporar cabeçalhos, rodapés ou valores de outras colunas;
- detalhes como parcela/período podem permanecer na descrição, salvo se detectados como campo extra explícito.

### Campos extras

- nomes duplicados recebem desambiguação previsível;
- ordem segue a aparição estável no documento;
- ausência em determinado lançamento gera célula vazia;
- tipos são inferidos conservadoramente.

## Modelo das abas

### `Lançamentos`

Campos comuns, campos extras, `Página de origem` e, se aprovado na implementação, indicador de alerta. A ordem dos lançamentos segue a ordem do PDF.

### `Conferência`

Página, texto de origem, valores interpretados, alertas e motivo da baixa confiança.

### `Metadados`

Dados do documento, esquema detectado, contagens, período, saldo inicial/final quando identificados e resumo dos alertas.
