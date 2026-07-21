# 00 — Estado Atual do Projeto

> Documento de entrada e fonte principal de status para pessoas e agentes de IA.

## Controle do documento

| Campo | Valor |
|---|---|
| Projeto | Extrato Parser |
| Versão do pacote | 0.1.0 |
| Data da baseline | 21/07/2026 |
| Estado | MVP funcional em evolução |
| Plataforma | Windows, execução local |
| Linguagem | Python 3.12+; ambiente atual validado em Python 3.14.6 |
| Testes automatizados | 11 aprovados na baseline |
| Distribuição | código-fonte com ambiente virtual e inicializador `.bat`; executável ainda não empacotado |

## Resumo executivo

O sistema recebe um extrato bancário em PDF com texto selecionável, identifica o layout, extrai lançamentos e gera um arquivo Excel. Todo o processamento é local. A interface gráfica permite escolher um PDF e o destino do `.xlsx`.

Layouts específicos existentes:

1. Banco Inter;
2. Caixa;
3. Itaú;
4. Santander;
5. fallback genérico.

A arquitetura em camadas está implementada, mas a migração ainda é parcial. As abstrações, entidades, portas, caso de uso, registro e adaptadores existem; entretanto, algoritmos de parsing continuam concentrados em funções privadas de `parser.py`, e o adaptador Excel delega para `exporter.py`.

## O que está implementado

### Aplicação

- interface Tkinter;
- seleção de PDF e destino Excel;
- execução em thread para não bloquear a janela;
- comunicação por fila entre worker e interface;
- mensagens de sucesso e erro;
- inicializador `ABRIR_EXTRATO_PARSER.bat`.

### Entrada PDF

- leitura com `pdfplumber`;
- extração de palavras e coordenadas;
- agrupamento espacial em linhas físicas;
- processamento de múltiplas páginas;
- erro explícito para documento sem texto selecionável.

### Interpretação

- seleção de layout por `LayoutRegistry` e `LayoutDetector`;
- regras específicas para Santander, Itaú, Inter e Caixa;
- fallback genérico;
- datas brasileiras;
- moeda brasileira com `Decimal`;
- datas herdadas quando o layout permitir;
- descrições multilinha;
- campos e rótulos de saída definidos por layout;
- preservação de página, texto de origem, alertas e rejeições.

### Saída Excel

- `.xlsx` com `openpyxl`;
- abas `Lançamentos`, `Conferência` e `Metadados`;
- esquema dinâmico;
- datas e movimentos gravados como tipos nativos quando aplicável;
- filtros, cabeçalho formatado e painéis congelados;
- gravação temporária seguida de substituição do arquivo final.

## Matriz de layouts

| Layout | Estado | Campos principais | Particularidades | Teste automatizado |
|---|---|---|---|---|
| Santander | Implementado | Data, Descrição, Nº Documento, Crédito, Débito, Movimento, Saldo | descrições multilinha; sinal posterior; saldo por grupo | `test_parser.py` |
| Itaú | Implementado | Data, Descrição, Entradas, Saídas, Movimento, Saldo | datas agrupadas; legendas laterais; saldo anterior/final | `test_itau_parser.py` |
| Inter | Implementado | Data, Descrição, Crédito, Débito, Movimento, Saldo | datas por extenso; `R$`/`-R$`; fallback textual | `test_inter_parser.py` |
| Caixa | Implementado | Data, Data Efetiva, Documento, Histórico, Valor, Saldo | saldo textual C/D; `SALDO DIA`; data/hora | `test_caixa_parser.py` |
| Genérico | Parcial | campos reconhecidos por cabeçalho | conservador; não garante qualquer banco desconhecido | coberto indiretamente pelo Santander |

“Implementado” significa que existe código e teste sintético/de regressão. Não significa compatibilidade com todas as versões de extrato emitidas pelo banco.

## Estado por requisito

