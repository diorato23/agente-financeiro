# 🚀 Guia Rápido: Atualizar Código e Docker no VPS

Este guia passo a passo serve para você salvar suas alterações, enviá-las para o GitHub e atualizá-las no seu servidor (VPS).

## 1️⃣ No seu Computador (Local)
Sempre que fizer uma mudança no código, você precisa enviá-la para a nuvem.

1.  Abra a pasta do projeto.
2.  Clique duas vezes no arquivo **`upload_github.bat`**.
3.  Espere ele confirmar que o "Upload" foi feito com sucesso.

---

## 2️⃣ No Servidor (VPS)
Agora vamos puxar essas mudanças e reiniciar o robô.

### A. Conectar (SSH)
Abra seu terminal/PowerShell e digite:
```bash
ssh root@SEU_IP_AQUI
```
*(Digite sua senha se pedir)*

### B. Atualizar e Reiniciar
Copie e cole os comandos abaixo (um por um):

**1. Entrar na pasta:**
```bash
cd agente-financeiro
```

**2. Baixar atualizações:**
```bash
git pull
```

**3. Recriar o container (Atualizar o Docker):**
```bash
docker compose up -d --build
```

### C. Verificar se está tudo certo (Logs)
Para ver o que o robô está fazendo agora:
```bash
docker logs -f agente-financeiro
```
*   **Para sair:** Pressione `CTRL + C`
