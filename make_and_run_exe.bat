@echo off
rem -----------------------------------------------------------
rem ONE‑CLICK script: install Python (if missing), create venv, install deps,
rem compile exe with PyInstaller and run it in background.
rem -----------------------------------------------------------
setlocal

rem ==== 1) Verify Python ====================================================
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing via winget...
    winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
    if %errorlevel% neq 0 (
        echo Failed to install Python. Please install it manually and rerun this script.
        exit /b 1
    )
)

rem ==== 2) Initialize git repository (first run only) ========================
if not exist .git (
    echo Initializing Git repository...
    init_repo.bat
)

rem ==== 3) Create/activate virtual env and install dependencies =============
iniciar_local_python.bat
rem (this script creates .venv if missing, activates it and runs pip install -r requirements.txt)

rem ==== 4) Build the standalone exe =========================================
build_exe_venv.bat

rem ==== 5) Start the exe in background ======================================
run_pior_exe.bat

endlocal
pause
