@echo off
rem -----------------------------------------------------------
rem Build the standalone Windows executable for Pior using the project's virtual env
rem -----------------------------------------------------------
setlocal

rem Ensure we are in the project root
pushd "%~dp0"

rem ---------- Verify Python ----------
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Por favor execute iniciar_local_python.bat para instalar Python e criar o .venv.
    popd
    exit /b 1
)

rem ---------- Activate virtual environment ----------
if not exist .venv (
    echo .venv nao encontrado. Rode iniciar_local_python.bat primeiro.
    popd
    exit /b 1
)
call .venv\Scripts\activate.bat

rem ---------- Install PyInstaller inside the venv ----------
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller no ambiente virtual...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Falha ao instalar PyInstaller. Abortando.
        popd
        exit /b 1
    )
)

rem ---------- Ensure OpenCV is installed ----------
pip show opencv-python >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando opencv-python...
    pip install opencv-python
    if %errorlevel% neq 0 (
        echo Falha ao instalar opencv-python. Abortando.
        popd
        exit /b 1
    )
)

rem ---------- Build the exe (onefile, console hidden) with hidden import cv2 ----------
echo Compilando run_pior.exe com hidden import cv2...
pyinstaller --onefile --noconsole --hidden-import=cv2 run_pior.py
if %errorlevel% neq 0 (
    echo Falha ao compilar o exe com PyInstaller. Abortando.
    popd
    exit /b 1
)

rem ---------- Move the exe to the project root ----------
if exist dist\run_pior.exe (
    move /Y dist\run_pior.exe .
    echo Executavel criado: run_pior.exe
) else (
    echo exe nao encontrado em dist. Verifique o log do PyInstaller.
    popd
    exit /b 1
)

rem ---------- Iniciar o exe em background ----------
start "" /b run_pior.exe

echo Pior exe iniciado. Abra http://localhost:8000 no navegador.

rem ---------- Cleanup (optional) ----------
rmdir /S /Q build 2>nul
rmdir /S /Q __pycache__ 2>nul
if exist run_pior.spec del /F /Q run_pior.spec

popd
endlocal
pause
