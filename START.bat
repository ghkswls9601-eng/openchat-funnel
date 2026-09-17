@echo off
setlocal
cd /d "%~dp0"
title OpenChat Funnel

echo ========================================
echo OpenChat Funnel - Setup and Start
echo ========================================
echo Working folder:
echo %CD%
echo.

if not exist "app.py" (
  echo ERROR: app.py not found.
  echo Extract the ZIP first, then run START.bat from that folder.
  pause
  exit /b 1
)

if not exist "requirements.txt" (
  echo ERROR: requirements.txt not found.
  pause
  exit /b 1
)

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
  echo ERROR: Python command is unavailable.
  pause
  exit /b 1
)

echo.
echo [2/4] Installing packages...
python -m pip install --upgrade pip
if errorlevel 1 goto :install_error
python -m pip install -r "%CD%\requirements.txt"
if errorlevel 1 goto :install_error

echo.
echo [3/4] Verifying Uvicorn...
python -c "import fastapi, uvicorn, jinja2; print('Dependencies OK')"
if errorlevel 1 goto :install_error

echo.
echo [4/4] Starting server...
echo DO NOT CLOSE THIS WINDOW while using the dashboard.
echo Dashboard: http://127.0.0.1:8000/admin
echo.
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8000/admin"
python -m uvicorn app:app --host 127.0.0.1 --port 8000
echo.
echo Server stopped.
pause
exit /b

:install_error
echo.
echo ERROR: Package installation failed.
echo Copy or screenshot the lines above this message.
pause
exit /b 1
