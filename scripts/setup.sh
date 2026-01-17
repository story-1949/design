#!/bin/bash
# 项目初始化脚本（Linux/Mac）

echo "🚀 AI 电商机器人 - 项目初始化"
echo "================================"

# 检查 Python 版本
echo "📌 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv .venv

# 激活虚拟环境
echo "✅ 激活虚拟环境..."
source .venv/bin/activate

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 复制环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，填入你的 ANTHROPIC_API_KEY"
fi

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 初始化数据库
echo "🗄️  初始化数据库..."
python -c "from app.core.database import init_db; init_db()"

echo ""
echo "✨ 初始化完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，设置 ANTHROPIC_API_KEY"
echo "2. 运行: python main.py"
echo "3. 访问: http://localhost:8000/docs"
echo ""
