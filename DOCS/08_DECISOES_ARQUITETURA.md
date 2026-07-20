# 08 — Decisões de Arquitetura

## ADR-001 — Aplicação desktop local

**Decisão:** construir aplicação para Windows, de usuário único e funcionamento offline.

**Motivo:** simplicidade operacional, privacidade de dados bancários e ausência de necessidade de servidor.

**Consequência:** distribuição requer executável Windows; colaboração e acesso remoto ficam fora do escopo.

**Data:** 15/07/2026.

## ADR-002 — Python como linguagem

**Decisão:** usar Python na implementação.

**Motivo:** bibliotecas maduras para PDF, Excel, testes e interface desktop.

**Consequência:** será necessário empacotamento e controle de dependências.

**Data:** 15/07/2026.

## ADR-003 — Extração espacial, não apenas texto linear

**Decisão:** interpretar palavras e coordenadas da página.

**Motivo:** a amostra demonstra que o texto copiado perde relações entre crédito, débito, documento e saldo.

**Consequência:** implementação é mais elaborada, porém auditável e mais precisa.

**Data:** 15/07/2026.

## ADR-004 — Núcleo genérico com adaptadores

**Decisão:** combinar reconhecimento genérico com adaptadores isolados para layouts conhecidos.

**Motivo:** nenhum conjunto fixo de regras interpreta perfeitamente todos os bancos, mas regras totalmente separadas duplicariam o sistema.

**Consequência:** layouts novos podem funcionar parcialmente e gerar alertas até receberem adaptação.

**Data:** 15/07/2026.

## ADR-005 — Esquema Excel dinâmico

**Decisão original:** manter campos comuns no início e acrescentar campos detectados ao final.

**Estado:** revisada pela ADR-012. O esquema passou a ser definido pelo layout detectado; o modelo interno mantém os campos financeiros normalizados, mas o Excel não possui uma quantidade fixa de colunas comuns.

**Motivo:** exigência de preservar campos diferentes entre bancos.

**Consequência:** arquivos de saída podem possuir colunas diferentes e integrações futuras não devem presumir esquema inteiramente fixo.

**Data:** 15/07/2026.

## ADR-006 — Movimento financeiro unificado

**Decisão revisada:** preservar `Crédito (R$)` e `Débito (R$)` em colunas independentes, ambos com valores positivos, e também calcular `Movimento (R$)`, sendo crédito positivo e débito negativo.

**Motivo:** evita ambiguidade em reutilizações do Excel sem perder a conveniência de uma coluna assinada para cálculos.

**Consequência:** o esquema comum passa a ter sete colunas. Crédito e débito nunca devem ser preenchidos simultaneamente sem alerta.

**Data:** 15/07/2026; revisada e aprovada pelo usuário em 15/07/2026.

## ADR-007 — Saldo conservador

**Decisão:** preencher saldo somente quando houver associação confiável; não repetir automaticamente o último saldo.

**Motivo:** evitar informação fabricada e associação incorreta em grupos diários.

**Consequência:** algumas linhas terão saldo vazio, refletindo o documento.

**Data:** 15/07/2026.

## ADR-008 — Incerteza explícita

**Decisão:** preservar registros duvidosos na aba `Conferência`, com origem e alerta.

**Motivo:** dados financeiros exigem rastreabilidade e falha segura.

**Consequência:** poderá haver conferência manual em layouts novos.

**Data:** 15/07/2026.

## ADR-009 — Sem banco de dados e sem serviços externos

**Decisão:** não usar banco, nuvem ou IA externa na primeira versão.

**Motivo:** execução unitária local, menor complexidade e proteção dos dados.

**Consequência:** histórico de execuções não será persistido além dos arquivos gerados e logs mínimos.

**Data:** 15/07/2026.

## ADR-010 — PDFs textuais primeiro

**Decisão:** suportar inicialmente PDFs com texto selecionável.

**Motivo:** escopo informado e possibilidade de maior precisão sem OCR.

**Consequência:** PDF escaneado será detectado e rejeitado com orientação até uma fase futura aprovada.

**Data:** 15/07/2026.

## ADR-011 — Tkinter e openpyxl como escolhas iniciais

