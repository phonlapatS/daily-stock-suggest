@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
python scripts/check_forward_testing.py %*
pause

