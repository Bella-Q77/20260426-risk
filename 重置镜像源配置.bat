@echo off
chcp 65001 >nul
title 重置 pip 和 conda 镜像源配置

echo ============================================================
echo   重置 pip 和 conda 镜像源配置
echo   Reset pip and conda mirror configuration
echo ============================================================
echo.
echo   注意: 此脚本将移除自定义镜像源配置，使用官方默认源
echo.
echo   这是解决镜像源访问错误（如403、找不到包等问题）的有效方法
echo ============================================================
echo.

echo [步骤 1/4] 检查 pip 配置文件位置
echo.

set "PIP_CONFIG_DIR=%APPDATA%\pip"
set "PIP_CONFIG_FILE=%PIP_CONFIG_DIR%\pip.ini"

if exist "%PIP_CONFIG_FILE%" (
    echo [找到] pip 配置文件: %PIP_CONFIG_FILE%
    echo.
    echo [内容] 当前配置:
    echo ------------------------------------------------------------
    type "%PIP_CONFIG_FILE%"
    echo ------------------------------------------------------------
    echo.
    
    echo [操作] 正在备份并移除配置文件...
    copy "%PIP_CONFIG_FILE%" "%PIP_CONFIG_FILE%.backup" >nul
    if exist "%PIP_CONFIG_FILE%.backup" (
        echo [已备份] 备份文件: %PIP_CONFIG_FILE%.backup
    )
    
    del "%PIP_CONFIG_FILE%"
    echo [已删除] pip 配置文件已删除
) else (
    echo [未找到] 没有找到 pip 配置文件，继续下一步
)
echo.

echo [步骤 2/4] 检查其他可能的 pip 配置位置
echo.

set "PIP_CONFIG_DIR2=%USERPROFILE%\pip"
set "PIP_CONFIG_FILE2=%PIP_CONFIG_DIR2%\pip.ini"

if exist "%PIP_CONFIG_FILE2%" (
    echo [找到] 备用位置 pip 配置文件: %PIP_CONFIG_FILE2%
    copy "%PIP_CONFIG_FILE2%" "%PIP_CONFIG_FILE2%.backup" >nul
    del "%PIP_CONFIG_FILE2%"
    echo [已删除] 备用位置 pip 配置文件已删除
)

set "PIP_CONF_USER=%USERPROFILE%\.config\pip\pip.conf"
if exist "%PIP_CONF_USER%" (
    echo [找到] Linux/Mac 风格配置: %PIP_CONF_USER%
    copy "%PIP_CONF_USER%" "%PIP_CONF_USER%.backup" >nul
    del "%PIP_CONF_USER%"
    echo [已删除] 该配置文件已删除
)
echo.

echo [步骤 3/4] 重置 conda 配置（如果使用 conda）
echo.

conda --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [找到] conda 已安装
    
    echo [操作] 正在重置 conda 镜像源配置...
    conda config --remove-key channels 2>nul
    conda config --add channels defaults 2>nul
    conda config --set channel_alias https://conda.anaconda.org 2>nul
    
    echo [显示] 当前 conda 配置:
    echo ------------------------------------------------------------
    conda config --show channels
    echo ------------------------------------------------------------
    echo.
    echo [已完成] conda 镜像源已重置为默认官方源
) else (
    echo [跳过] 未检测到 conda
)
echo.

echo [步骤 4/4] 验证配置
echo.

echo [验证] pip 当前使用的镜像源:
echo ------------------------------------------------------------
pip config list 2>nul || echo (使用默认源)
echo ------------------------------------------------------------
echo.

echo ============================================================
echo   配置重置完成！
echo ============================================================
echo.
echo   现在可以运行 "安装依赖.bat" 来安装依赖包
echo   或者手动执行: pip install numpy pandas flask 等
echo.
echo   如果之前有 pip.conf/pip.ini 配置文件:
echo   - 已备份为 .backup 文件
echo   - 如需恢复，可以手动将 .backup 文件重命名
echo.
echo ============================================================
pause
