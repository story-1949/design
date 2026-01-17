# 项目总览

## 📁 项目结构

```
ai-ecommerce-bot/
├── app/                          # 应用主目录
│   ├── __init__.py              # 应用包初始化
│   ├── core/                    # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理
│   │   └── database.py         # 数据库配置
│   ├── routes/                  # API 路由
│   │   ├── __init__.py
│   │   ├── chat.py             # 对话接口
│   │   └── search.py           # 搜索接口
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── copilot_client.py  # AI 客户端
│   │   ├── intent_classifier.py # 意图分类
│   │   ├── search_service.py   # 搜索服务
│   │   └── session_manager.py  # 会话管理
│   ├── middleware/              # 中间件
│   │   ├── __init__.py
│   │   └── rate_limit.py       # 限流中间件
│   └── utils/                   # 工具模块
│       ├── __init__.py
│       ├── cache.py            # 缓存工具
│       ├── exceptions.py       # 自定义异常
│       ├── helpers.py          # 辅助函数
│       ├── logger.py           # 日志配置
│       └── rate_limiter.py     # 限流工具
├── tests/                       # 测试文件
│   └── test_chat.py
├── scripts/                     # 脚本文件
│   ├── setup.bat               # Windows 初始化
│   ├── setup.sh                # Linux/Mac 初始化
│   ├── run_tests.bat           # Windows 测试
│   └── run_tests.sh            # Linux/Mac 测试
├── logs/                        # 日志目录（自动创建）
├── main.py                      # 应用入口
├── requirements.txt             # Python 依赖
├── pyproject.toml              # 项目配置
├── Dockerfile                   # Docker 镜像
├── docker-compose.yml          # Docker Compose
├── alembic.ini                 # 数据库迁移配置
├── Makefile                    # 快捷命令
├── .env.example                # 环境变量模板
├── .gitignore                  # Git 忽略文件
├── README.md                   # 项目说明
├── QUICK_START.md              # 快速开始
├── CONTRIBUTING.md             # 贡献指南
├── CHANGELOG.md                # 更新日志
└── OPTIMIZATION_SUMMARY.md     # 优化总结
```

## 🎯 核心功能模块

### 1. 配置管理 (app/core/config.py)
- 环境变量管理
- 配置单例模式
- 环境判断（开发/生产）

### 2. 数据库 (app/core/database.py)
- SQLAlchemy ORM
- 连接池管理
- 数据模型定义
- 索引优化

### 3. AI 客户端 (app/services/copilot_client.py)
- Claude API 封装
- 单例模式
- 超时控制
- 缓存优化

### 4. 意图分类 (app/services/intent_classifier.py)
- 正则匹配
- 实体提取
- 上下文推断

### 5. 搜索服务 (app/services/search_service.py)
- 商品搜索
- 分类筛选
- 价格过滤
- 排序功能

### 6. 会话管理 (app/services/session_manager.py)
- 会话创建/获取
- 历史记录管理
- 自动过期清理
- 单例模式

### 7. 缓存系统 (app/utils/cache.py)
- 内存缓存
- TTL 支持
- 装饰器模式

### 8. 限流系统 (app/utils/rate_limiter.py)
- 滑动窗口算法
- IP 限流
- 剩余次数查询

### 9. 异常处理 (app/utils/exceptions.py)
- 自定义异常类
- 业务异常
- 错误码管理

### 10. 日志系统 (app/utils/logger.py)
- 统一日志格式
- 文件和控制台输出
- 日志级别控制

## 🔄 请求流程

```
客户端请求
    ↓
限流中间件 (rate_limit.py)
    ↓
路由层 (routes/)
    ↓
意图识别 (intent_classifier.py)
    ↓
会话管理 (session_manager.py)
    ↓
AI 处理 (copilot_client.py)
    ↓
业务逻辑 (services/)
    ↓
数据库操作 (database.py)
    ↓
响应返回
```

## 📊 数据流

```
用户消息
    ↓
[意图识别] → 识别用户意图和实体
    ↓
[会话管理] → 获取历史对话上下文
    ↓
[AI 处理] → Claude 生成回复
    ↓
[业务逻辑] → 商品搜索/推荐
    ↓
[数据存储] → 保存对话历史
    ↓
返回结果
```

