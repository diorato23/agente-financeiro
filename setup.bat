@echo off
echo ==========================================
echo      CONFIGURACAO DO AGENTE FINANCEIRO
echo ==========================================
echo.

cd /d "%~dp0"

echo 1. Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado! Instale o Python 3.10+ e adicione ao PATH.
    pause
    exit /b
)

echo.
echo 2. Criando ambiente virtual (venv)...
if not exist venv (
    python -m venv venv
    echo [OK] Ambiente criado.
) else (
    echo [INFO] Ambiente ja existe.
)

echo.
echo 3. Instalando dependencias...
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo ==========================================
echo      INSTALACAO CONCLUIDA!
echo ==========================================
echo Agora execute o arquivo 'start.bat' para iniciar.
pause
