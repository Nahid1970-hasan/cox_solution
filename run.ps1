# Run Django with the project's virtual environment (no need to activate venv)
Set-Location $PSScriptRoot
& "$PSScriptRoot\venv\Scripts\python.exe" manage.py runserver @args
