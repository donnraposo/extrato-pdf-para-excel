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

**Decisão:** manter cinco campos comuns no início e acrescentar campos detectados ao final.

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
