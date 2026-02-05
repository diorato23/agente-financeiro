@echo off
echo ==========================================
echo       INICIANDO AGENTE FINANCEIRO
echo ==========================================
echo.

cd /d "%~dp0"

echo 1. Ativando ambiente virtual...
if not exist venv\Scripts\activate.bat (
    echo [ERRO] Pasta 'venv' nao encontrada!
    pause
    exit /b
)
call venv\Scripts\activate.bat

echo 2. Abrindo navegador...
start http://localhost:8000

echo 3. Iniciando Servidor...
echo (Pressione CTRL+C para parar)
echo.
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo [AVISO] O servidor parou. Veja o erro acima.
pause
