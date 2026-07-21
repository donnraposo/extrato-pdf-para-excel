# Extrato Parser

Aplicação desktop local para Windows que converte extratos bancários em PDF textual para Excel. Todo o processamento ocorre no computador do usuário, sem envio de dados bancários para serviços externos.

## Funcionalidades

- processa PDFs com uma ou várias páginas;
- extrai texto e coordenadas com `pdfplumber`;
- reconhece automaticamente o layout bancário;
- interpreta datas, documentos, históricos, valores e saldos;
- preserva descrições que ocupam várias linhas;
- gera Excel com as abas `Lançamentos`, `Conferência` e `Metadados`;
- mantém página e texto de origem para auditoria;
- sinaliza dados ambíguos para conferência;
- grava valores financeiros como números quando o layout permitir;
- funciona offline.

## Bancos e esquemas reconhecidos

### Santander

`Data | Descrição | Nº Documento | Crédito | Débito | Movimento | Saldo`

- Crédito e Débito são positivos em suas colunas;
- Movimento representa crédito positivo e débito negativo;
- detalhes em múltiplas linhas são incorporados ao lançamento.

### Itaú

`Data | Descrição | Entradas | Saídas | Movimento | Saldo`

- não cria a coluna Nº Documento quando ela não existe no extrato;
- Entradas são positivas;
- Saídas são positivas na coluna própria e negativas em Movimento.

### Banco Inter

`Data | Descrição | Crédito | Débito | Movimento | Saldo por transação`

- reconhece datas por extenso compartilhadas por vários lançamentos;
- interpreta `R$` como crédito e `-R$` como débito;
- associa o saldo apresentado a cada transação;
- ignora resumos e rodapés de atendimento.

### Caixa

`Data | Data Efetiva | Documento | Histórico | Valor | Saldo`

- Data Efetiva inclui data e horário, como `03/01/2026 03:43`;
- Valor é numérico: créditos positivos e débitos negativos;
- Saldo preserva o indicador do PDF no mesmo campo, como `531,74 C` ou `255,00 D`;
- linhas `SALDO DIA` aparecem na ordem original com Valor vazio;
- cabeçalhos repetidos e artefatos como `about:blank n/m` são ignorados;
- lançamentos fora do período declarado são preservados e enviados para conferência.

## Como usar

No Windows:

1. feche qualquer instância antiga da aplicação após uma atualização;
2. dê dois cliques em `ABRIR_EXTRATO_PARSER.bat`;
3. clique em **Selecionar PDF**;
4. escolha o destino do arquivo Excel;
5. clique em **Gerar Excel**;
6. revise a aba `Conferência`.

## Arquitetura

O projeto utiliza uma estrutura inspirada em Clean Architecture e princípios SOLID. A separação principal está implementada, mas a migração do parser e do exportador legados ainda é parcial:

- `application`: portas e caso de uso de conversão;
- `domain`: entidades independentes de PDF, Excel e interface;
- `infrastructure`: implementações com `pdfplumber` e `openpyxl`;
- `layouts`: detector, registro e classes especializadas por banco;
- uma classe pública por arquivo;
- novos bancos são adicionados pelo registro de layouts, sem alterar o caso de uso;
- fachadas mantêm compatibilidade com os pontos de entrada existentes.

O estado e a dívida técnica estão detalhados em `DOCS/00_ESTADO_ATUAL.md` e `DOCS/03_ARQUITETURA_SISTEMA.md`.

```text
Interface
   ↓
ConvertStatement
   ├── StatementReader      ← PdfPlumberStatementReader
   ├── StatementInterpreter ← LayoutStatementInterpreter
   └── StatementExporter    ← OpenpyxlStatementExporter
```

A documentação completa está em [`DOCS`](DOCS/). Para entender o andamento, comece por:

- [`00_ESTADO_ATUAL.md`](DOCS/00_ESTADO_ATUAL.md);
- [`01_VISAO_DO_PROJETO.md`](DOCS/01_VISAO_DO_PROJETO.md);
- [`03_ARQUITETURA_SISTEMA.md`](DOCS/03_ARQUITETURA_SISTEMA.md);
- [`08_DECISOES_ARQUITETURA.md`](DOCS/08_DECISOES_ARQUITETURA.md);
- [`09_GUIA_NOVO_LAYOUT.md`](DOCS/09_GUIA_NOVO_LAYOUT.md);
- [`10_OPERACAO_E_DIAGNOSTICO.md`](DOCS/10_OPERACAO_E_DIAGNOSTICO.md);
- [`11_CHANGELOG.md`](DOCS/11_CHANGELOG.md);
- [`MASTER_PROJECT_PROTOCOL.md`](DOCS/MASTER_PROJECT_PROTOCOL.md).

O estado oficial da baseline está em `00_ESTADO_ATUAL.md`. A arquitetura em camadas está funcional, mas a migração ainda possui código legado de compatibilidade documentado como dívida técnica.

## Desenvolvimento

Requisitos:

- Python 3.12 ou compatível;
- dependências definidas em `pyproject.toml`.

Executar os testes:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Executar a aplicação em desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m extrato_parser.app
```

O inicializador `run_app.pyw` configura o caminho de `src` para a abertura pelo arquivo `.bat`.

## Estado dos testes

A suíte atual possui 11 testes automatizados cobrindo:

- normalização de datas e moeda;
- agrupamento e sinais;
- exportação para Excel;
- Santander, Itaú, Inter e Caixa;
- Data Efetiva da Caixa;
- Valor assinado, saldo textual com `C/D` e `SALDO DIA`.

## Limitações

- PDFs compostos apenas por imagem ainda não possuem OCR;
- PDFs protegidos ou com codificação textual defeituosa podem não ser interpretados;
- mudanças de layout do banco podem exigir atualização do adaptador;
- PDFs reais com dados sensíveis não devem ser adicionados ao repositório sem anonimização;
- antes do uso contábil, compare o Excel com o PDF e verifique a aba `Conferência`.
