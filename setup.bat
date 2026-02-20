@echo off
echo ==========================================
echo       Agente Financeiro - Setup
echo ==========================================

echo [1/4] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Docker nao encontrado. Instale o Docker Desktop.
    pause
    exit /b
)

echo [2/4] Criando arquivo .env se necessario...
if not exist .env (
    echo [AVISO] Arquivo .env nao encontrado. Criando a partir de .env.example...
    copy .env.example .env
    echo [!] Por favor, edite o arquivo .env com suas senhas seguras.
) else (
    echo [OK] Arquivo .env encontrado.
)

echo [3/4] Construindo e iniciando containers...
docker compose up -d --build

echo [4/4] Verificando status...
docker compose ps

echo ==========================================
echo       Deploy Finalizado com Sucesso!
echo ==========================================
echo Acesse: http://localhost:8000
pause
