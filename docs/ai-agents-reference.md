# 🤖 Referência de Agentes de IA — Agente Financeiro

> Guia consolidado de todos os agentes de IA disponíveis no projeto, seus comandos, quando usá-los e como colaboram entre si.

---

## Sumário

- [Como Invocar um Agente](#como-invocar-um-agente)
- [Visão Geral dos Agentes](#visão-geral-dos-agentes)
- [Agentes em Detalhe](#agentes-em-detalhe)
  - [👑 aios-master — Orion](#-aios-master--orion)
  - [🔍 analyst — Atlas](#-analyst--atlas)
  - [🏛️ architect — Aria](#️-architect--aria)
  - [💻 dev — Dex](#-dev--dex)
  - [⚡ devops — Gage](#-devops--gage)
  - [📋 pm — Morgan](#-pm--morgan)
  - [🎯 po — Pax](#-po--pax)
  - [✅ qa — Quinn](#-qa--quinn)
  - [🌊 sm — River](#-sm--river)
  - [🎨 ux-design-expert — Uma](#-ux-design-expert--uma)
- [Fluxo de Colaboração Entre Agentes](#fluxo-de-colaboração-entre-agentes)
- [MCPs Disponíveis](#mcps-disponíveis)
- [Skills Disponíveis](#skills-disponíveis)
- [Workflows Disponíveis](#workflows-disponíveis)

---

## Como Invocar um Agente

Para ativar um agente, use o prefixo `@` seguido do ID do agente:

```
@aios-master   → Orion (Orquestrador)
@analyst       → Atlas (Analista)
@architect     → Aria (Arquiteto)
@dev           → Dex (Desenvolvedor)
@devops        → Gage (DevOps / Git)
@pm            → Morgan (Product Manager)
@po            → Pax (Product Owner)
@qa            → Quinn (QA)
@sm            → River (Scrum Master)
@ux-design-expert → Uma (UX/UI Designer)
```

Os comandos de cada agente usam o prefixo `*`:

```
*help          → Lista todos os comandos disponíveis
*yolo          → Ativa modo sem confirmação (ask > auto > explore)
*exit          → Sai do modo do agente
```

---

## Visão Geral dos Agentes

| Ícone | ID | Nome | Título | Arquétipo | Melhor para |
|-------|----|------|--------|-----------|-------------|
| 👑 | `aios-master` | Orion | AIOS Master Orchestrator | — | Tudo; orquestração geral; criação de componentes do framework |
| 🔍 | `analyst` | Atlas | Business Analyst | Explorer | Pesquisa, brainstorming, análise de mercado |
| 🏛️ | `architect` | Aria | System Architect | Visionary | Arquitetura de sistema, seleção de tecnologia, design de API |
| 💻 | `dev` | Dex | Full Stack Developer | Builder | Implementação de código, debugging, refatoração |
| ⚡ | `devops` | Gage | DevOps Specialist | Operator | Git push, PRs, CI/CD, versionamento semântico |
| 📋 | `pm` | Morgan | Product Manager | Strategist | PRDs, epics, estratégia de produto |
| 🎯 | `po` | Pax | Product Owner | Balancer | Backlog, priorização, validação de histórias |
| ✅ | `qa` | Quinn | Test Architect | Guardian | Revisão de código, quality gates, testes |
| 🌊 | `sm` | River | Scrum Master | Facilitator | Criação de histórias de usuário, sprint planning |
| 🎨 | `ux-design-expert` | Uma | UX/UI Designer | Empathizer | UX research, wireframes, design systems, componentes atômicos |

---

## Agentes em Detalhe

---

### 👑 aios-master — Orion

**Título:** AIOS Master Orchestrator & Framework Developer  
**Quando usar:** Para expertise abrangente em todos os domínios, criação/modificação de componentes do framework, orquestração de workflows, ou tarefas que não requerem persona especializada. É o único agente que pode executar `*correct-course`.

#### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `*create` | Cria novo componente AIOS (agent, task, workflow, template, checklist) |
| `*modify` | Modifica componente AIOS existente |
| `*run-workflow {name} [start\|continue\|status\|skip\|abort] [--mode=guided\|engine]` | Executa workflow em modo guiado ou como subagente |
| `*correct-course` | Realiza correção de curso do processo (exclusivo deste agente) |
| `*yolo` | Alterna modo de permissão |
| `*exit` | Sai do modo |

---

### 🔍 analyst — Atlas

**Título:** Business Analyst  
**Quando usar:** Para pesquisa de mercado, análise competitiva, pesquisa de usuários, facilitação de sessões de brainstorming, workshops de ideação, estudos de viabilidade, tendências do setor, documentação de discovery (brownfield).  
**NÃO usar para:** Criação de PRDs → `@pm`. Design de arquitetura → `@architect`.

#### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `*brainstorm {topic}` | Facilita brainstorming estruturado |
| `*perform-market-research` | Cria análise de pesquisa de mercado |
| `*create-project-brief` | Cria project brief |
| `*help` | Lista todos os comandos |
| `*yolo` | Alterna modo de permissão |
| `*exit` | Sai do modo |

---

### 🏛️ architect — Aria

**Título:** System Architect  
**Quando usar:** Para arquitetura de sistema (fullstack, backend, frontend, infraestrutura), seleção de stack tecnológico, design de API (REST/GraphQL/tRPC/WebSocket), arquitetura de segurança, otimização de performance, estratégia de deploy.  
**NÃO usar para:** Pesquisa de mercado → `@analyst`. Criação de PRD → `@pm`.

#### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `*generate-ai-prompt {topic}` | Gera prompt de IA para um tópico técnico |
| `*create-architecture` | Cria documentação de arquitetura |
| `*design-api` | Design de interfaces de API |
| `*security-review` | Revisão de arquitetura de segurança |
| `*help` | Lista todos os comandos |
| `*yolo` | Alterna modo de permissão |
| `*exit` | Sai do modo |

---

### 💻 dev — Dex

**Título:** Full Stack Developer  
**Quando usar:** Para implementação de código, debugging, refatoração e boas práticas de desenvolvimento.  
**NÃO usar para:** Operações de git push → `@devops`. Criação de histórias → `@sm`. Arquitetura → `@architect`.

#### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `*develop [--mode=yolo\|interactive\|preflight]` | Implementa tarefas de história |
| `*run-tests` | Executa linting e todos os testes |
| `*create-service {type}` | Cria novo serviço (api-integration, utility, agent-tool) |
| `*debug {issue}` | Inicia processo de debugging sistemático |
| `*review-qa` | Solicita revisão ao @qa após implementação |
| `*help` | Lista todos os comandos |
| `*yolo` | Alterna modo de permissão |
| `*exit` | Sai do modo |

---

### ⚡ devops — Gage

**Título:** GitHub Repository Manager & DevOps Specialist  
**Quando usar:** Para operações de repositório, gerenciamento de versão, CI/CD, quality gates e **operações de git push** (único agente autorizado a fazer push para repositório remoto).  
**Nota crítica:** É o ÚNICO agente autorizado a executar `git push`, criar PRs e fazer merge.

#### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `*detect-repo` | Detecta contexto do repositório |
| `*version-check` | Analisa versão e recomenda próxima (semver) |
| `*pre-push` | Executa todos os quality checks antes do push |
| `*push` | Executa git push após quality gates passarem |
| `*create-pr` | Cria pull request da branch atual |
| `*release` | Cria release versionada com changelog |
| `*cleanup` | Identifica e remove branches/arquivos obsoletos |
| `*configure-ci` | Configura/atualiza GitHub Actions workflows |
| `*setup-github` | Configura infraestrutura DevOps do projeto |
| `*add-mcp` | Adiciona servidor MCP ao Docker MCP Toolkit |
| `*list-mcps` | Lista MCPs habilitados e suas ferramentas |
| `*help` | Lista todos os comandos |
| `*exit` | Sai do modo |

**Quality gates obrigatórios antes de push:**
- CodeRabbit (0 issues CRITICAL)
- `npm run lint` — PASS
- `npm test` — PASS
- `npm run typecheck` — PASS
- `npm run build` — PASS

---

### 📋 pm — Morgan

**Título:** Product Manager  
**Quando usar:** Para criação de PRDs (greenfield e brownfield), criação e gerenciamento de epics, estratégia e visão de produto, priorização de features (MoSCoW, RICE), roadmap, casos de negócio.  
**NÃO usar para:** Pesquisa de mercado → `@analyst`. Design de arquitetura → `@architect`. Criação de histórias de usuário → `@sm`.

#### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `*create-prd` | Cria documento de requisitos de produto |
| `*create-brownfield-prd` | PRD para projetos existentes |
| `*create-epic` | Cria epic para brownfield |
| `*create-story` | Cria história de usuário |
| `*execute-epic {path}` | Executa plano de epic com desenvolvimento paralelo por waves |
| `*research {topic}` | Gera prompt de pesquisa aprofundada |
| `*gather-requirements` | Elicita e documenta requisitos |
| `*write-spec` | Gera documento de especificação formal |
| `*shard-prd` | Divide PRD em partes menores |
| `*toggle-profile` | Alterna perfil de usuário (bob / advanced) |
| `*help` | Lista todos os comandos |
| `*exit` | Sai do modo |

---

### 🎯 po — Pax

**Título:** Product Owner  
**Quando usar:** Para gerenciamento de backlog, refinamento de histórias, critérios de aceitação, sprint planning e decisões de priorização.  
**NÃO usar para:** Criação de PRD → `@pm`. Criação de histórias → `@sm`. Pesquisa → `@analyst`.

#### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `*validate-story-draft {story}` | Valida qualidade e completude da história (INÍCIO do ciclo) |
| `*close-story {story}` | Fecha história, atualiza epic (FIM do ciclo) |
| `*backlog-add` | Adiciona item ao backlog (follow-up/tech-debt/enhancement) |
| `*backlog-review` | Review de backlog para sprint planning |
| `*backlog-prioritize {item} {priority}` | Re-prioriza itens |
| `*backlog-schedule {item} {sprint}` | Agenda item para sprint |
| `*sync-story` | Sincroniza história com ferramenta PM (ClickUp, GitHub, Jira) |
| `*stories-index` | Regera índice de histórias |
| `*shard-doc {document} {destination}` | Divide documento em partes menores |
| `*help` | Lista todos os comandos |
| `*exit` | Sai do modo |

---

### ✅ qa — Quinn

**Título:** Test Architect & Quality Advisor  
**Quando usar:** Para revisão abrangente de arquitetura de teste, decisões de quality gate, melhoria de código e análise de qualidade. Fornece análise advisory (as equipes escolhem o nível de qualidade).  
**NÃO usar para:** Implementação de código → `@dev`. Criação de histórias → `@sm`.

#### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `*review {story}` | Revisão abrangente de história com decisão de gate |
| `*review-build {story}` | Revisão QA estruturada em 10 fases — gera `qa_report.md` |
| `*code-review {scope}` | Executa revisão automatizada (uncommitted ou committed) |
| `*gate {story}` | Cria decisão de quality gate (PASS/CONCERNS/FAIL/WAIVED) |
| `*nfr-assess {story}` | Valida requisitos não-funcionais (segurança, performance) |
| `*security-check {story}` | Scan de vulnerabilidades em 8 pontos |
| `*test-design {story}` | Cria cenários de teste |
| `*trace {story}` | Mapeia requisitos para testes (Given-When-Then) |
| `*validate-libraries {story}` | Valida uso de bibliotecas via Context7 |
| `*validate-migrations {story}` | Valida migrações de banco de dados |
| `*risk-profile {story}` | Gera matriz de avaliação de risco |
| `*create-fix-request {story}` | Gera QA_FIX_REQUEST.md para @dev |
| `*backlog-review` | Review de backlog para sprint planning |
| `*help` | Lista todos os comandos |
| `*exit` | Sai do modo |

**Integração CodeRabbit (automática):**
- CRITICAL → Auto-fix (até 3 tentativas)
- HIGH → Auto-fix (até 3 tentativas)
- MEDIUM → Documenta como tech debt
- LOW → Ignora / anota na revisão

---

### 🌊 sm — River

**Título:** Scrum Master  
**Quando usar:** Para criação de histórias de usuário a partir de PRD, validação e completude de histórias, definição de critérios de aceitação, refinamento de histórias, sprint planning, backlog grooming e gerenciamento de branches locais.  
**NÃO usar para:** Criação de PRD → `@pm`. Pesquisa → `@analyst`. Implementação → `@dev`. Git push → `@devops`.

#### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `*draft` | Cria próxima história de usuário |
| `*story-checklist` | Executa checklist de draft de história |
| `*help` | Lista todos os comandos |
| `*exit` | Sai do modo |

**Gerenciamento de branches (local apenas):**
```bash
git checkout -b feature/X.Y-story-name  # Criar branch de feature
git branch                              # Listar branches
git branch -d branch-name              # Deletar branch local
git checkout branch-name               # Trocar de branch
git merge branch-name                  # Merge local
# NUNCA: git push (use @devops)
```

---

### 🎨 ux-design-expert — Uma

**Título:** UX/UI Designer & Design System Architect  
**Quando usar:** Workflow completo de design — pesquisa de usuário, wireframes, design systems, extração de tokens, criação de componentes e quality assurance.  
**Filosofia:** Combina Sally (UX empático) + Brad Frost (Design Systems data-driven) usando **Atomic Design** como metodologia central.

#### Fases e Comandos

**Fase 1 — UX Research & Design:**

| Comando | Descrição |
|---------|-----------|
| `*research` | Pesquisa de usuário e análise de necessidades |
| `*wireframe {fidelity}` | Cria wireframes e fluxos de interação |
| `*generate-ui-prompt` | Gera prompts para ferramentas AI (v0, Lovable) |
| `*create-front-end-spec` | Cria especificação frontend detalhada |

**Fase 2 — Auditoria de Design System (Brownfield):**

| Comando | Descrição |
|---------|-----------|
| `*audit {path}` | Escaneia codebase por redundâncias de padrões UI |
| `*consolidate` | Reduz redundância com clustering inteligente |
| `*shock-report` | Gera relatório HTML visual (caos + ROI) |

**Fase 3 — Tokens & Setup:**

| Comando | Descrição |
|---------|-----------|
| `*tokenize` | Extrai design tokens dos padrões consolidados |
| `*setup` | Inicializa estrutura do design system |
| `*migrate` | Gera estratégia de migração faseada |
| `*upgrade-tailwind` | Plano e execução de upgrades Tailwind CSS v4 |

**Fase 4 — Construção de Componentes Atômicos:**

| Comando | Descrição |
|---------|-----------|
| `*build {component}` | Constrói componente atômico em produção |
| `*compose {molecule}` | Compõe molécula a partir de átomos existentes |
| `*extend {component}` | Adiciona variante a componente existente |

**Fase 5 — Documentação & Qualidade:**

| Comando | Descrição |
|---------|-----------|
| `*document` | Gera documentação da pattern library |
| `*a11y-check` | Auditoria de acessibilidade (WCAG AA/AAA) |
| `*calculate-roi` | Calcula ROI e economias de custo |
| `*help` | Lista comandos por fase |
| `*exit` | Sai do modo |

---

## Fluxo de Colaboração Entre Agentes

```mermaid
flowchart TD
    analyst["🔍 @analyst\nAtlas"] -->|project-brief| pm
    pm["📋 @pm\nMorgan"] -->|PRD| po
    po["🎯 @po\nPax"] -->|backlog priorizado| sm
    sm["🌊 @sm\nRiver"] -->|histórias| dev
    architect["🏛️ @architect\nAria"] -->|arquitetura| dev
    ux["🎨 @ux-design-expert\nUma"] -->|specs de design| dev
    dev["💻 @dev\nDex"] -->|código pronto| qa
    qa["✅ @qa\nQuinn"] -->|aprovado| devops
    devops["⚡ @devops\nGage"] -->|push + PR| GitHub
    master["👑 @aios-master\nOrion"] -->|coordena| todos
```

### Autoridade de Comandos por Escopo

| Operação | Agente Responsável |
|----------|-------------------|
| `git push` / criar PR / merge PR | **@devops** (exclusivo) |
| `git checkout -b` / branches locais | @sm |
| Criação de épicos | @pm |
| Criação de histórias | @sm |
| Validação de histórias | @po |
| Implementação de código | @dev |
| Revisão QA e quality gates | @qa |
| Arquitetura e tecnologia | @architect |
| Correção de curso (`*correct-course`) | **@aios-master** (exclusivo) |

---

## MCPs Disponíveis

Os MCPs (Model Context Protocol) estendem as capacidades dos agentes com ferramentas externas.

### MCPs Ativos no Projeto

| MCP | Servidor | Ferramentas |
|-----|----------|-------------|
| **GitHub** | `github-mcp-server` | Gerenciamento de issues, PRs, branches, commits, code search |
| **Supabase** | `supabase-mcp-server` | Queries SQL, migrações, edge functions, logs, tipos TypeScript |

### Como os MCPs são Usados

- **`github-mcp-server`** → Usado principalmente pelo `@devops` (Gage) para operações de repositório, criação de PRs e gerenciamento de releases.
- **`supabase-mcp-server`** → Usado pelo `@dev` (Dex) e `@architect` (Aria) para operações de banco de dados, migrações DDL e deploy de Edge Functions.

---

## Skills Disponíveis

Skills são pastas de instruções e scripts que estendem as capacidades para tarefas especializadas. Localização: `.agent/skills/` (cada skill tem um `SKILL.md`).

> Para usar uma skill, leia o arquivo `SKILL.md` correspondente com a ferramenta `view_file` antes de executar.

---

## Workflows Disponíveis

Workflows são processos passo-a-passo definidos em `.agent/workflows/`. Invoque com `/nome-do-workflow`.

| Comando | Arquivo | Descrição |
|---------|---------|-----------|
| `/brainstorm` | `brainstorm.md` | Exploração de conceitos, ideias e soluções criativas |
| `/bug` | `bug.md` | Processo para identificação e correção de bugs |
| `/create` | `create.md` | Criação estruturada de novos arquivos, componentes ou projetos |
| `/debug` | `debug.md` | Processo sistemático de identificação e solução de erros |
| `/deploy` | `deploy.md` | Procedimentos para deploy e publicação da aplicação |
| `/docs` | `docs.md` | Processo para criar e manter a documentação do projeto |
| `/feature` | `feature.md` | Processo completo para desenvolver e entregar novas funcionalidades |
| `/melhoria` | `melhoria.md` | Processo para realizar melhorias e refatoração no código existente |
| `/orchestrate` | `orchestrate.md` | Coordenação de múltiplas tarefas e dependências |
| `/plan` | `plan.md` | Planejamento inicial de novas funcionalidades ou melhorias |
| `/test` | `test.md` | Planejamento e execução de testes sistemáticos |
| `/ui-ux-pro-max` | `ui-ux-pro-max.md` | Design de interface e experiência de usuário de alta fidelidade |

### Workflow `/deploy` — Passos

1. **Pre-Deploy Check** — testes passaram? código limpo? dependências atualizadas?  
2. **Build** — compilar assets, construir imagens Docker  
3. **Deploy** — enviar para VPS, migrar banco, reiniciar serviços  
4. **Post-Deploy Verification** — acessar app, verificar logs, testar fluxos críticos  

### Workflow `/feature` — Passos

1. **Especificação** — escopo, requisitos, mockups  
2. **Planejamento Técnico** — usar `/plan`, impacto na arquitetura  
3. **Implementação** — codificar seguindo padrões  
4. **Testes** — unitários, integração, validação  
5. **Documentação** — README, docs específicas  

### Workflow `/plan` — Passos

1. **Análise de Requisitos** — entender pedido, identificar arquivos, dependências  
2. **Criação de Artefatos** — `task.md` + `implementation_plan.md`  
3. **Revisão** — apresentar ao usuário, ajustar  
4. **Preparação** — ambiente de dev, branches  

---

*Última atualização: gerado automaticamente pela sessão de desenvolvimento do Agente Financeiro.*
