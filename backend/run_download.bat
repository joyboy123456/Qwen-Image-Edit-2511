@echo off
chcp 65001 >nul
cd /d "f:\1\comfyui"
python -m modal run --detach backend/download_models_simple.py
pause
