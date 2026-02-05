# Agente Financeiro Pessoal 🇨🇴

Este é um assistente financeiro pessoal projetado para o mercado colombiano, com integração via WhatsApp (n8n) e Dashboard Web.

## Pré-requisitos

1.  **Python 3.10+** instalado.
2.  (Opcional) **Docker** se desejar rodar via container.
3.  **n8n** (Desktop ou Server) para a integração com WhatsApp.

## Instalação Rápida (Windows)

1.  Abra a pasta do projeto.
2.  Dê um duplo clique no arquivo `setup.bat`.
    - Isso criará o ambiente virtual (`venv`) e instalará as dependências automaticamente.

## Como Iniciar

1.  Execute o arquivo `start.bat`.
    - O servidor iniciará em `http://localhost:8000`.
    - O navegador abrirá automaticamente.

## Credenciais Padrão

Se for solicitado login, utilize:
- **Usuário:** `admin`
- **Senha:** `1234`

## Automação (n8n)

O arquivo `agente_financeiro.json` contém o workflow do n8n.
1.  No n8n, vá em **New Workflow**.
2.  Clique nos 3 pontinhos (canto superior direito) -> **Import from File**.
3.  Selecione o arquivo `agente_financeiro.json`.
4.  Configure as credenciais do WhatsApp e OpenAI no n8n.

## Estrutura

- `backend/`: API em FastAPI e Banco de Dados (`financeiro.db`).
- `frontend/`: Interface Web simples.
- `docker-compose.yml`: Configuração para deploy com Docker (avançado).
