@echo off
REM Set code page to UTF-8
chcp 65001 > nul

REM Set Python to use UTF-8
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

cd /d "f:\1\comfyui"

echo ============================================================
echo Deploying ComfyUI service to Modal...
echo ============================================================
echo.

REM Run modal deploy and ignore encoding errors
python -m modal deploy backend/comfyui_modal.py 2>&1

echo.
echo ============================================================
echo Deployment command executed
echo Check Modal web console at: https://modal.com/apps
echo ============================================================
echo.
pause
