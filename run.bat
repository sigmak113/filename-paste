@echo off
chcp 65001 >nul
pip install keyboard pywin32
python "%~dp0filename_paste.py"
pause
