#!/bin/bash
# 运行测试脚本

echo "🧪 运行测试..."
echo "==============="

# 激活虚拟环境
source .venv/bin/activate

# 运行测试
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

echo ""
echo "✅ 测试完成！"
echo "📊 查看覆盖率报告: htmlcov/index.html"
