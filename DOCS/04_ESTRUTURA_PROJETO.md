# 04 — Estrutura do Projeto

> **Baseline:** 21/07/2026 | O mapa abaixo descreve arquivos versionados relevantes e omite `.venv`, caches e artefatos locais.

Estrutura implementada durante a refatoração incremental para SOLID/Clean Architecture. A organização física existe, mas a migração dos algoritmos legados ainda é parcial:

```text
extrato-parser/
├── DOCS/
│   ├── 00_ESTADO_ATUAL.md
│   ├── 01_VISAO_DO_PROJETO.md
│   ├── 02_ANALISE_TECNICA.md
│   ├── 03_ARQUITETURA_SISTEMA.md
│   ├── 04_ESTRUTURA_PROJETO.md
│   ├── 05_MODELO_DADOS.md
│   ├── 06_ROADMAP_IMPLEMENTACAO.md
│   ├── 07_PLANO_TESTES.md
│   ├── 08_DECISOES_ARQUITETURA.md
│   ├── 09_GUIA_NOVO_LAYOUT.md
│   ├── 10_OPERACAO_E_DIAGNOSTICO.md
│   ├── 11_CHANGELOG.md
│   └── MASTER_PROJECT_PROTOCOL.md
├── src/extrato_parser/
│   ├── application/
│   │   ├── ports/
│   │   │   ├── statement_reader.py
│   │   │   ├── statement_interpreter.py
│   │   │   └── statement_exporter.py
│   │   └── use_cases/convert_statement.py
│   ├── domain/entities/
│   │   ├── word.py
│   │   ├── physical_line.py
│   │   ├── statement_entry.py
│   │   └── parse_result.py
│   ├── infrastructure/
│   │   ├── pdf/
│   │   │   ├── pdf_text_error.py
│   │   │   ├── word_line_grouper.py
│   │   │   └── pdfplumber_statement_reader.py
│   │   └── excel/openpyxl_statement_exporter.py
│   ├── layouts/
│   │   ├── statement_layout.py
│   │   ├── layout_detector.py
│   │   ├── layout_registry.py
│   │   ├── layout_statement_interpreter.py
│   │   ├── generic/
│   │   ├── santander/
│   │   ├── itau/
│   │   ├── inter/
│   │   └── caixa/
│   ├── normalization.py
│   ├── app.py
│   ├── exporter.py
│   ├── extraction.py
│   ├── models.py
│   ├── parser.py
│   └── service.py
├── tests/
│   ├── test_parser.py
│   ├── test_itau_parser.py
│   ├── test_inter_parser.py
│   ├── test_caixa_parser.py
│   ├── test_exporter.py
│   └── test_normalization.py
├── ABRIR_EXTRATO_PARSER.bat
├── run_app.pyw
├── pyproject.toml
└── README.md
```

## Responsabilidades

- `application/ports`: contratos independentes para leitura, interpretação e exportação.
- `application/use_cases`: orquestração do objetivo do usuário.
- `domain/entities`: entidades sem dependência de PDF, Excel ou UI.
- `infrastructure/pdf`: integração exclusiva com pdfplumber e agrupamento físico.
- `infrastructure/excel`: implementação de exportação com openpyxl.
- `layouts`: contrato, detector, registro e layouts bancários.
- `normalization.py`: funções puras para texto, moeda e datas brasileiras.
- fachadas de compatibilidade: preservam imports e pontos de entrada anteriores.
- `tests`: regressões sintéticas e testes de exportação.
- `DOCS`: fonte oficial de arquitetura, decisões, modelo, roadmap e testes.

## Fachadas e código de transição

- `models.py` reexporta entidades do domínio;
- `extraction.py` mantém funções compatíveis de extração;
- `parser.py` ainda contém os algoritmos concretos dos layouts;
- `exporter.py` contém a geração concreta do workbook;
- `service.py` é o composition root usado pela interface.

Esses arquivos não devem ser removidos antes da migração dos algoritmos e da confirmação de todos os testes de regressão.

## Convenções obrigatórias

- uma classe pública por arquivo;
- nomes internos em inglês e interface/documentação em português;
- domínio não importa infraestrutura;
- caso de uso depende de portas;
- adaptadores são registrados explicitamente;
- arquivos bancários reais não entram no repositório sem anonimização;
- toda correção de layout inclui teste de regressão.
- o fallback genérico permanece por último no registro;
- um layout não importa Tkinter ou openpyxl;
- documentos de status usam `00_ESTADO_ATUAL.md` como referência temporal.
