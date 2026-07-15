# 03 — Arquitetura do Sistema

## Visão geral

A aplicação será desktop, local e dividida em camadas. A interface apenas coleta caminhos e apresenta progresso. O motor executa extração, reconhecimento, normalização e validação sem depender da interface.

```text
Usuário
   |
Interface desktop (seleção e progresso)
   |
Orquestrador de processamento
   |
   +--> Leitor de PDF --> páginas, palavras e coordenadas
   |
   +--> Detector de layout --> tabelas, cabeçalhos e faixas
   |
   +--> Interpretador --> linhas físicas e lançamentos lógicos
   |         |
   |         +--> Núcleo genérico
   |         +--> Adaptador do banco, quando reconhecido
   |
   +--> Normalizador --> campos comuns, extras, datas e valores
   |
   +--> Validador --> alertas, confiança e reconciliação possível
   |
   +--> Exportador Excel --> Lançamentos, Conferência, Metadados
```

## Componentes

### Interface desktop

- selecionar PDF;
- selecionar destino;
- iniciar processamento;
- mostrar progresso por página;
- mostrar resultado e alertas compreensíveis.

### Orquestrador

Controla o fluxo, agrega métricas e impede que falhas parciais sejam silenciosas.

### Leitor de PDF

Produz uma representação neutra: página, texto, posição horizontal, posição vertical e dimensões. Também informa se uma página não possui texto suficiente, indicando possível imagem.

### Detector de layout

- remove regiões repetitivas de cabeçalho e rodapé;
- encontra cabeçalhos tabulares;
- delimita faixas horizontais de colunas;
- detecta mudanças de esquema entre páginas;
- cria nomes para campos extras.

### Identificador de banco/layout

Calcula uma assinatura usando textos institucionais, nomes de campos e padrões. A identificação nunca é obrigatória: sem correspondência, o núcleo genérico continua.

### Interpretador genérico

Reconstrói linhas por proximidade vertical, associa palavras às faixas das colunas e usa uma máquina de estados para unir descrições multilinha e herdar datas.

### Adaptadores

Um adaptador pode ajustar:

- assinatura do layout;
- regiões ignoradas;
- aliases de cabeçalho;
- regras de continuidade;
- marcação de crédito/débito;
- validações específicas.

O adaptador Santander será o primeiro candidato, com base na amostra fornecida.

### Normalizador

- converte datas brasileiras em valores de data;
- usa `Decimal` para moeda durante o processamento;
- converte crédito/débito em movimento assinado;
- limpa documento ausente;
- mantém valor bruto para auditoria;
- ordena campos comuns antes dos extras.

### Validador

Gera alertas por lançamento e por documento. Não corrige silenciosamente valores ambíguos. Reconciliação de saldo será usada apenas quando a semântica do extrato permitir.

### Exportador Excel

Cria:

- `Lançamentos`: dados aprovados estruturalmente;
- `Conferência`: registros ambíguos, texto bruto, página e motivo;
- `Metadados`: arquivo, banco/layout provável, período, páginas, contagens e avisos.

## Fluxo da informação

1. usuário seleciona o PDF e destino;
2. sistema valida extensão e acesso;
3. leitor extrai palavras por página;
4. detector identifica regiões e esquemas;
5. interpretador monta lançamentos;
6. normalizador cria o esquema de saída;
7. validador classifica registros e alertas;
8. exportador grava um arquivo temporário;
9. após sucesso, o arquivo final é concluído;
10. interface apresenta o resumo.

## Modelo interno do lançamento

Cada registro conterá, no mínimo:

- campos normalizados;
- dicionário de campos extras;
- página de origem;
- linhas/texto de origem;
- identificador do layout;
- alertas;
- evidências de interpretação.

## Persistência e banco de dados

Não haverá banco de dados na primeira versão. Configurações e regras serão arquivos versionados da aplicação. O Excel é o artefato final. Essa decisão reduz exposição de dados e complexidade operacional.

## Autenticação, APIs, filas e rede

- autenticação: não aplicável para usuário local único;
- APIs externas: nenhuma;
- filas: nenhuma;
- rede: não necessária;
- processamento: síncrono em processo separado ou tarefa controlada para manter a interface responsiva.

## Segurança e privacidade

- processamento offline;
- nenhum upload automático;
- logs sem conteúdo bancário integral;
- arquivos temporários limitados e removidos ao final;
- mensagens de erro sem dados excessivos;
- não sobrescrever saída existente sem confirmação.

## Estratégia de evolução

1. núcleo genérico e amostra Santander;
2. novos layouts adicionados por testes e adaptadores;
3. configurações declarativas para variações simples;
4. OCR somente como módulo opcional futuro;
5. eventual processamento em lote sem alterar o pipeline central.
