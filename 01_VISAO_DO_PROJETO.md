# 01 — Visão do Projeto

## Objetivo principal

Criar uma aplicação local para Windows que permita selecionar um único extrato bancário em PDF, processar todas as suas páginas e gerar um único arquivo Excel com os lançamentos identificados.

O sistema deve reconhecer automaticamente os campos disponíveis no documento. Cinco campos terão representação padronizada e aparecerão primeiro no Excel:

1. Data;
2. Descrição;
3. Nº Documento;
4. Crédito (R$);
5. Débito (R$);
6. Movimento (R$);
7. Saldo (R$).

Campos adicionais encontrados no extrato serão preservados como novas colunas ao final. Portanto, arquivos Excel gerados a partir de bancos diferentes poderão possuir esquemas diferentes.

## Problema resolvido

Extratos bancários apresentam lançamentos visualmente tabulares, mas a cópia do texto frequentemente mistura cabeçalhos, descrições multilinha, documentos, créditos, débitos e saldos. O projeto transforma essa representação desestruturada em dados tabulares auditáveis, reduzindo a organização manual no Excel.

## Público usuário

- Usuário único;
- uso no próprio computador Windows;
- processamento local e offline;
- interface gráfica simples, sem necessidade de terminal.

## Casos de uso

### UC01 — Selecionar extrato

O usuário abre a aplicação, seleciona um PDF e escolhe onde salvar o Excel.

### UC02 — Interpretar páginas

O sistema lê todas as páginas, ignora cabeçalhos e rodapés, identifica a estrutura tabular e agrupa linhas que pertencem ao mesmo lançamento.

### UC03 — Normalizar movimentos

Créditos são representados como valores positivos e débitos como valores negativos.

### UC04 — Preservar campos variáveis

Campos reconhecidos que não fazem parte do esquema comum são adicionados automaticamente ao Excel.

### UC05 — Conferir incertezas

Registros ambíguos ou incompletos são preservados em uma aba de conferência, acompanhados da página, texto original e motivo do alerta.

## Requisitos funcionais

- RF01: selecionar um arquivo PDF por interface gráfica;
- RF02: processar um PDF com uma ou várias páginas;
- RF03: trabalhar inicialmente com PDFs cujo texto seja selecionável;
- RF04: detectar cabeçalhos e limites de colunas usando texto e posição na página;
- RF05: reconhecer sinônimos, como `Histórico`/`Descrição` e `Documento`/`Nº Documento`;
- RF06: produzir uma linha por lançamento;
- RF07: unir descrições continuadas em várias linhas;
- RF08: herdar a data para lançamentos subsequentes quando ela não for repetida visualmente;
- RF09: deixar campos ausentes vazios;
- RF10: preservar crédito e débito em colunas separadas, com valores positivos;
- RF10.1: calcular Movimento com crédito positivo e débito negativo;
- RF11: não inventar nem repetir saldo quando ele não estiver associado ao lançamento;
- RF12: detectar e preservar colunas adicionais;
- RF13: reunir todas as páginas em um único `.xlsx`;
- RF14: gerar abas `Lançamentos`, `Conferência` e `Metadados`;
- RF15: informar conclusão, quantidade de registros e alertas;
- RF16: permitir evolução por regras específicas de banco sem reescrever o núcleo.

## Requisitos não funcionais

- RNF01: executar localmente no Windows;
- RNF02: não enviar dados bancários para serviços externos;
- RNF03: apresentar interface em português brasileiro;
- RNF04: aceitar datas e números no padrão brasileiro;
- RNF05: manter rastreabilidade até arquivo, página e texto de origem;
- RNF06: falhar de forma segura, preservando linhas duvidosas para conferência;
- RNF07: gerar Excel compatível com versões atuais do Microsoft Excel;
- RNF08: separar extração, interpretação, validação e exportação para facilitar manutenção;
- RNF09: registrar erros sem expor dados sensíveis além do necessário.

## Regras de negócio

- RB01: movimento de crédito é positivo;
- RB02: movimento de débito é negativo;
- RB03: `-`, ausência ou marcador equivalente no documento torna o campo vazio;
- RB04: saldo é preenchido somente quando houver associação confiável àquele lançamento;
- RB05: todas as páginas pertencem ao mesmo arquivo Excel de saída;
- RB06: campos extras são adicionados depois dos cinco campos comuns;
- RB07: o conteúdo original nunca é descartado silenciosamente quando houver dúvida;
- RB08: resumo, saldo inicial/final, cabeçalho e rodapé não são lançamentos, mas podem compor metadados.

## Observações da amostra Santander

- a data é apresentada apenas no primeiro lançamento de um grupo;
- descrições e detalhes podem ocupar várias linhas;
- créditos e débitos ficam em colunas distintas;
- o sinal de débito pode aparecer após o valor;
- o saldo pode aparecer apenas ao final do grupo diário;
- cabeçalhos e rodapés reaparecem entre páginas;
- textos copiados sequencialmente não preservam de forma suficiente a estrutura visual.

## Limitações conhecidas

- não é possível garantir interpretação perfeita de todo layout bancário desconhecido;
- a primeira versão não contempla PDF composto apenas por imagem;
- documentos protegidos por senha exigirão tratamento posterior;
- tabelas com sobreposição, fontes incorporadas defeituosas ou texto fora de ordem podem exigir adaptador específico;
- o reconhecimento automático de campos extras depende de cabeçalhos ou indícios estruturais confiáveis;
- validação contábil pode ser limitada quando o extrato não apresenta saldo por lançamento.

## Critérios de sucesso

- aplicação abre e permite selecionar um PDF válido;
- todas as páginas são consideradas;
- o Excel contém os cinco campos comuns e os campos extras detectados;
- débitos e créditos recebem sinal correto;
- linhas não confiáveis são sinalizadas, não descartadas;
- a amostra Santander atinge os critérios de qualidade definidos no plano de testes;
- um novo layout pode ser suportado adicionando configuração ou adaptador isolado.

## Perguntas pendentes

- definir, durante a validação, o limiar mínimo de confiança para envio à aba `Conferência`;
- definir política futura para PDFs escaneados e protegidos por senha;
- definir se saldo inicial e saldo final também devem aparecer como metadados destacados.
