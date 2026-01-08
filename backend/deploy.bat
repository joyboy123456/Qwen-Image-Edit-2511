@echo off
REM Deploy ComfyUI to Modal
cd /d "f:\1\comfyui"
python -m modal deploy backend/comfyui_modal.py 2>&1
echo.
echo Deployment command executed. Check output above for results.
pause
