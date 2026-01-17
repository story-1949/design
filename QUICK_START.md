# 快速开始指南

## 🚀 5分钟快速启动

### Windows 用户

```bash
# 1. 运行初始化脚本
scripts\setup.bat

# 2. 编辑 .env 文件，设置你的 API Key
notepad .env

# 3. 启动应用
python main.py
```

### Linux/Mac 用户

```bash
# 1. 给脚本添加执行权限
chmod +x scripts/setup.sh scripts/run_tests.sh

# 2. 运行初始化脚本
./scripts/setup.sh

# 3. 编辑 .env 文件，设置你的 API Key
nano .env

# 4. 启动应用
python main.py
```

### Docker 用户

```bash
# 1. 复制环境变量文件
cp .env.example .env

# 2. 编辑 .env，设置 ANTHROPIC_API_KEY
nano .env

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f app
```

## 📝 必需配置

在 `.env` 文件中设置：

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

获取 API Key：https://console.anthropic.com/

## 🧪 测试 API

### 1. 访问文档

打开浏览器访问：http://localhost:8000/docs

### 2. 测试对话

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

### 3. 测试搜索

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "手机", "use_ai": true}'
```

## 🔧 常用命令

### 开发模式

```bash
# 启动开发服务器（自动重载）
uvicorn main:app --reload

# 或使用 make
make dev
```

### 运行测试

```bash
# Windows
scripts\run_tests.bat

# Linux/Mac
./scripts/run_tests.sh

# 或使用 make
make test
```

### 代码格式化

```bash
make format
```

### 代码检查

```bash
make lint
```

## 📊 查看日志

```bash
# 实时查看日志
tail -f logs/app.log

# Windows
type logs\app.log
```

## 🐳 Docker 命令

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart app
```

## ❓ 常见问题

### 1. 端口被占用

修改 `.env` 文件中的 `PORT` 配置：

```bash
PORT=8001
```

### 2. API Key 无效

确保在 `.env` 文件中正确设置了 `ANTHROPIC_API_KEY`

### 3. 数据库连接失败

检查 `DATABASE_URL` 配置，默认使用 SQLite，无需额外配置

### 4. 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

## 📚 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 [API 文档](http://localhost:8000/docs)
- 阅读 [优化总结](OPTIMIZATION_SUMMARY.md) 了解代码改进
- 参考 [贡献指南](CONTRIBUTING.md) 参与开发

## 💡 提示

- 开发环境使用 SQLite，生产环境建议使用 PostgreSQL
- 启用 Redis 可以提升性能
- 查看 `app/core/config.py` 了解所有配置项
- 使用 `make help` 查看所有可用命令

## 🆘 获取帮助

遇到问题？

1. 查看日志文件：`logs/app.log`
2. 检查配置文件：`.env`
3. 提交 Issue：[GitHub Issues](your-repo-url/issues)

祝你使用愉快！🎉
