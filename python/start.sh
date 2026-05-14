#!/bin/bash

echo "===================================="
echo "  学生管理系统启动脚本"
echo "===================================="
echo ""

echo "检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "[错误] 未找到Python，请先安装Python 3.8+"
    echo "下载地址: https://www.python.org/downloads/"
    read -p "按Enter键退出..."
    exit 1
fi

echo ""
echo "安装依赖..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    read -p "按Enter键退出..."
    exit 1
fi

echo ""
echo "===================================="
echo "  启动API服务..."
echo "===================================="
echo ""
echo "访问地址: http://127.0.0.1:5000"
echo "API文档: http://127.0.0.1:5000/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py
