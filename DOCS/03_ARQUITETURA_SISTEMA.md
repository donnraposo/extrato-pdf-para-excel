# 03 — Arquitetura do Sistema

## 1. Objetivo arquitetural

O Extrato Parser é uma aplicação desktop local para Windows que transforma extratos bancários em PDF textual em arquivos Excel estruturados. A arquitetura prioriza:

- isolamento das bibliotecas externas;
- suporte incremental a novos bancos;
- preservação dos layouts já homologados;
- rastreabilidade dos dados extraídos;
- processamento offline;
- falha segura para registros ambíguos.

A solução adota uma arquitetura em camadas inspirada em Clean Architecture, com portas para leitura, interpretação e exportação. A migração ainda é parcial: alguns layouts e adaptadores de infraestrutura delegam para funções compatíveis localizadas nos módulos legados `parser.py` e `exporter.py`.

## 2. Contexto do sistema

```text
┌─────────┐       ┌──────────────────────────┐       ┌──────────────┐
│ Usuário │──────▶│ Extrato Parser (desktop) │──────▶│ Arquivo XLSX │
└─────────┘       └──────────────────────────┘       └──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ PDF textual │
                     └─────────────┘
```

Não existem servidor, banco de dados, autenticação, fila ou API externa. O PDF é lido no computador do usuário e o resultado é gravado localmente.

## 3. Visão de componentes

```text
Application (Tkinter)
        │
        ▼
service.convert_statement  ─────────────── Composition Root
        │
        ▼
ConvertStatement                           Caso de uso
   │              │                  │
   ▼              ▼                  ▼
StatementReader  StatementInterpreter  StatementExporter       Portas
   ▲              ▲                  ▲
   │              │                  │
PdfPlumber      LayoutStatement     Openpyxl                    Adaptadores
StatementReader Interpreter         StatementExporter
                  │
                  ▼
             LayoutDetector
                  │
                  ▼
             LayoutRegistry
                  │
     ┌────────────┼────────────┬───────────┬────────────┐
     ▼            ▼            ▼           ▼            ▼
   Inter        Caixa        Itaú      Santander     Genérico
```

## 4. Camadas e responsabilidades

### 4.1 Apresentação

Implementada em `app.py` com Tkinter.

Responsabilidades:

- selecionar o PDF de entrada;
- selecionar o caminho do Excel;
- iniciar a conversão;
- manter a janela responsiva;
- apresentar progresso, sucesso e erro.

O processamento ocorre em uma thread daemon. A comunicação de volta para a thread da interface utiliza uma fila, consultada periodicamente pelo event loop do Tkinter. A interface não contém regras bancárias.

### 4.2 Aplicação

O caso de uso `ConvertStatement` coordena o fluxo sem importar `pdfplumber` ou `openpyxl`.

Responsabilidades:

1. validar extensão e existência do PDF;
2. solicitar a leitura por `StatementReader`;
3. solicitar a interpretação por `StatementInterpreter`;
4. impedir exportação silenciosa quando nenhum lançamento for reconhecido;
5. solicitar a gravação por `StatementExporter`;
6. devolver o `ParseResult` à interface.

### 4.3 Domínio

O domínio contém estruturas independentes das bibliotecas de entrada e saída:

- `Word`: palavra e coordenadas no PDF;
- `PhysicalLine`: palavras agrupadas em uma linha visual;
- `StatementEntry`: lançamento normalizado;
- `ParseResult`: resultado, esquema de saída, metadados e rejeições.

`StatementEntry` suporta:

- data do lançamento;
- data efetiva, quando existente;
- descrição;
- documento;
- crédito e débito separados;
- movimento assinado;
- saldo numérico ou textual;
- campos adicionais;
- página e texto de origem;
- alertas e registros exclusivos de saldo.

### 4.4 Infraestrutura

#### PDF

`PdfPlumberStatementReader` implementa `StatementReader` e converte o PDF em linhas físicas. A infraestrutura encapsula `pdfplumber`; os layouts recebem apenas entidades do domínio.

