@echo off
rem -----------------------------------------------------------
rem Build the standalone Windows executable for Pior (FastAPI server)
rem -----------------------------------------------------------
setlocal

rem Ensure pyinstaller is installed
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller via pip...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Falha ao instalar PyInstaller. Abortando.
        exit /b 1
    )
)

rem Build the exe (onefile, console hidden)
pyinstaller --onefile --noconsole run_pior.py
if %errorlevel% neq 0 (
    echo Falha ao compilar o exe. Abortando.
    exit /b 1
)

rem Move the generated exe to the project root for easy access
if exist dist\run_pior.exe (
    move /Y dist\run_pior.exe .
    echo Executavel criado: run_pior.exe
) else (
    echo exe nao encontrado em dist. Verifique o log.
)

rem Cleanup build artefacts (optional)
rmdir /S /Q build
rmdir /S /Q __pycache__
if exist run_pior.spec del /F /Q run_pior.spec

endlocal
pause
