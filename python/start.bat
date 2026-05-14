@echo off
echo ====================================
echo   学生管理系统启动脚本
echo ====================================
echo.

echo 正在检查Python环境...
python --version
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo 正在安装依赖...
pip install -r requirements.txt

if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ====================================
echo   启动API服务...
echo ====================================
echo.
echo 访问地址: http://127.0.0.1:5000
echo API文档: http://127.0.0.1:5000/health
echo.
echo 按 Ctrl+C 停止服务
echo.

python app_db.py

pause
