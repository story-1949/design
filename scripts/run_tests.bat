@echo off
REM 运行测试脚本（Windows）

echo 🧪 运行测试...
echo ===============

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 运行测试
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

echo.
echo ✅ 测试完成！
echo 📊 查看覆盖率报告: htmlcov\index.html
pause
