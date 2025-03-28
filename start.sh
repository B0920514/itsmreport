#!/bin/bash

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 first."
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 启动应用
echo "Starting the application..."
python app.py 