O agrupamento usa proximidade vertical e ordenação horizontal. PDF sem texto selecionável é rejeitado com mensagem específica. OCR não faz parte da versão atual.

#### Excel

`OpenpyxlStatementExporter` implementa `StatementExporter` e encapsula a geração de `.xlsx`.

O arquivo contém:

- `Lançamentos`: registros estruturados e esquema dinâmico;
- `Conferência`: lançamentos ou linhas que exigem revisão;
- `Metadados`: origem, banco provável, páginas, contagens e informações inferidas.

A gravação utiliza arquivo temporário seguido de substituição, reduzindo o risco de deixar uma saída parcial após falha.

### 4.5 Layouts bancários

`StatementLayout` define dois contratos:

- `matches(lines)`: decide se o layout reconhece o documento;
- `parse(lines, source, page_count)`: converte linhas físicas em `ParseResult`.

`LayoutDetector` percorre os layouts na ordem definida por `LayoutRegistry`. O primeiro `matches` verdadeiro vence. O layout genérico deve permanecer por último e atua como fallback.

Ordem atual:

1. Inter;
2. Caixa;
3. Itaú;
4. Santander;
5. Genérico.

A ordem é parte do comportamento do sistema. Uma assinatura excessivamente ampla em uma posição anterior pode capturar um PDF destinado a outro adaptador.

## 5. Estratégias por banco

| Layout | Assinatura principal | Particularidades | Esquema típico |
|---|---|---|---|
| Inter | textos e estrutura próprios do extrato Inter | data agrupada, valor assinado, saldo por transação | Data, Descrição, Crédito, Débito, Movimento, Saldo |
| Caixa | Documento, Histórico, Valor, Saldo, Data Efetiva e assinatura Caixa | data efetiva, valor assinado e saldo com marcador C/D | Data, Data Efetiva, Documento, Histórico, Valor, Saldo |
| Itaú | identificação textual ou combinação Entradas/Saídas/Saldo | data herdada por grupo, saldo anterior/final e legendas laterais | Data, Descrição, Entradas, Saídas, Movimento, Saldo |
| Santander | assinatura e cabeçalho espacial Santander | documento, descrições multilinha, créditos e débitos separados | Data, Descrição, Nº Documento, Crédito, Débito, Movimento, Saldo |
| Genérico | fallback | inferência conservadora por cabeçalho e coordenadas | depende dos campos reconhecidos |

## 6. Detecção e interpretação

O detector apenas escolhe um `StatementLayout`. Remoção de cabeçalhos, rodapés, legendas, agrupamento de descrições e regras de datas pertencem ao layout selecionado.

Pipeline de interpretação:

1. normalizar texto para comparação, preservando o original;
2. identificar assinatura e cabeçalhos;
3. delimitar regiões e colunas por coordenadas;
4. descartar elementos não transacionais;
5. agrupar linhas físicas em lançamentos lógicos;
6. herdar datas somente quando a estrutura do banco permitir;
7. interpretar moeda brasileira com `Decimal`;
8. produzir crédito/débito e movimento assinado;
9. associar saldo somente com evidência suficiente;
10. registrar alertas e texto de origem.

## 7. Esquema dinâmico de saída

O modelo interno é normalizado, mas o Excel respeita os campos reconhecidos no documento.

`ParseResult.output_fields` define quais campos serão exportados e em qual ordem. `ParseResult.field_labels` define os nomes apresentados ao usuário. Campos adicionais são transportados em `extra_fields` e `detected_extra_fields`.

Regras financeiras:

- crédito/entrada é positivo;
- débito/saída é armazenado como positivo em sua coluna própria;
- movimento é positivo para crédito e negativo para débito;
- saldo não é repetido ou inventado quando o PDF não o associa ao lançamento;
- documento é texto para preservar zeros à esquerda.

## 8. Fluxo de execução

