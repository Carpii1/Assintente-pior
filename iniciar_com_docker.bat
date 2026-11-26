@echo off
setlocal

rem Check if Docker is available
where docker >nul 2>&1
if %errorlevel% neq 0 (
  echo Docker nao encontrado no PATH. Instale Docker Desktop ou use a opcao Python.
  exit /b 1
)

echo Iniciando stack Docker...
docker compose up --build

endlocal
pause
