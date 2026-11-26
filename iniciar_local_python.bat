@echo off
setlocal

rem Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
  echo Python nao encontrado. Instalando via winget...
  winget install -e --id Python.Python.3.11
  if %errorlevel% neq 0 (
    echo Falha ao instalar Python. Abortando.
    exit /b 1
  )
  echo Python instalado. Reinicie o script.
  exit /b 0
)

rem Create virtual env if missing
if not exist .venv (
  echo Criando ambiente virtual .venv...
  python -m venv .venv
)

call .venv\Scripts\activate.bat

rem Upgrade pip and install deps
pip install --upgrade pip
pip install -r requirements.txt

rem Start FastAPI (Uvicorn)
echo Iniciando servidor FastAPI...
uvicorn src.main:app --reload

endlocal
pause
