@echo off
REM 项目初始化脚本（Windows）

echo 🚀 AI 电商机器人 - 项目初始化
echo ================================

REM 检查 Python 版本
echo 📌 检查 Python 版本...
python --version

REM 创建虚拟环境
echo 📦 创建虚拟环境...
python -m venv .venv

REM 激活虚拟环境
echo ✅ 激活虚拟环境...
call .venv\Scripts\activate.bat

REM 升级 pip
echo ⬆️  升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 📥 安装依赖...
pip install -r requirements.txt

REM 复制环境变量文件
if not exist .env (
    echo 📝 创建 .env 文件...
    copy .env.example .env
    echo ⚠️  请编辑 .env 文件，填入你的 ANTHROPIC_API_KEY
)

REM 创建日志目录
echo 📁 创建日志目录...
if not exist logs mkdir logs

REM 初始化数据库
echo 🗄️  初始化数据库...
python -c "from app.core.database import init_db; init_db()"

echo.
echo ✨ 初始化完成！
echo.
echo 下一步：
echo 1. 编辑 .env 文件，设置 ANTHROPIC_API_KEY
echo 2. 运行: python main.py
echo 3. 访问: http://localhost:8000/docs
echo.
pause
