# 06 — Roadmap de Implementação

> **Baseline:** 21/07/2026 | **Versão:** 0.1.0.

## Legenda

- **Concluído:** implementado e coberto por ao menos um teste relevante.
- **Parcial:** utilizável, mas incompleto ou sem cobertura suficiente.
- **Pendente:** ainda não implementado.
- **Bloqueado:** depende de decisão, amostra ou autorização externa.

## Resumo

| Entrega | Estado | Observação |
|---|---|---|
| Fundação Python | Concluído | pacote `src`, ambiente virtual e dependências |
| Extração PDF textual | Concluído | pdfplumber e coordenadas |
| Parser Santander | Concluído | regressão sintética |
| Parser Itaú | Concluído | regressão sintética e correções com PDF real |
| Parser Inter | Concluído | três testes |
| Parser Caixa | Concluído | esquema específico e teste |
| Fallback genérico | Parcial | não garante campos extras universais |
| Excel dinâmico | Concluído | três testes de exportação |
| Interface Windows | Concluído | teste manual; sem automação UI |
| Clean Architecture | Parcial | estrutura pronta; parsing/exportação ainda legados |
| Testes end-to-end com PDFs | Pendente | dados reais não versionados |
| Executável Windows | Pendente | PyInstaller não configurado |
| OCR | Fora do escopo atual | exige nova decisão |

## Fase A — MVP funcional

**Estado:** concluída.

Entregas:

- modelos básicos;
- normalização brasileira;
- extração espacial;
- Santander;
- exportação Excel;
- interface Tkinter;
- inicializador local.

## Fase B — Esquema dinâmico e novos bancos

**Estado:** concluída para assinaturas conhecidas; parcial para universalidade.

Entregas:

- Itaú com Entradas/Saídas;
- Inter com datas por extenso e saldo por transação;
- Caixa com Data Efetiva, Valor, saldo C/D e `SALDO DIA`;
- definição de `output_fields` e `field_labels`.

Pendente:

- formalizar campos extras arbitrários;
- testar variações adicionais de cada banco;
- versionar assinaturas.

## Fase C — Refatoração arquitetural

**Estado:** parcial.

Concluído:

- domínio;
- portas;
- caso de uso;
- leitor PDF de infraestrutura;
- exportador de infraestrutura;
- contrato, detector e registro de layouts;
- composition root em `service.py`;
- fachadas de compatibilidade.

Pendente:

1. mover parsers concretos para cada pacote de layout;
2. eliminar imports de funções privadas do módulo legado;
3. mover implementação completa do workbook para infraestrutura;
4. reduzir fachadas a reexportações ou removê-las com migração controlada;
5. adicionar testes unitários do detector/registro.

## Fase D — Qualidade e homologação

**Estado:** parcial.

Concluído:

- 11 testes automatizados;
- regressões sintéticas dos quatro bancos;
- testes básicos do Excel e normalização;
- conferência explícita para ambiguidades.

Pendente:

- fixtures PDF anonimizadas;
- testes end-to-end;
- cobertura automatizada;
- testes de arquivos inválidos/protegidos;
- testes de permissão e sobrescrita;
- testes de interface;
- matriz de gabaritos versionada;
- reconciliação de totais e saldos quando possível.

## Fase E — Distribuição Windows

**Estado:** pendente.

Plano:

1. escolher modo portátil ou instalador;
2. configurar PyInstaller;
3. incluir dependências de PDF;
4. testar em máquina Windows limpa;
5. documentar atualização e desinstalação;
6. avaliar falso positivo de antivírus;
7. versionar artefato e checksum;
8. homologar com os quatro bancos.

## Backlog futuro sujeito a nova aprovação

- OCR;
- processamento de vários PDFs;
- importação de faturas;
- CLI formal;
- regras configuráveis sem código;
- dashboard de reconciliação;
- banco de dados;
- serviços externos;
- atualizações automáticas.

## Próxima entrega recomendada

Concluir a Fase C antes de ampliar o número de bancos. O objetivo é remover dependências privadas do módulo legado mantendo os 11 testes e adicionando testes do detector e do caso de uso.

## Critério de atualização deste roadmap

Uma entrega muda para **Concluído** somente quando:

- código existe;
- teste proporcional ao risco passa;
- documentação foi atualizada;
- não existe divergência crítica conhecida;
- aprovação foi obtida quando exigida.