**Decisão:** planejar Tkinter para interface e openpyxl para Excel, condicionados à validação técnica na implementação.

**Motivo:** baixo peso, funcionamento local e recursos suficientes para o escopo.

**Consequência:** uma interface mais sofisticada exigiria decisão posterior de mudança.

**Data:** 15/07/2026.

## Registro de mudanças futuras

Qualquer mudança estrutural deve registrar: contexto, alternativas, impacto, decisão, data e aprovação do usuário antes da implementação.

## ADR-012 — Esquema de saída por layout detectado

**Decisão:** gerar as colunas do Excel conforme os campos reconhecidos no PDF, mantendo `Movimento (R$)` como campo calculado. O Santander mantém `Nº Documento`, enquanto o Itaú utiliza `Entradas (R$)` e `Saídas (R$)` e omite documento.

**Motivo:** preservar a semântica de cada banco sem impor colunas inexistentes e sem duplicar o motor de parsing.

**Alternativa rejeitada:** usar sempre um esquema fixo para todos os bancos; isso criaria campos vazios e reduziria a fidelidade ao documento.

**Consequência:** consumidores do Excel devem considerar que as colunas podem variar por layout. O núcleo mantém campos financeiros normalizados para validação e cálculo.

**Data:** 17/07/2026; aprovada pelo usuário.

## ADR-013 — Clean Architecture, SOLID e uma classe por arquivo

**Decisão:** organizar domínio, aplicação, portas, infraestrutura e layouts em camadas; cada classe pública ocupa um arquivo próprio.

**Motivo:** reduzir acoplamento, evitar crescimento monolítico do parser e permitir evolução segura por banco.

**Consequência:** fachadas antigas são mantidas temporariamente para compatibilidade; dependências concretas são injetadas no caso de uso.

**Data:** 20/07/2026; aprovada pelo usuário.

## ADR-014 — Registro extensível de layouts

**Decisão:** selecionar Inter, Caixa, Itaú, Santander ou fallback genérico por `LayoutRegistry` e `LayoutDetector`.

**Motivo:** novos bancos não devem introduzir condicionais no caso de uso.

**Consequência:** a ordem do registro vai do layout mais específico ao fallback genérico.

**Data:** 20/07/2026; aprovada pelo usuário.

## ADR-015 — Layout Banco Inter

**Decisão:** reconhecer datas por extenso, valores assinados e saldo por transação por interpretação determinística do texto extraído.

**Motivo:** o PDF pode misturar cabeçalho e data e não oferece o mesmo esquema espacial dos bancos anteriores.

**Consequência:** o Inter possui regressão própria e esquema sem Nº Documento.

**Data:** 20/07/2026; aprovada pelo usuário.

## ADR-016 — Layout Caixa e esquema nativo

**Decisão:** exportar Caixa como Data, Data Efetiva, Documento, Histórico, Valor e Saldo. Valor é decimal assinado; Data Efetiva preserva horário.

**Motivo:** fidelidade ao cabeçalho original e reutilização direta dos dados.

**Consequência:** Crédito, Débito e Movimento não aparecem separadamente no Excel Caixa, embora o modelo interno mantenha a classificação financeira.

**Data:** 20/07/2026; aprovada pelo usuário.

## ADR-017 — SALDO DIA na aba Lançamentos

**Decisão:** preservar cada `SALDO DIA` da Caixa na ordem original, usando as colunas existentes e deixando Valor vazio.

**Motivo:** o usuário precisa visualizar o fechamento diário exatamente junto aos movimentos.

**Consequência:** essas linhas não são movimentos e não exigem Data Efetiva ou Documento para status `OK`.

**Data:** 20/07/2026; aprovada pelo usuário.

## ADR-018 — Saldo textual da Caixa com C/D

**Decisão:** armazenar o saldo Caixa como texto sem `R$`, preservando a letra final, por exemplo `531,74 C` ou `255,00 D`.

**Motivo:** fidelidade explícita ao extrato conforme decisão do usuário.

**Alternativa rejeitada:** converter `D` em saldo negativo ou descartar o indicador.

**Consequência:** a coluna Saldo da Caixa não é diretamente somável no Excel; a coluna Valor permanece numérica.

**Data:** 20/07/2026; aprovada pelo usuário.
