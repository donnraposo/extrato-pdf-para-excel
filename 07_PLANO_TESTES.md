# 07 — Plano de Testes

## Princípios

- resultados esperados devem ser preparados manualmente a partir de amostras anonimizadas;
- nenhum teste deve depender de internet;
- valores financeiros devem ser comparados como decimais;
- toda correção de layout deve adicionar teste de regressão;
- o sistema deve preferir alertar a produzir silenciosamente dado incorreto.

## Testes unitários

### Datas brasileiras

- `05/02` com ano do período;
- `31/12/2026` completo;
- datas inválidas e fora do período;
- herança de data dentro do mesmo grupo.

### Moeda

- `1.368,50` → 1368,50;
- `335,99-` → -335,99 quando confirmado como débito;
- crédito e débito em colunas separadas;
- zero, célula vazia e formatos inválidos.

### Campos

- aliases conhecidos;
- cabeçalho extra preservado;
- nomes extras duplicados;
- documento `-` convertido em vazio;
- documento com zero à esquerda preservado.

### Agrupamento

- descrição de uma linha;
- descrição multilinha;
- vários lançamentos sob uma única data;
- troca de página no meio de um grupo;
- cabeçalho repetido não incorporado à descrição.

## Testes de integração

- PDF textual → representação espacial;
- representação espacial → esquema;
- esquema → lançamentos;
- lançamentos → Excel;
- abertura do Excel gerado e verificação de abas, células e tipos;
- falha controlada para PDF vazio, inválido, protegido ou sem texto.

## Testes de regressão por banco

Cada layout suportado terá:

- PDF anonimizado mínimo;
- manifesto do layout esperado;
- conjunto esperado de lançamentos;
- campos extras esperados;
- alertas esperados;
- versão/assinatura do adaptador.

Para o Santander da amostra, testar especialmente:

- data presente apenas no primeiro lançamento diário;
- descrições com parcela e período;
- valor de débito com sinal posterior;
- crédito e débito em faixas distintas;
- saldo apenas no fim de determinados grupos;
- rodapés `Página: n/m` e cabeçalhos repetidos;
- saldo inicial e final tratados como metadados, não lançamentos.

## Testes de segurança e privacidade

- ausência de chamadas de rede;
- logs não contêm extrato completo;
- arquivo existente não é sobrescrito sem confirmação;
- temporários são removidos após sucesso ou falha;
- caminhos e nomes incomuns não executam comandos;
- arquivo não PDF é rejeitado de forma legível.

## Testes de interface e usuário

- selecionar PDF e cancelar seleção;
- selecionar destino e cancelar;
- acompanhar progresso em PDF com várias páginas;
- impedir início duplicado;
- apresentar erro compreensível;
- abrir/encontrar o resultado após conclusão;
- interface permanece responsiva durante o processamento.

## Critérios de aprovação da primeira versão

- 100% das páginas do arquivo de teste são visitadas;
- nenhum lançamento do gabarito é descartado silenciosamente;
- 100% dos débitos e créditos aceitos possuem sinal correto;
- campos extras do gabarito são preservados;
- datas e valores exportados são tipos reais do Excel;
- cabeçalhos, rodapés e resumos não aparecem como lançamentos;
- registros não interpretados com segurança aparecem em `Conferência`;
- para o layout Santander aprovado, meta inicial de pelo menos 98% dos lançamentos estruturados corretamente, com 100% de precisão nos valores aceitos;
- testes automatizados passam no ambiente de desenvolvimento e no executável Windows.

## Homologação

O usuário comparará o Excel com o PDF em amostras reais anonimizadas. Divergências serão classificadas como regra genérica, variação de layout, erro de adaptador ou ambiguidade legítima. A versão só será aceita após correção ou sinalização explícita de todas as divergências críticas.
