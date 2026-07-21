# 11 — Histórico de Alterações

As datas registram decisões e mudanças conhecidas. Este arquivo não substitui histórico Git.

## 21/07/2026 — Baseline documental

- arquitetura revisada contra o código real;
- registrada migração parcial para Clean Architecture;
- criado documento central de estado;
- criados guias de novo layout e diagnóstico;
- formalizada matriz de requisitos e lacunas de teste;
- versão corrente confirmada como 0.1.0;
- suíte confirmada com 11 testes coletados.

## 20/07/2026 — Inter, Caixa e refatoração

- adicionados layouts Banco Inter e Caixa;
- criada estrutura de domínio, aplicação, portas, infraestrutura e layouts;
- criado registro ordenado de layouts;
- preservadas fachadas de compatibilidade;
- Caixa passou a suportar Data Efetiva, Valor assinado, saldo C/D e `SALDO DIA`;
- suíte ampliada para 11 testes.

## 17/07/2026 — Itaú e esquema dinâmico

- adicionado reconhecimento de Entradas, Saídas e Saldo;
- omitido Nº Documento no Excel Itaú;
- corrigida herança de datas;
- corrigida interferência de legendas laterais;
- adicionada identificação por assinatura estrutural;
- mantido Movimento calculado.

## 15/07/2026 — MVP Santander

- criados documentos iniciais de projeto;
- implementada interface Windows;
- implementada extração espacial com pdfplumber;
- implementado parser Santander;
- implementado Excel com três abas;
- separados Crédito e Débito e mantido Movimento;
- adicionados testes iniciais;
- configurado ambiente virtual e inicializador local.

## Convenção futura

Toda alteração deve registrar:

- data;
- comportamento alterado;
- layouts afetados;
- testes adicionados ou modificados;
- ADR relacionada;
- impacto de compatibilidade;
- aprovação quando exigida pelo protocolo.