| ID | Requisito | Estado | Evidência principal |
|---|---|---|---|
| RF01 | Selecionar PDF por interface | Implementado | `app.py` |
| RF02 | Processar várias páginas | Implementado | leitor PDF e layouts |
| RF03 | Ler PDF textual | Implementado | `PdfPlumberStatementReader` |
| RF04 | Usar texto e coordenadas | Implementado | entidades `Word`/`PhysicalLine` |
| RF05 | Reconhecer aliases de campos | Parcial | regras por layout e parser genérico |
| RF06 | Produzir linha por lançamento | Implementado por layout homologado | testes bancários |
| RF07 | Unir descrições multilinha | Implementado por layout | Santander/Caixa |
| RF08 | Herdar datas | Implementado por layout | Itaú/Inter/Santander |
| RF09 | Manter ausências vazias | Implementado | domínio/exportador |
| RF10 | Separar crédito e débito | Implementado onde o esquema exige | Santander/Itaú/Inter |
| RF11 | Não inventar saldo | Implementado de forma conservadora | parsers e conferência |
| RF12 | Preservar qualquer coluna adicional | Parcial | modelo suporta extras; detecção universal não existe |
| RF13 | Um Excel por PDF | Implementado | caso de uso/exportador |
| RF14 | Três abas de saída | Implementado | exportador e testes |
| RF15 | Informar contagens e alertas | Implementado | interface/metadados |
| RF16 | Evoluir por adaptadores | Implementado estruturalmente | `StatementLayout`/registro |
| RF17 | Detectar quatro bancos | Implementado para assinaturas conhecidas | layouts registrados |
| RF18 | Esquema Caixa específico | Implementado | parser/testes Caixa |
| RF19 | Registro sem `if banco` no caso de uso | Implementado | aplicação/layouts |

## Testes da baseline

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Testes coletados:

- 1 Caixa;
- 3 exportação Excel;
- 3 Banco Inter;
- 1 Itaú;
- 2 normalização;
- 1 Santander.

Total: 11.

Cobertura não existente ou insuficiente:

- automação da interface Tkinter;
- PDF inválido, protegido e sem texto;
- falhas de permissão e sobrescrita;
- testes end-to-end versionados com PDFs anonimizados;
- chamadas de rede e privacidade verificadas automaticamente;
- cobertura quantitativa por linhas/branches;
- empacotamento Windows.

## Dívida técnica

### Alta prioridade

- mover `_parse_caixa_lines`, `_parse_inter_lines` e `_parse_generic_lines` de `parser.py` para seus layouts;
- remover dependência de layouts em funções privadas do módulo legado;
- mover a implementação completa do Excel para `infrastructure/excel`;
- criar testes end-to-end com fixtures PDF anonimizadas.

### Média prioridade

- estruturar códigos de alerta em vez de mensagens livres;
- definir política explícita de sobrescrita;
- criar logging seguro e opcional;
- medir cobertura de testes;
- formalizar versão de assinatura de cada layout;
- ampliar o detector de campos extras.

### Baixa prioridade/evolução

- empacotar executável com PyInstaller;
- OCR opcional;
- processamento em lote;
- relatório de reconciliação de saldos;
- internacionalização além do padrão brasileiro.

## Limitações vigentes

- somente PDF com texto selecionável;
- um PDF por execução;
- sem OCR;
- sem servidor, banco de dados ou nuvem;
- sem garantia universal para layout desconhecido;
- alterações de layout bancário podem exigir novo teste/adaptador;
- arquivo de saída deve ser conferido antes de uso contábil;
- PDFs reais sensíveis não devem ser versionados sem anonimização.

## Próximas ações recomendadas

1. concluir migração dos algoritmos legados para os pacotes de layout;
2. criar fixtures PDF anonimizadas para os quatro bancos;
3. aumentar testes de falha e integração;
4. definir política de sobrescrita e logs;
5. empacotar e homologar executável Windows;
6. somente depois ampliar para OCR ou novos bancos.

## Mapa documental

| Documento | Finalidade |
|---|---|
| `00_ESTADO_ATUAL.md` | status, baseline, riscos e próxima ação |
| `01_VISAO_DO_PROJETO.md` | objetivos, escopo e requisitos |
| `02_ANALISE_TECNICA.md` | tecnologias, alternativas e riscos |
| `03_ARQUITETURA_SISTEMA.md` | componentes, dependências e fluxo |
| `04_ESTRUTURA_PROJETO.md` | mapa físico do repositório |
| `05_MODELO_DADOS.md` | entidades, campos e regras de transformação |
| `06_ROADMAP_IMPLEMENTACAO.md` | entregas concluídas e pendentes |
| `07_PLANO_TESTES.md` | estratégia, cobertura e homologação |
| `08_DECISOES_ARQUITETURA.md` | ADRs e decisões aprovadas |
| `09_GUIA_NOVO_LAYOUT.md` | procedimento para suportar outro banco |
| `10_OPERACAO_E_DIAGNOSTICO.md` | uso, falhas e investigação |
| `11_CHANGELOG.md` | histórico cronológico |
| `MASTER_PROJECT_PROTOCOL.md` | governança e aprovações |

## Regra para agentes de IA

Antes de atuar:

1. ler `MASTER_PROJECT_PROTOCOL.md`;
2. ler este documento;
3. consultar a arquitetura e as ADRs;
4. comparar qualquer afirmação documental com o código e os testes;
5. tratar itens “parciais” como não concluídos;
6. não alterar arquitetura ou comportamento sem análise de impacto e aprovação;
7. adicionar teste de regressão para toda correção de layout.
