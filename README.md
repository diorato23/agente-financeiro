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

---

## 👩‍💻 Guia para Desenvolvedores (Novo)

Se você vai mexer no código, siga estes passos:

### 1. Clonar o Repositório
```bash
git clone https://github.com/diorato23/agente-financeiro.git
cd agente-financeiro
```

### 2. Rodar Localmente (Sem Docker)
Você pode usar os scripts automáticos:
- **Instalar:** Dê dois cliques em `setup.bat`.
- **Rodar:** Dê dois cliques em `start.bat`.

### 3. Rodar com Docker (Recomendado para simular Produção)
Se tiver Docker instalado, é o jeito mais fácil de ver exatamente como vai ficar no servidor:
```bash
docker compose up -d --build
```
O app ficará disponível em `http://localhost:8000`.

### 4. Últimas Atualizações (Mobile & UI)
- O sistema agora tem **Notificações Toast** bonitas (nada de `alert()`).
- O layout mobile foi ajustado (botões menores, cabeçalho limpo).
- As cores de alerta (Laranja/Vermelho) são automáticas baseadas em 70%/90% do orçamento.
- **Atenção:** Se mudar algo no HTML/JS/CSS, lembre-se de limpar o cache ou reconstruir o Docker para ver a mudança.

