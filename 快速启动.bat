@echo off
chcp 65001 >nul
title 风控策略/建模/算法工程师工作系统 - 极简版

echo ============================================================
echo   风控策略/建模/算法工程师工作系统
echo   Risk Control Workbench (Quick Start)
echo ============================================================
echo.
echo   此版本跳过依赖检查，直接尝试启动
echo   如果启动失败，请先运行 "安装依赖.bat"
echo ============================================================
echo.

cd /d "%~dp0"
set PYTHONPATH=%~dp0;%PYTHONPATH%

echo [启动] 正在启动服务...
echo.
echo   服务地址: http://localhost:5000
echo.
echo   如果浏览器没有自动打开，请手动访问上述地址
echo.
echo ============================================================
echo.

start http://localhost:5000

python app.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo   [错误] 服务启动失败！
    echo ============================================================
    echo.
    echo   可能原因及解决方案：
    echo.
    echo   1. 缺少 Python 环境
    echo      请安装 Python 3.8 或更高版本
    echo      下载地址: https://www.python.org/downloads/
    echo      注意: 安装时请勾选 "Add Python to PATH"
    echo.
    echo   2. 缺少依赖包
    echo      请双击运行 "安装依赖.bat" 文件
    echo.
    echo   3. 端口被占用
    echo      请检查端口 5000 是否被其他程序占用
    echo.
    echo ============================================================
    pause
)
