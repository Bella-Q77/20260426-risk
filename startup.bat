@echo off
chcp 65001 >nul
title 风控策略/建模/算法工程师工作系统

echo ============================================================
echo   风控策略/建模/算法工程师工作系统
echo   Risk Control Workbench
echo ============================================================
echo.

cd /d "%~dp0"

set PYTHONPATH=%~dp0;%PYTHONPATH%

echo 正在启动服务...
echo 服务地址: http://localhost:5000
echo.
echo 按 Ctrl+C 停止服务
echo ============================================================
echo.

python app.py

pause
