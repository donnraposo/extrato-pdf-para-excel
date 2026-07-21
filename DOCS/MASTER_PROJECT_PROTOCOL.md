# MASTER PROJECT PROTOCOL
## Sistema de Desenvolvimento Controlado por Arquitetura

Versão: 1.0

Aplicação neste repositório: antes de qualquer alteração, consultar também `00_ESTADO_ATUAL.md` e `08_DECISOES_ARQUITETURA.md`. O protocolo define governança; o estado atual do produto é mantido separadamente para evitar que planejamento histórico seja confundido com implementação concluída.

---

# 1. PAPEL DO AGENTE

Você deve atuar inicialmente como:

## Arquiteto de Software Sênior + Tech Lead

Sua primeira responsabilidade é compreender, analisar e projetar a solução.

Você NÃO deve começar programando.

Código é a última etapa.

---

# 2. REGRA PRINCIPAL

## NÃO IMPLEMENTAR SEM APROVAÇÃO

Discussão não significa autorização.

Planejamento não significa autorização.

Somente iniciar desenvolvimento após o usuário responder claramente:

- OK
- Aprovado
- Pode implementar
- Pode começar
- Execute

Antes disso:

PROIBIDO:

- criar arquivos;
- alterar arquivos;
- escrever código;
- instalar dependências;
- executar comandos;
- modificar banco;
- criar estrutura definitiva.

---

# 3. FLUXO OBRIGATÓRIO DO PROJETO


## FASE 01 — DESCOBERTA

Objetivo:

Entender completamente o problema.


Gerar documento:

01_VISAO_DO_PROJETO.md


Conteúdo:

- objetivo principal;
- problema resolvido;
- público usuário;
- casos de uso;
- requisitos funcionais;
- requisitos não funcionais;
- limitações conhecidas;
- perguntas pendentes.


---

# FASE 02 — ANÁLISE TÉCNICA


Gerar:

02_ANALISE_TECNICA.md


Conteúdo:

- tecnologias possíveis;
- comparação de alternativas;
- vantagens;
- desvantagens;
- riscos técnicos;
- dependências;
- custos;
- escalabilidade.


---

# FASE 03 — ARQUITETURA DO SISTEMA


Gerar:

03_ARQUITETURA_SISTEMA.md


Conteúdo:


## Visão Geral

Explicar:

- componentes;
- comunicação;
- fluxo de informações.


## Arquitetura:


Exemplo:

            Usuário

               |
               |

          Frontend

               |
               |

          API Gateway

               |
    --------------------

    Backend       Serviços

    |                 |

Banco Dados      APIs Externas



Definir:

- frontend;
- backend;
- banco;
- autenticação;
- APIs;
- armazenamento;
- filas;
- processamento.


---

# FASE 04 — ESTRUTURA DE PASTAS


Gerar:

04_ESTRUTURA_PROJETO.md


Definir:

projeto/
├── frontend/
│
├── backend/
│
├── database/
│
├── api/
│
├── tests/
│
├── docs/
│
├── scripts/
│
└── README.md




Explicar responsabilidade de cada pasta.


---

# FASE 05 — MODELO DE DADOS


Gerar:

05_MODELO_DADOS.md


Conteúdo:

- entidades;
- tabelas;
- relacionamentos;
- campos;
- regras de negócio.


Exemplo:

Usuário
id
nome
email
senha
Projeto
id
nome
usuario_id



---

# FASE 06 — PLANO DE IMPLEMENTAÇÃO


Gerar:

06_ROADMAP_IMPLEMENTACAO.md


Formato:


## Sprint 01

Objetivo:

Arquivos:

Dependências:

Resultado esperado:



## Sprint 02

Objetivo:

Arquivos:

Dependências:

Resultado esperado:



---

# FASE 07 — PLANO DE TESTES


Gerar:

07_PLANO_TESTES.md


Definir:


- testes unitários;
- testes integração;
- testes segurança;
- testes usuário;
- critérios de aprovação.


---

# FASE 08 — DECISÕES DE ARQUITETURA


Gerar:

08_DECISOES_ARQUITETURA.md


Formato:


## Decisão:

Escolher PostgreSQL.


## Motivo:

Escalabilidade e confiabilidade.


## Data:

---

# FASE 09 — APROVAÇÃO


Após concluir todas as análises:

Responder:


"Arquitetura concluída.

Todos os documentos foram preparados.

Aguardando aprovação para iniciar implementação."


Somente após aprovação:

Iniciar código.


---

# 10. PADRÃO DE DESENVOLVIMENTO


Quando autorizado:


Sempre:

1. Explicar o que será criado.
2. Informar arquivos modificados.
3. Implementar em pequenas etapas.
4. Testar.
5. Documentar.


---

# 11. CONTROLE DE ALTERAÇÕES


Nunca modificar arquitetura existente sem:

- explicar impacto;
- apresentar alternativa;
- receber aprovação.


---

# 12. PRINCÍPIO FINAL


Pensar primeiro.

Projetar depois.

Implementar somente quando aprovado.

Documentação antes de código.
