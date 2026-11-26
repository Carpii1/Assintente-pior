@echo off
chcp 65001 > nul
echo ========================================================
echo        PIOR - Envio para o GitHub
echo ========================================================
echo.
set /p REPO_URL="Cole a URL do seu repositorio GitHub (ex: https://github.com/SEU_USUARIO/pior-assistant.git): "

if "%REPO_URL%"=="" (
    echo [ERRO] Nenhuma URL informada. Operacao cancelada.
    pause
    exit /b 1
)

echo.
echo Adicionando repositorio remoto...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo Enviando branch main para o GitHub...
echo (O navegador ou o Git Credential Manager pode solicitar sua confirmacao de login)
echo.

git branch -M main
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo [SUCESSO] Projeto enviado para o GitHub com sucesso!
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo [AVISO] Ocorreu um problema no envio. Verifique se o
    echo repositorio existe no seu GitHub e se voce tem permissao.
    echo ========================================================
)

echo.
pause
