# AI 电商机器人 🤖🛍️

一个基于 FastAPI 和 Claude AI 的智能电商助手，提供商品搜索、智能对话、订单管理等功能。

## ✨ 主要特性

- 🤖 **智能对话**：基于 Claude AI 的自然语言理解和对话生成
- 🔍 **智能搜索**：AI 增强的商品搜索，理解用户真实意图
- 💬 **多轮对话**：支持上下文管理的多轮对话
- 🎯 **意图识别**：自动识别用户意图（搜索、询价、订单查询等）
- 📦 **实体提取**：提取商品名称、颜色、尺寸、价格范围等关键信息
- 🚀 **高性能**：异步处理、缓存优化、连接池管理
- 🔒 **安全可靠**：限流保护、异常处理、日志记录
- 🐳 **容器化部署**：Docker 和 Docker Compose 支持

## 🏗️ 技术栈

- **Web 框架**：FastAPI 0.109+
- **AI 服务**：Anthropic Claude (Sonnet 4)
- **数据库**：SQLAlchemy (支持 SQLite/PostgreSQL)
- **缓存**：Redis (可选)
- **容器化**：Docker & Docker Compose
- **测试**：Pytest

## 📦 项目结构

```
.
├── app/
│   ├── core/              # 核心配置
│   │   ├── config.py      # 应用配置
│   │   └── database.py    # 数据库配置
│   ├── routes/            # API 路由
│   │   ├── chat.py        # 对话接口
│   │   └── search.py      # 搜索接口
│   ├── services/          # 业务逻辑
│   │   ├── copilot_client.py      # AI 客户端
│   │   ├── intent_classifier.py   # 意图分类
│   │   ├── search_service.py      # 搜索服务
│   │   └── session_manager.py     # 会话管理
│   ├── utils/             # 工具模块
│   │   ├── cache.py       # 缓存工具
│   │   ├── rate_limiter.py # 限流工具
│   │   ├── logger.py      # 日志配置
│   │   └── exceptions.py  # 自定义异常
│   └── middleware/        # 中间件
│       └── rate_limit.py  # 限流中间件
├── tests/                 # 测试文件
├── main.py               # 应用入口
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 配置
├── docker-compose.yml   # Docker Compose 配置
└── .env.example         # 环境变量示例
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd ai-ecommerce-bot

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# 重要：设置 ANTHROPIC_API_KEY
```

### 3. 运行应用

```bash
# 开发模式
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

### 4. Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📖 API 使用示例

### 智能对话

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想买一部性价比高的手机，预算3000左右"
  }'
```

响应：
```json
{
  "session_id": "uuid-here",
  "message": "根据您的预算，我为您推荐以下几款性价比高的手机...",
  "intent": "search_product",
  "entities": {
    "product_name": "手机",
    "min_price": 2500,
    "max_price": 3500
  },
  "products": [...]
}
```

### 商品搜索

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "iPhone",
    "min_price": 5000,
    "max_price": 10000,
    "use_ai": true
  }'
```

### 获取聊天历史

```bash
curl "http://localhost:8000/api/v1/chat/history/{session_id}"
```

## 🔧 配置说明

主要配置项（在 `.env` 文件中）：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ANTHROPIC_API_KEY` | Claude API 密钥 | 必填 |
| `DATABASE_URL` | 数据库连接 | sqlite:///./ecommerce.db |
| `REDIS_URL` | Redis 连接 | redis://localhost:6379/0 |
| `RATE_LIMIT_REQUESTS` | 每分钟最大请求数 | 100 |
| `MAX_CONVERSATION_HISTORY` | 最大对话历史轮数 | 10 |
| `AI_TIMEOUT` | AI 请求超时时间（秒） | 30 |

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_chat.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 📊 性能优化

- ✅ 异步 I/O 处理
- ✅ 数据库连接池
- ✅ Redis 缓存（可选）
- ✅ 内存缓存装饰器
- ✅ 限流保护
- ✅ 请求超时控制
- ✅ 单例模式服务

## 🔒 安全特性

- 限流保护（防止 API 滥用）
- 输入验证（Pydantic 模型）
- 异常处理（全局异常捕获）
- CORS 配置
- 环境变量管理
- 生产模式隐藏文档

## 📝 开发建议

1. **代码质量**：使用 `black` 格式化，`flake8` 检查
2. **类型提示**：使用 `mypy` 进行类型检查
3. **日志记录**：合理使用日志级别
4. **错误处理**：使用自定义异常类
5. **测试覆盖**：保持高测试覆盖率

## 🚧 待优化项

- [ ] 接入真实商品数据库
- [ ] 实现用户认证和授权
- [ ] 添加订单管理功能
- [ ] 实现支付集成
- [ ] 添加推荐算法
- [ ] 实现 WebSocket 实时通信
- [ ] 添加监控和告警
- [ ] 性能压测和优化

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请提交 Issue 或联系维护者。
