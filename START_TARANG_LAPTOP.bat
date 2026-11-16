@echo off
title TARANG Laptop Hybrid Collector
cd /d "%~dp0"
echo Starting TARANG Laptop Hybrid App on http://127.0.0.1:8765 ...
set PYTHONPATH=%~dp0apps\windows-collector;%~dp0services\api
python -m tarang_collector --port 8765
pause
