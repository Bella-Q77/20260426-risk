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

echo [检查 Python 环境]
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.9 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python 已安装
echo.

echo [检查依赖包]
python -c "import numpy, pandas, sklearn, flask, flask_cors" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 缺少必要的依赖包，正在安装...
    echo.
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo.
        echo [警告] 尝试使用官方源安装...
        pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo.
            echo [错误] 依赖安装失败，请手动执行: pip install -r requirements.txt
            pause
            exit /b 1
        )
    )
    echo.
    echo [OK] 依赖安装完成
) else (
    echo [OK] 所有依赖已安装
)
echo.

echo ============================================================
echo   正在启动服务...
echo   服务地址: http://localhost:5000
echo.
echo   按 Ctrl+C 停止服务
echo ============================================================
echo.

python app.py

pause