## 🔧 配置项说明

### 必需配置
- `ANTHROPIC_API_KEY`: Claude API 密钥

### 应用配置
- `APP_NAME`: 应用名称
- `DEBUG`: 调试模式
- `ENVIRONMENT`: 环境（development/production）
- `HOST`: 监听地址
- `PORT`: 监听端口

### AI 配置
- `COPILOT_MODEL`: AI 模型
- `MAX_TOKENS`: 最大 token 数
- `TEMPERATURE`: 温度参数
- `AI_TIMEOUT`: 请求超时

### 数据库配置
- `DATABASE_URL`: 数据库连接
- `DATABASE_POOL_SIZE`: 连接池大小
- `DATABASE_MAX_OVERFLOW`: 最大溢出连接

### 缓存配置
- `CACHE_TTL`: 缓存过期时间
- `ENABLE_CACHE`: 是否启用缓存

### 限流配置
- `RATE_LIMIT_ENABLED`: 是否启用限流
- `RATE_LIMIT_REQUESTS`: 每分钟最大请求数
- `RATE_LIMIT_WINDOW`: 时间窗口

### 会话配置
- `SESSION_TIMEOUT`: 会话超时时间
- `MAX_CONVERSATION_HISTORY`: 最大对话历史

## 🚀 部署方式

### 1. 本地开发
```bash
python main.py
```

### 2. Docker 单容器
```bash
docker build -t ai-ecommerce-bot .
docker run -p 8000:8000 ai-ecommerce-bot
```

### 3. Docker Compose（推荐）
```bash
docker-compose up -d
```

### 4. 生产部署
- 使用 Gunicorn/Uvicorn workers
- Nginx 反向代理
- PostgreSQL 数据库
- Redis 缓存
- 负载均衡

## 📈 性能指标

### 响应时间
- 健康检查: < 10ms
- 简单对话: < 2s
- AI 增强搜索: < 3s
- 复杂对话: < 5s

### 并发能力
- 单实例: ~100 并发
- 多实例: 水平扩展

### 资源占用
- 内存: ~200MB (基础)
- CPU: 1-2 核心
- 磁盘: ~100MB (代码)

## 🔒 安全措施

1. **输入验证**: Pydantic 模型验证
2. **限流保护**: 防止 API 滥用
3. **异常处理**: 全局异常捕获
4. **日志记录**: 详细的操作日志
5. **环境隔离**: 开发/生产环境分离
6. **敏感信息**: 环境变量管理

## 🧪 测试策略

### 单元测试
- 服务层测试
- 工具函数测试
- 意图分类测试

### 集成测试
- API 接口测试
- 数据库操作测试
- 会话管理测试

### 性能测试
- 压力测试
- 并发测试
- 响应时间测试

## 📚 技术选型理由

### FastAPI
- 高性能异步框架
- 自动 API 文档
- 类型验证
- 现代 Python 特性

### Anthropic Claude
- 强大的语言理解
- 长上下文支持
- 可靠的 API
- 良好的中文支持

### SQLAlchemy
- 成熟的 ORM
- 多数据库支持
- 连接池管理
- 迁移工具

### Docker
- 环境一致性
- 快速部署
- 易于扩展
- 资源隔离

## 🎓 学习资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Anthropic API 文档](https://docs.anthropic.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Docker 文档](https://docs.docker.com/)

## 🤝 团队协作

### 开发流程
1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 提交 Pull Request
5. 代码审查
6. 合并主分支

### 代码规范
- 使用 Black 格式化
- 遵循 PEP 8
- 添加类型提示
- 编写文档字符串

### 提交规范
- feat: 新功能
- fix: 修复
- docs: 文档
- refactor: 重构
- test: 测试

## 📞 联系方式

- GitHub Issues: 报告问题
- Pull Requests: 贡献代码
- Discussions: 讨论交流

---

**版本**: 1.0.0  
**最后更新**: 2025-01-17  
**维护者**: Your Team
