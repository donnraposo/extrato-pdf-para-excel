# Extrato Parser

Aplicação local para Windows que converte extratos bancários em PDF textual para Excel.

## Estado da primeira versão

- lê todas as páginas de um PDF com texto selecionável;
- usa a posição visual das palavras para reconstruir colunas;
- reconhece Data, Descrição, Nº Documento, Crédito, Débito e Saldo;
- preserva `Crédito (R$)` e `Débito (R$)` em colunas separadas;
- também calcula `Movimento (R$)`: crédito positivo e débito negativo;
- cria as abas `Lançamentos`, `Conferência` e `Metadados`;
- possui detecção inicial do formato demonstrado do Santander;
- reconhece o formato Itaú com `Entradas`, `Saídas` e `Saldo`;
- adapta as colunas do Excel ao esquema reconhecido: o Itaú, por exemplo, não recebe `Nº Documento`;
- não usa internet nem envia o extrato a serviços externos.

Layouts bancários desconhecidos podem exigir ajustes. O sistema preserva ambiguidades na aba de conferência.

## Esquemas atualmente reconhecidos

- **Santander:** Data, Descrição, Nº Documento, Crédito, Débito, Movimento e Saldo;
- **Itaú:** Data, Descrição, Entradas, Saídas, Movimento e Saldo.

O campo `Movimento (R$)` é calculado pelo sistema: entradas/créditos são positivos e saídas/débitos são negativos. Outros nomes equivalentes são normalizados pelo detector de cabeçalhos. Layouts ainda desconhecidos podem precisar de um adaptador e uma amostra anonimizada.

## Como abrir

No Windows, dê dois cliques em `ABRIR_EXTRATO_PARSER.bat`. Na tela:

1. clique em **Selecionar PDF**;
2. confirme o destino do Excel;
3. clique em **Gerar Excel**;
4. revise a aba `Conferência` ao final.

## Desenvolvimento e testes

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m extrato_parser.app
```

Para o segundo comando, instale o projeto em modo de desenvolvimento ou defina `PYTHONPATH=src`. O inicializador já configura o caminho do código automaticamente.

## Limitações

- PDFs escaneados ainda não são suportados;
- PDF protegido ou com codificação textual defeituosa pode não ser interpretado;
- campos adicionais dependem de cabeçalhos reconhecíveis; a infraestrutura está preparada, mas a ampliação do detector será incremental por amostras reais;
- antes do uso contábil, compare o resultado com o PDF e verifique a aba `Conferência`.
