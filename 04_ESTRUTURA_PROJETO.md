# 04 — Estrutura do Projeto

Estrutura proposta para a etapa de implementação:

```text
extrato-parser/
├── src/
│   └── extrato_parser/
│       ├── app.py
│       ├── ui/
│       ├── application/
│       ├── domain/
│       ├── extraction/
│       ├── layout/
│       │   └── adapters/
│       ├── normalization/
│       ├── validation/
│       ├── export/
│       └── config/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   └── fixtures/
├── docs/
├── scripts/
├── build/
├── pyproject.toml
├── README.md
└── .gitignore
```

Esta estrutura é proposta, não criada nesta fase.

## Responsabilidades

### `src/extrato_parser/ui`

Janela, seleção de arquivos, progresso e mensagens. Não contém regras bancárias.

### `application`

Casos de uso e orquestração do pipeline.

### `domain`

Modelos independentes de biblioteca: documento, página, esquema, lançamento, campo, alerta e resultado.

### `extraction`

Integração com leitores PDF e conversão para representação espacial neutra.

### `layout`

Detecção de tabelas, cabeçalhos, faixas e assinaturas.

### `layout/adapters`

Regras isoladas de bancos/layouts conhecidos. Nenhum adaptador deve alterar o comportamento global sem testes.

### `normalization`

Aliases, datas, moeda brasileira, documentos e campos extras.

### `validation`

Confiança, integridade, alertas e reconciliação de saldos quando aplicável.

### `export`

Geração segura do `.xlsx`, abas, estilos e metadados.

### `config`

Dicionários de aliases, limites padrão e configurações não sensíveis.

### `tests`

- `unit`: regras pequenas e determinísticas;
- `integration`: PDF até modelo e modelo até Excel;
- `regression`: layouts bancários anonimizados já suportados;
- `fixtures`: amostras sintéticas ou anonimizadas, nunca dados pessoais sem necessidade.

### `docs`

Arquitetura, decisões, guia do usuário e notas de formatos suportados.

### `scripts` e `build`

Automação controlada de qualidade e empacotamento. Artefatos gerados não devem ser misturados ao código-fonte.

## Convenções

- código e nomes internos sem acentos; interface e documentação em português;
- dependências apontam para o domínio, não da regra de negócio para a interface;
- biblioteca de PDF fica encapsulada;
- adaptadores são registrados explicitamente;
- nenhuma amostra real sensível entra no repositório sem anonimização.
