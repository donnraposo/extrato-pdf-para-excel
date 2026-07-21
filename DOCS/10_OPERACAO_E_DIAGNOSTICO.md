# 10 — Operação e Diagnóstico

## Execução normal

1. Fechar instâncias antigas da aplicação.
2. Abrir `ABRIR_EXTRATO_PARSER.bat`.
3. Selecionar um PDF textual.
4. Escolher um nome de saída `.xlsx`.
5. Gerar o Excel.
6. Revisar `Conferência` e `Metadados`.

## Execução de desenvolvimento

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m extrato_parser.app
```

O projeto usa layout `src`. `run_app.pyw` inclui `src` no caminho ao ser iniciado pelo `.bat`.

## Como validar uma conversão

- confirmar banco provável em `Metadados`;
- conferir quantidade de páginas;
- comparar primeira e última transação;
- conferir todas as mudanças de data;
- comparar totais de créditos e débitos;
- confirmar sinais de Movimento/Valor;
- conferir saldos onde existirem;
- revisar todas as linhas de `Conferência`;
- verificar descrições vazias e datas ausentes;
- confirmar que cabeçalhos e rodapés não viraram lançamentos.

## Diagnóstico por sintoma

### Banco provável incorreto

Possível causa: assinatura ausente, genérica ou capturada por layout anterior.

Verificar:

- textos das primeiras linhas extraídas;
- `matches` de cada layout;
- ordem do `LayoutRegistry`;
- teste de falso positivo.

### Datas vazias

Possíveis causas:

- ano/período não inferido;
- data caiu em coluna errada;
- cabeçalho delimitou incorretamente as faixas;
- formato de data ainda não suportado.

### Descrições vazias ou deslocadas

Possíveis causas:

- coordenada do início da descrição incorreta;
- legenda lateral interpretada como coluna;
- descrição posterior ao valor associada ao lançamento seguinte;
- agrupamento vertical inadequado.

### Crédito classificado como débito

Possíveis causas:

- posições de cabeçalho sobrescritas por legenda;
- coluna única com sinal não interpretado;
- limites horizontais incorretos.

### Linhas extras no final

Possível causa: o layout não reconheceu o marcador de fim da região transacional, como `Saldo final`, resumo ou rodapé.

### Nenhum lançamento identificado

Verificar:

- se o PDF possui texto selecionável;
- se está protegido;
- se o cabeçalho foi extraído;
- se o layout correto foi selecionado;
- motivos em `rejected_lines`.

### Erro ao salvar Excel

Verificar:

- arquivo aberto no Excel;
- permissão da pasta;
- nome/caminho válido;
- espaço em disco;
- existência de arquivo temporário após falha.

## Evidências para reportar um erro

Preferir:

- banco e período;
- página afetada;
- print anonimizado;
- linhas esperadas e obtidas;
- Excel gerado;
- quantidade mostrada em `Metadados`;
- mensagens da aba `Conferência`.

O PDF original é o melhor artefato para problemas de coordenadas. Se houver dados sensíveis, usar uma cópia anonimizada que preserve posições e fontes.

## Segurança operacional

- não enviar extratos reais para serviços não autorizados;
- não versionar PDFs ou Excels sensíveis;
- não registrar texto integral do extrato em logs;
- manter dependências atualizadas somente após testes;
- não sobrescrever resultados homologados durante diagnóstico;
- gerar arquivo corrigido com novo nome.

## Recuperação

A aplicação não mantém banco ou estado interno. Em caso de falha:

1. fechar a aplicação;
2. preservar PDF e Excel parcial para diagnóstico;
3. remover apenas temporários confirmados;
4. executar testes;
5. corrigir com regressão;
6. gerar novo Excel sem substituir o anterior;
7. comparar com o gabarito.
