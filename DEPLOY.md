# Guia de Deploy - Agente Financeiro

Este guia descreve como colocar a aplicação no ar em um servidor VPS.

## Pré-requisitos na VPS
- Docker e Docker Compose instalados.
- Rede `n8n_default` criada (se usar Traefik reverso).
  - Comando: `docker network create n8n_default` (se não existir).

## Passos para Deploy

1. **Transferir Arquivos**
   
   Você está usando `/var/www/agente-financeiro`, o que é ótimo!
   Certifique-se de que todos os arquivos atualizados (backend, frontend, Dockerfile, docker-compose.yml, etc) estejam lá.

2. **Configuração**
   - O arquivo `.env` deve estar na pasta raiz.

3. **Subir a Aplicação**
   No terminal, dentro da pasta do projeto:
   ```bash
   docker compose up -d --build
   ```

4. **Verificar Status**
   ```bash
   docker compose ps
   ```

## Solução de Problemas Comuns

### ❌ Erro: "The container name is already in use"
Se aparecer um erro dizendo que o nome já está em uso, significa que tem um container antigo solto.
**Solução:**
Execute estes comandos para limpar e tentar de novo:
```bash
# 1. Tenta parar o container antigo
docker stop agente-financeiro

# 2. Remove o container antigo (forçando)
docker rm -f agente-financeiro

# 3. Sobe tudo de novo
docker compose up -d --build
```

### ❌ Erro: Container "Restarting" (Loop)
Se o status ficar como `Restarting ...`, significa que o programa está falhando ao iniciar.
Veja o erro exato com:
```bash
docker logs agente-financeiro
```
Envie o final do log para análise. Erros comuns:
- Dependência faltando no `requirements.txt`.
- Erro de conexão com Banco de Dados.
- Variável de ambiente faltando.
