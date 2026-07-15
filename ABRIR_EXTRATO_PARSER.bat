@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
    echo O ambiente do Extrato Parser nao foi encontrado.
    echo Consulte o README.md para preparar o projeto.
    pause
    exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "run_app.pyw"
endlocal
