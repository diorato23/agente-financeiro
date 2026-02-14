---
description: Procedimentos para deploy e publicação da aplicação
---

1. [Pre-Deploy Check]
   - Todos os testes passaram?
   - O código está comittado e limpo?
   - As dependências estão atualizadas (requirements.txt, package.json)?

2. [Build]
   - Compilar assets (se houver).
   - Construir imagens Docker (se usar Docker).

3. [Deploy]
   - Enviar arquivos para o servidor (VPS).
   - Executar scripts de migração de banco de dados.
   - Reiniciar serviços (Gunicorn, Nginx, Docker containers).

4. [Post-Deploy Verification]
   - Acessar a aplicação em produção.
   - Verificar logs de erro.
   - Testar fluxos críticos (Login, Cadastro).
