@echo off
chcp 65001 >nul
echo ====================================
echo   用户登录系统前端 - Vue3
echo ====================================
echo.

echo 正在检查Node.js环境...
node --version
if errorlevel 1 (
    echo [错误] 未安装Node.js
    echo 请先下载安装: https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo 正在安装依赖...
npm install

if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ====================================
echo   启动开发服务器...
echo ====================================
echo.
echo 前端地址: http://localhost:3000
echo API 地址: 见 python-web\.env 配置（远程/本地）
echo.
echo 本地联调时先启动后端: cd ..\python ^&^& python app.py
echo.
echo 按 Ctrl+C 停止服务
echo.

npm run dev

pause
