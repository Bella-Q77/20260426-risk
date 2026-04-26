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

echo [步骤 1/5] 检查 Python 环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8 或更高版本
    echo.
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 注意: 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] %%i
echo.

echo [步骤 2/5] 检查 pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 pip，请确保 Python 安装正确
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('pip --version 2^>^&1') do echo [OK] %%i
echo.

echo [步骤 3/5] 检查核心依赖
set "CORE_PACKAGES=numpy pandas flask flask_cors sklearn joblib matplotlib seaborn openpyxl scipy"
set "MISSING_CORE=0"

for %%p in (%CORE_PACKAGES%) do (
    python -c "import %%p" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [缺失] %%p
        set "MISSING_CORE=1"
    ) else (
        echo [已安装] %%p
    )
)

if %MISSING_CORE% == 1 (
    echo.
    echo [警告] 缺少核心依赖包，正在安装...
    echo.
    
    echo [尝试] 使用清华镜像源安装...
    pip install numpy pandas flask flask-cors scikit-learn joblib matplotlib seaborn openpyxl scipy -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
    
    if %errorlevel% neq 0 (
        echo.
        echo [尝试] 使用阿里镜像源安装...
        pip install numpy pandas flask flask-cors scikit-learn joblib matplotlib seaborn openpyxl scipy -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
        
        if %errorlevel% neq 0 (
            echo.
            echo [尝试] 使用官方源安装...
            pip install numpy pandas flask flask-cors scikit-learn joblib matplotlib seaborn openpyxl scipy
            
            if %errorlevel% neq 0 (
                echo.
                echo [警告] 部分依赖安装可能失败，继续检查...
            )
        )
    )
    echo.
    echo [重新检查] 核心依赖状态:
    for %%p in (%CORE_PACKAGES%) do (
        python -c "import %%p" >nul 2>&1
        if %errorlevel% neq 0 (
            echo [失败] %%p
        ) else (
            echo [成功] %%p
        )
    )
) else (
    echo.
    echo [OK] 所有核心依赖已安装
)
echo.

echo [步骤 4/5] 检查可选依赖（xgboost, lightgbm, pyarrow）
set "OPTIONAL_PACKAGES=xgboost lightgbm pyarrow"

for %%p in (%OPTIONAL_PACKAGES%) do (
    python -c "import %%p" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [缺失] %%p ^(可选^)
        echo         正在尝试安装...
        pip install %%p -i https://pypi.tuna.tsinghua.edu.cn/simple >nul 2>&1
        python -c "import %%p" >nul 2>&1
        if %errorlevel% neq 0 (
            echo         [跳过] %%p 安装失败，系统将使用替代方案
        ) else (
            echo         [成功] %%p 已安装
        )
    ) else (
        echo [已安装] %%p
    )
)
echo.

echo [步骤 5/5] 验证系统启动
echo.
echo ============================================================
echo   系统准备就绪！
echo ============================================================
echo.
echo   服务地址: http://localhost:5000
echo.
echo   按 Ctrl+C 停止服务
echo.
echo   如果浏览器没有自动打开，请手动访问上述地址
echo ============================================================
echo.

start http://localhost:5000

python app.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 服务启动失败
    echo.
    echo 可能的解决方案:
    echo 1. 检查端口 5000 是否被占用
    echo 2. 检查防火墙设置
    echo 3. 以管理员身份运行此脚本
    pause
)
