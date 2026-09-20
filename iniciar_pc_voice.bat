@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python pc_voice_control.py
pause
