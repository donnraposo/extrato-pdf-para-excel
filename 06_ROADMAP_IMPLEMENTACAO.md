# 06 — Roadmap de Implementação

Este roadmap só poderá ser executado após aprovação explícita da arquitetura completa.

## Sprint 01 — Fundação e modelos

**Objetivo:** preparar projeto, modelos de domínio, configuração e qualidade básica.

**Arquivos/áreas:** configuração do projeto, domínio, testes unitários iniciais e documentação de execução.

**Dependências:** decisão final de versões e bibliotecas.

**Resultado esperado:** projeto executável em desenvolvimento e modelos independentes de PDF/UI.

## Sprint 02 — Extração espacial

**Objetivo:** transformar PDFs textuais em páginas, palavras e coordenadas.

**Arquivos/áreas:** `extraction`, fixtures anonimizadas e testes de integração.

**Dependências:** biblioteca PDF aprovada; amostra PDF real anonimizada.

**Resultado esperado:** visualização diagnóstica reproduzível das palavras extraídas por página.

## Sprint 03 — Detector de esquema genérico

**Objetivo:** detectar cabeçalhos, faixas de colunas, campos comuns e extras.

**Arquivos/áreas:** `layout`, aliases e testes sintéticos.

**Dependências:** saída estável da Sprint 02.

**Resultado esperado:** esquema detectado por página com evidências e confiança.

## Sprint 04 — Interpretador de lançamentos

**Objetivo:** reconstruir linhas e agrupar descrições multilinha, datas herdadas, documentos e valores.

**Arquivos/áreas:** interpretador, máquina de estados e normalização.

**Dependências:** esquema detectado; regras brasileiras de data/moeda.

**Resultado esperado:** lançamentos tipados, ainda sem interface ou Excel final.

## Sprint 05 — Santander e validação contábil

**Objetivo:** criar o primeiro adaptador e validar a amostra Santander.

**Arquivos/áreas:** adaptador Santander, regressões e validador.

**Dependências:** PDF original ou páginas anonimizadas no momento dos testes; resultado esperado manual.

**Resultado esperado:** sinais, agrupamentos e saldos associados conforme critérios do plano de testes.

## Sprint 06 — Exportação Excel

**Objetivo:** gerar `.xlsx` seguro e utilizável.

**Arquivos/áreas:** exportador e testes de leitura do arquivo gerado.

**Dependências:** modelo validado.

**Resultado esperado:** abas `Lançamentos`, `Conferência` e `Metadados`, tipos e filtros corretos.

## Sprint 07 — Interface Windows

**Objetivo:** criar tela de seleção, destino, progresso e resultado.

**Arquivos/áreas:** `ui` e orquestrador.

**Dependências:** pipeline funcional sem interface.

**Resultado esperado:** processamento completo sem terminal e sem congelamento perceptível da janela.

## Sprint 08 — Robustez e novos layouts

**Objetivo:** testar pelo menos um layout adicional e confirmar extensibilidade.

**Arquivos/áreas:** adaptadores/configurações, regressões e mensagens.

**Dependências:** amostra anonimizada de outro banco e Excel esperado.

**Resultado esperado:** campos extras dinâmicos e fallback genérico comprovados.

## Sprint 09 — Distribuição

**Objetivo:** gerar executável Windows e guia do usuário.

**Arquivos/áreas:** build, versão, README e artefato de distribuição.

**Dependências:** testes completos aprovados.

**Resultado esperado:** aplicação instalável ou portátil, com procedimento reproduzível de build.

## Fora do escopo inicial

- OCR para PDFs escaneados;
- processamento de múltiplos PDFs em lote;
- armazenamento em banco;
- integração com nuvem ou bancos;
- interpretação por serviços externos de IA;
- faturas de cartão.

Esses itens exigem nova análise de impacto e aprovação.
