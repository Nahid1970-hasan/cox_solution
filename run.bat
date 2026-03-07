@echo off
REM Run Django with the project's virtual environment (no need to activate venv)
cd /d "%~dp0"
"venv\Scripts\python.exe" manage.py runserver %*
pause
