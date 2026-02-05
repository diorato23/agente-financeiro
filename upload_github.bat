@echo off
chcp 65001 >nul
echo ==========================================
echo    CONFIGURAÇÃO AUTOMÁTICA V2 (CORREÇÃO)
echo ==========================================
echo.

:: 1. Verificar Git
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Git não encontrado. Instale: https://git-scm.com/download/win
    pause
    exit /b
)

:: 2. Configurar Identidade (O erro anterior ocorreu aqui!)
echo Verificando configuração de usuário do Git...
for /f "tokens=*" %%a in ('git config user.email') do set GIT_EMAIL=%%a
if "%GIT_EMAIL%"=="" (
    echo.
    echo [NECESSÁRIO] O Git precisa saber quem está enviando.
    set /p NEW_EMAIL="Digite seu email (o mesmo do GitHub): "
    set /p NEW_NAME="Digite seu nome (ex: Diora): "
    
    call git config --global user.email "%%NEW_EMAIL%%"
    call git config --global user.name "%%NEW_NAME%%"
    echo Configuração salva!
)

:: 3. Inicializar e Adicionar
if not exist ".git" git init
git branch -M main
git add .

:: 4. Commit (Agora vai funcionar)
git commit -m "Upload inicial corrigido"

:: 5. Configurar Remoto
:: Removemos o antigo para garantir que o novo link seja usado
git remote remove origin 2>nul

echo.
echo URL definida: https://github.com/diorato23/agente-financeiro.git
git remote add origin https://github.com/diorato23/agente-financeiro.git

:: 6. Enviar
echo.
echo Tentando enviar novamente...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo [SUCESSO] Tudo certo! Projeto no ar.
    echo Link: https://github.com/diorato23/agente-financeiro
    echo ==========================================
) else (
    echo.
    echo [ERRO] Ainda deu erro. Verifique se o repositório no site está REALMENTE vazio.
)

pause
