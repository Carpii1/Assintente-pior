@echo off
rem -----------------------------------------------------------
rem Start the compiled Pior executable in background (no console window)
rem -----------------------------------------------------------
setlocal

if not exist run_pior.exe (
    echo Executavel run_pior.exe nao encontrado. Execute build_exe.bat primeiro.
    exit /b 1
)

rem Start the exe hidden (use start /b for background)
start "" /b run_pior.exe

echo Pior exe iniciado em background.

endlocal
pause
