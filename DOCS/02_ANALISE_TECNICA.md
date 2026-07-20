# 02 — Análise Técnica

## Estratégia recomendada

Usar uma arquitetura híbrida, local e determinística:

1. extrair palavras e suas coordenadas do PDF;
2. localizar regiões tabulares e cabeçalhos;
3. inferir o esquema presente em cada região;
4. montar linhas físicas por alinhamento espacial;
5. agrupar linhas físicas em lançamentos lógicos;
6. normalizar campos comuns e preservar campos extras;
7. validar datas, valores, sinais e saldos;
8. exportar o resultado e as incertezas para Excel.

O reconhecimento genérico atende layouts bem estruturados. Adaptadores determinísticos específicos aumentam a precisão dos layouts conhecidos. A implementação combina leitura espacial e interpretação textual quando a codificação interna do PDF exigir.

## Arquitetura implementada

A aplicação adota Clean Architecture e princípios SOLID:

- entidades não dependem de PDF, Excel ou interface;
- o caso de uso depende de contratos de leitura, interpretação e exportação;
- `pdfplumber` e `openpyxl` ficam na infraestrutura;
- layouts implementam um contrato comum e são selecionados por detector e registro;
- cada classe pública ocupa um arquivo próprio;
- fachadas preservam compatibilidade com os pontos de entrada anteriores.

Fluxo de dependências: `presentation -> application -> ports/domain`, enquanto infraestrutura e layouts implementam os contratos da aplicação.

## Tecnologias possíveis

### Linguagem

**Python 3.12 ou versão estável compatível no momento da implementação.**

Vantagens: ecossistema maduro para PDF e Excel, desenvolvimento rápido e boa integração com interface desktop. Desvantagens: distribuição exige empacotamento e controle cuidadoso das dependências.

### Extração de PDF

#### pdfplumber — recomendado para o núcleo

- extrai palavras, caixas delimitadoras e tabelas;
- permite reconstruir colunas por coordenadas;
- facilita depuração por página.

Risco: alguns PDFs possuem ordem textual ou codificação interna defeituosa.

#### PyMuPDF — alternativa e fallback

- rápido;
- boa extração em blocos, palavras e coordenadas;
- útil como segundo mecanismo quando a extração principal falhar.

Risco: critérios de tabela precisam ser implementados no projeto.

#### Camelot/Tabula

- úteis para tabelas com linhas e colunas muito regulares;
- menos adequados como solução universal para extratos sem grades e descrições multilinha;
- Tabula adiciona dependência Java.

Decisão: não usar como núcleo na primeira versão.

### Interface gráfica

#### Tkinter — recomendado para a primeira versão

- acompanha o Python;
- suficiente para seleção, progresso, mensagens e salvamento;
- reduz dependências e complexidade.

#### PySide6

- interface mais sofisticada;
- maior tamanho de distribuição e complexidade.

Decisão: Tkinter inicialmente, preservando separação entre interface e motor.

### Excel

#### openpyxl — recomendado

- cria `.xlsx`, múltiplas abas, estilos, filtros e tipos numéricos;
- não exige Microsoft Excel instalado durante a geração.

#### pandas

- conveniente para manipulação tabular;
- não resolve a interpretação do PDF e adiciona peso desnecessário ao núcleo inicial.

Decisão: estruturas tipadas internas e openpyxl; pandas somente se surgir necessidade comprovada.

### Empacotamento

**PyInstaller** é a opção inicial para gerar executável Windows. Deve ser avaliado após o motor estar testado, pois empacotar cedo dificulta diagnóstico.

## Comparação das abordagens

| Abordagem | Precisão em layout conhecido | Generalização | Manutenção | Decisão |
|---|---:|---:|---:|---|
| Texto linear + regex | Média | Baixa | Baixa inicialmente | Complemento em adaptadores conhecidos |
| Extração espacial genérica | Boa | Boa | Média | Base do sistema |
| Regra fixa por banco | Muito boa | Baixa | Alta com muitos bancos | Adaptador opcional |
| IA/serviço externo | Variável | Potencialmente alta | Custo e privacidade | Fora do escopo inicial |
| OCR | Boa para imagens limpas | Média | Complexa | Evolução futura |

## Identificação dinâmica de campos

O sistema manterá um dicionário de sinônimos para campos comuns, mas não limitará o esquema a ele. Cabeçalhos desconhecidos serão saneados, preservados com nome legível e associados à faixa horizontal correspondente.

Exemplos de equivalência:

- `Data`, `Dt.` → `Data`;
- `Histórico`, `Descrição`, `Lançamento` → `Descrição`;
- `Documento`, `Nº Doc.`, `Identificador` → `Nº Documento` quando semanticamente equivalentes;
- `Crédito` e `Débito` → `Movimento (R$)` com sinal;
- `Valor`/`Movimento` com marcador C/D → `Movimento (R$)`.

Campos não equivalentes, como `Agência`, `Categoria` ou `Identificador PIX`, permanecem como colunas extras.

## Confiança e validação

Cada lançamento receberá evidências e alertas, não uma decisão opaca. Exemplos:

- data válida e dentro do período;
- valor monetário válido;
- coluna espacial compatível;
- sinal identificado;
- descrição presente;
- documento opcional;
- saldo coerente quando for possível reconciliar.

Baixa confiança encaminha o registro à aba `Conferência`.

## Dependências previstas

- biblioteca de extração PDF;
- biblioteca de Excel;
- biblioteca padrão para interface, datas, decimal, logs e arquivos;
- framework de testes;
- empacotador Windows somente na etapa de distribuição.

As versões exatas serão fixadas apenas na implementação, após teste de compatibilidade.

## Custos

- licenças: expectativa de custo zero com bibliotecas permissivas;
- infraestrutura: nenhuma, por execução local;
- manutenção: principal custo, devido à diversidade de layouts bancários;
- serviços externos: nenhum na primeira versão.

## Riscos técnicos e mitigação

| Risco | Impacto | Mitigação |
|---|---|---|
| Layout desconhecido sem cabeçalhos claros | Alto | confiança, conferência e adaptadores |
| Texto interno fora da ordem visual | Alto | coordenadas e fallback de extração |
| Descrição confundida com novo lançamento | Alto | máquina de estados e regras de continuidade |
| Saldo associado à linha errada | Alto | não preencher sem evidência espacial |
| Campo extra confundido com descrição | Médio | inferência por faixa e validação amostral |
| Mudança de layout de banco conhecido | Médio | detecção de assinatura e testes de regressão |
| Dados sensíveis em logs | Alto | logs mínimos e mascaramento |
| Executável bloqueado por antivírus | Médio | build reproduzível e documentação |

## Escalabilidade

O foco é um usuário e um arquivo por execução. A arquitetura permite adicionar novos bancos por configuração/adaptador. Processamento em lote, OCR e paralelismo permanecem extensões futuras, sem necessidade de alterar o modelo central.

O registro atual contém Inter, Caixa, Itaú, Santander e fallback genérico, nessa ordem de especificidade. Um novo banco deve implementar o contrato de layout e ser registrado sem alterar o caso de uso.
