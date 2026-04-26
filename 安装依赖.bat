@echo off
chcp 65001 >nul
title 安装风控系统依赖

echo ============================================================
echo   风控策略/建模/算法工程师工作系统
echo   依赖安装程序
echo ============================================================
echo.

cd /d "%~dp0"

echo [步骤 1/4] 检查 Python 环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python！
    echo.
    echo 请先安装 Python 3.8 或更高版本：
    echo   下载地址: https://www.python.org/downloads/
    echo.
    echo 重要提示: 安装时务必勾选 "Add Python to PATH"
    echo ============================================================
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] %%i
echo.

echo [步骤 2/4] 检查并升级 pip
python -m pip install --upgrade pip -q 2>nul
echo [OK] pip 已准备就绪
echo.

echo [步骤 3/4] 安装核心依赖包
echo.
echo 核心依赖包括: numpy, pandas, flask, scikit-learn, matplotlib, seaborn 等
echo.

set "FAILED_PACKAGES="

set "CORE_LIST=numpy pandas flask flask-cors scikit-learn joblib matplotlib seaborn openpyxl xlrd scipy"

for %%p in (%CORE_LIST%) do (
    echo [安装] %%p
    pip install %%p
    python -c "import %%p" >nul 2>&1
    if %errorlevel% neq 0 (
        echo         [失败] %%p 安装失败
        set "FAILED_PACKAGES=%%p %FAILED_PACKAGES%"
    ) else (
        echo         [成功] %%p
    )
)

echo.
echo [步骤 4/4] 安装可选依赖包
echo.
echo 可选依赖包括: xgboost, lightgbm, pyarrow 等
echo 这些包安装失败不影响系统运行，系统会使用替代方案
echo.

set "OPTIONAL_LIST=xgboost lightgbm pyarrow"

for %%p in (%OPTIONAL_LIST%) do (
    echo [安装] %%p (可选)
    pip install %%p
    python -c "import %%p" >nul 2>&1
    if %errorlevel% neq 0 (
        echo         [跳过] %%p 安装失败，系统将使用替代方案
    ) else (
        echo         [成功] %%p
    )
)

echo.
echo ============================================================
echo   依赖安装完成！
echo ============================================================
echo.

echo [验证] 检查依赖安装状态:
echo.

set "ALL_OK=1"
for %%p in (%CORE_LIST%) do (
    python -c "import %%p" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [失败] %%p
        set "ALL_OK=0"
    ) else (
        echo [成功] %%p
    )
)

echo.
if "%ALL_OK%" == "1" (
    echo [结果] 所有核心依赖安装成功！
    echo.
    echo 现在可以双击 "启动系统.bat" 或 "快速启动.bat" 来运行系统
) else (
    echo [结果] 部分核心依赖安装失败
    echo.
    echo 失败的包: %FAILED_PACKAGES%
    echo.
    echo 可能的解决方案:
    echo 1. 以管理员身份运行此脚本
    echo 2. 检查网络连接
    echo 3. 手动执行: pip install 包名
    echo 4. 尝试使用 conda 安装: conda install 包名
)
echo.
echo ============================================================
pause
