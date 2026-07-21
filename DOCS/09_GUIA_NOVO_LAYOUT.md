# 09 — Guia para Implementar um Novo Layout Bancário

## Objetivo

Adicionar suporte a um banco ou variação de extrato sem introduzir regras bancárias na interface, no caso de uso ou no exportador.

## Pré-condições

- aprovação explícita da mudança;
- PDF textual anonimizado ou amostra sintética equivalente;
- resultado esperado revisado manualmente;
- entendimento dos cabeçalhos, sinais, datas, saldos e quebras de página.

## Análise obrigatória

Documentar antes do código:

- assinatura que distingue o layout;
- páginas/regiões transacionais;
- cabeçalhos e aliases;
- campos obrigatórios e opcionais;
- semântica de crédito, débito, movimento e saldo;
- regra de herança de data;
- descrições multilinha;
- saldos iniciais, finais e diários;
- cabeçalhos, rodapés e textos ignorados;
- condições de ambiguidade;
- esquema esperado no Excel.

## Implementação

1. Criar `src/extrato_parser/layouts/<banco>/`.
2. Criar uma classe que implemente `StatementLayout`.
3. Implementar `matches(lines)` com assinatura específica.
4. Implementar `parse(lines, source, page_count)`.
5. Preencher `ParseResult.metadata`, `output_fields` e `field_labels`.
6. Produzir `StatementEntry` com página e texto de origem.
7. Registrar ambiguidades em `warnings` ou `rejected_lines`.
8. Registrar a classe em `LayoutRegistry` antes do fallback genérico.
9. Atualizar matriz de layouts, roadmap, testes, ADRs e changelog.

## Regras para `matches`

- evitar apenas o nome do banco, pois logotipos podem não ser texto;
- combinar dois ou mais sinais estruturais quando possível;
- não aceitar assinatura comum a vários bancos;
- testar falsos positivos contra layouts já registrados;
- considerar a ordem do registro como parte do comportamento.

## Regras para `parse`

- usar `Decimal` para moeda;
- nunca usar `float` durante a interpretação;
- não inventar data, documento ou saldo;
- herdar data apenas quando o layout comprovar agrupamento;
- preservar zeros à esquerda em identificadores;
- não descartar linha silenciosamente;
- impedir cabeçalhos e rodapés de virarem lançamentos;
- manter a ordem original do PDF;
- registrar campos ausentes como `None`;
- diferenciar linha de saldo de movimento financeiro.

## Esquema de saída

Chaves internas disponíveis:

- `date`;
- `effective_date`;
- `description`;
- `document`;
- `credit`;
- `debit`;
- `movement`;
- `balance`.

O layout define a ordem por `output_fields` e os títulos por `field_labels`. Campos incomuns usam `extra_fields` e devem ser declarados em `detected_extra_fields`.

## Testes mínimos

- assinatura positiva;
- assinatura negativa contra pelo menos um layout existente;
- primeira e última transação;
- data completa e data herdada, se aplicável;
- crédito e débito;
- separadores brasileiros;
- descrição multilinha;
- documento ausente e com zero à esquerda;
- cabeçalho repetido;
- quebra de página;
- saldo inicial/final/diário;
- linha ambígua enviada para conferência;
- esquema e tipos do Excel;
- suíte completa sem regressão.

## Critério de conclusão

Um layout não está homologado apenas porque o parser executa. É necessário:

1. teste automatizado aprovado;
2. comparação com gabarito manual;
3. zero perda silenciosa;
4. sinais financeiros corretos;
5. documentação e ADR atualizadas;
6. aprovação do usuário.
