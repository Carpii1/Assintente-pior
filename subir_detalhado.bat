@echo off
chcp 65001 > nul
echo ========================================================
echo        PIOR - Envio Detalhado para o GitHub
echo ========================================================
echo.
cd /d "C:\Users\paulo\.gemini\antigravity\scratch\tcc"

echo Repositorio configurado:
git remote -v
echo.
echo Tentando enviar branch main para origin...
echo.

git push -u origin main -v

echo.
echo ========================================================
echo Codigo de saida: %ERRORLEVEL%
echo ========================================================
pause