```text
Selecionar PDF
    │
    ▼
Validar caminhos
    │
    ▼
Extrair palavras e coordenadas
    │
    ▼
Agrupar linhas físicas
    │
    ▼
Detectar layout por registro ordenado
    │
    ▼
Interpretar e normalizar lançamentos
    │
    ├── registros confiáveis ──▶ Lançamentos
    └── ambiguidades/rejeições ▶ Conferência
    │
    ▼
Gerar Metadados
    │
    ▼
Gravar XLSX temporário e concluir saída
```

## 9. Tratamento de erros e observabilidade

Falhas esperadas incluem:

- arquivo inexistente ou extensão incorreta;
- PDF protegido, inválido ou sem texto;
- cabeçalho não reconhecido;
- ausência de lançamentos;
- valor, data ou saldo ambíguo;
- falha ao gravar o Excel.

Erros impeditivos interrompem a conversão e são apresentados na interface. Ambiguidades recuperáveis são registradas em `warnings`, `rejected_lines` e na aba `Conferência`.

Não há subsistema de logs persistentes estruturados nesta versão. A rastreabilidade operacional depende de página, texto de origem, metadados e alertas registrados no Excel.

## 10. Segurança e privacidade

- processamento offline;
- nenhuma chamada de rede no pipeline;
- nenhum banco de dados;
- nenhum upload automático;
- conteúdo integral do extrato não deve ser gravado em logs;
- arquivos temporários devem ser removidos após sucesso ou falha;
- saída existente não deve ser substituída sem decisão explícita do usuário.

## 11. Extensibilidade

Para adicionar um banco:

1. criar um pacote em `layouts/<banco>`;
2. implementar `StatementLayout`;
3. criar uma assinatura específica e conservadora em `matches`;
4. implementar a interpretação sem depender da interface;
5. registrar o layout antes do fallback genérico;
6. adicionar fixtures anonimizadas e testes de regressão;
7. documentar campos, limites e variações conhecidas.

Um novo layout não deve introduzir condicionais por banco no caso de uso, na interface ou no exportador.

## 12. Regras de dependência

- apresentação depende da fachada de aplicação;
- aplicação depende apenas do domínio e das portas;
- infraestrutura implementa portas da aplicação;
- layouts dependem do domínio e de utilitários de normalização;
- domínio não depende de Tkinter, pdfplumber ou openpyxl;
- composição das implementações concretas ocorre na fachada `service.py`;
- o fallback genérico permanece o último item do registro.

## 13. Dívida técnica conhecida

A separação arquitetural está funcional, mas ainda existe uma camada de compatibilidade:

- layouts específicos delegam parte do parsing para funções privadas de `parser.py`;
- o adaptador Excel delega para `exporter.py`;
- fachadas antigas (`models.py`, `extraction.py`, `parser.py` e `service.py`) preservam compatibilidade.

Evolução recomendada:

1. mover cada algoritmo de parsing para o pacote do respectivo layout;
2. mover a implementação completa do Excel para o adaptador de infraestrutura;
3. eliminar dependências de funções privadas entre módulos;
4. manter fachadas finas apenas quando houver consumidores externos;
5. remover código legado somente após testes de regressão de todos os bancos.

## 14. Restrições atuais

- somente PDFs com texto selecionável;
- um PDF por execução;
- execução local e de usuário único;
- layouts desconhecidos podem exigir novo adaptador;
- processamento em thread, não em processo isolado;
- ausência de banco, API, fila, telemetria e OCR.

## 15. Critérios arquiteturais de qualidade

- todos os layouts existentes devem continuar passando seus testes de regressão;
- nenhuma regra bancária deve entrar no caso de uso ou na interface;
- o layout genérico não pode preceder adaptadores específicos;
- valores monetários usam `Decimal` durante a interpretação;
- registros ambíguos não podem ser descartados silenciosamente;
- o Excel deve manter tipos de data e número, não apenas texto formatado;
- toda nova variação real deve produzir fixture anonimizada e teste correspondente.
