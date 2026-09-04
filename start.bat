@echo off
title SkillTrack - SIH26135 Local Server
echo ===================================================
echo  Starting SkillTrack Web Server...
echo ===================================================
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python run.py
pause
