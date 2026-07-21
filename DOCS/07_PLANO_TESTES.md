# 07 — Plano de Testes

> **Baseline:** 21/07/2026 | 11 testes automatizados coletados e aprovados.

## Objetivo

Evitar perda silenciosa, troca de sinal, associação incorreta de data/saldo e regressão de layouts homologados.

## Pirâmide atual

| Nível | Existente | Lacuna |
|---|---:|---|
| Funções de normalização | 2 | mais formatos inválidos e limites |
| Parser/layout | 6 | detecção isolada, falsos positivos e variações |
| Exportação Excel | 3 | erros de I/O e workbook completo |
| End-to-end com PDF | 0 versionado | necessário |
| Interface | 0 automatizado | necessário antes da distribuição |
| Segurança/privacidade | 0 automatizado | necessário |

## Inventário dos testes

### `test_normalization.py`

- crédito e débito em moeda brasileira;
- data curta usando ano padrão e data inválida.

### `test_parser.py`

- Santander com descrição multilinha, documento, crédito, débito, saldo e detalhes posteriores.

### `test_itau_parser.py`

- cabeçalho dinâmico;
- datas agrupadas;
- Entradas/Saídas;
- legenda lateral;
- saldo anterior e saldo final;
- esquema sem documento.

### `test_inter_parser.py`

- datas agrupadas e valores assinados;
- fallback textual quando coordenadas são inadequadas;
- amostra sintética completa.

### `test_caixa_parser.py`

- cabeçalho dividido;
- Data Efetiva;
- descrição multilinha;
- sinais e saldo C/D;
- `SALDO DIA`;
- cabeçalho repetido e artefatos de página.

### `test_exporter.py`

- três abas e valor numérico;
- esquema dinâmico Itaú;
- Data Efetiva Caixa.

## Regras obrigatórias

- moeda é comparada como `Decimal` no parser;
- correção de banco exige regressão específica;
- teste não deve depender de internet;
- fixture sensível deve ser anonimizada;
- texto não reconhecido não pode desaparecer;
- teste de layout deve validar primeira, intermediária e última transação quando possível;
- suíte completa deve rodar após qualquer alteração.

## Critérios por domínio

### Datas

- formato completo e curto;
- ano inferido do período;
- virada de ano;
- data herdada;
- data inválida;
- Data Efetiva com horário.

### Valores

- milhar e centavos brasileiros;
- zero;
- sinal anterior e posterior;
- crédito/débito separados;
- valor assinado;
- saldo decimal;
- saldo textual C/D.

### Estrutura

- cabeçalho simples e dividido;
- cabeçalho repetido;
- rodapé;
- mudança de página;
- descrição multilinha;
- documento ausente e com zeros;
- saldo anterior/final/diário;
- campos dinâmicos.

## Testes planejados ainda não implementados

### Unidade

- ordem e fallback do `LayoutRegistry`;
- falsos positivos de `matches`;
- propriedade `needs_review`;
- agrupador de linhas em tolerâncias-limite;
- códigos de alerta, após tipagem.

### Integração

- PDF textual mínimo → Excel;
- PDF vazio, inválido, protegido e sem texto;
- falha de destino sem permissão;
- saída já existente;
- limpeza de temporário após falha;
- tipos e formatos de todas as colunas.

### Interface

- cancelar seletores;
- impedir execução duplicada;
- manter responsividade;
- mostrar mensagem de erro;
- reabilitar botão após conclusão/falha.

### Segurança

- ausência de rede;
- ausência de extrato integral em logs;
- caminhos malformados;
- arquivos sensíveis fora do controle de versão.

## Homologação por banco

Para cada layout:

1. preparar gabarito manual anonimizado;
2. comparar quantidade e ordem;
3. comparar datas e descrições;
4. comparar documentos;
5. comparar valores e sinais;
6. comparar saldos;
7. revisar conferência;
8. validar esquema Excel;
9. registrar variação e data;
10. obter aprovação do usuário.

## Critérios de aprovação

- todas as páginas visitadas;
- nenhum lançamento descartado silenciosamente;
- 100% de sinais corretos nos valores aceitos;
- tipos Excel corretos, exceto exceção documental Caixa;
- cabeçalhos/rodapés ausentes dos lançamentos;
- ambiguidades visíveis em `Conferência`;
- suíte completa aprovada;
- comparação manual sem divergência crítica.

## Comandos

```powershell
# suíte completa
.\.venv\Scripts\python.exe -m pytest

# inventário detalhado
.\.venv\Scripts\python.exe -m pytest --collect-only -vv

# arquivo específico
.\.venv\Scripts\python.exe -m pytest tests\test_itau_parser.py
```

## Evidência da baseline

Ambiente: Windows, Python 3.14.6, pytest 9.1.1. Total: 11 testes. PDFs reais permanecem fora do repositório; portanto, as afirmações de validação real são históricas/documentais e não reproduzíveis automaticamente na baseline.
