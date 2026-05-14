#!/bin/bash

echo "===================================="
echo "  学生管理系统前端 - Vue3"
echo "===================================="
echo ""

echo "检查Node.js环境..."
node --version
if [ $? -ne 0 ]; then
    echo "[错误] 未安装Node.js"
    echo "请先下载安装: https://nodejs.org/"
    read -p "按Enter键退出..."
    exit 1
fi

echo ""
echo "安装依赖..."
npm install

if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    read -p "按Enter键退出..."
    exit 1
fi

echo ""
echo "===================================="
echo "  启动开发服务器..."
echo "===================================="
echo ""
echo "前端地址: http://localhost:3000"
echo "后端地址: http://127.0.0.1:5000"
echo ""
echo "确保后端已启动 (python ../python/app.py)"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

npm run dev
