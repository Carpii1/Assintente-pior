@echo off
setlocal

echo Inicializando repositório Git...
git init
git add .
git commit -m "feat: scaffold do projeto Pior – Assistente Multimodal"
git branch -M main
echo Repositório preparado.

endlocal
pause
