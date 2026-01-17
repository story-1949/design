"""聊天接口测试"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestChatAPI:
    """聊天接口测试"""

    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_chat_without_session(self):
        """测试无会话聊天"""
        response = client.post(
            "/api/v1/chat",
            json={"message": "你好"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "message" in data

    def test_chat_with_session(self):
        """测试带会话聊天"""
        # 第一次请求
        response1 = client.post(
            "/api/v1/chat",
            json={"message": "我想买手机"}
        )
        data1 = response1.json()
        session_id = data1["session_id"]

        # 第二次请求，使用相同会话
        response2 = client.post(
            "/api/v1/chat",
            json={
                "session_id": session_id,
                "message": "有什么推荐吗？"
            }
        )
        data2 = response2.json()
        assert data2["session_id"] == session_id

    def test_get_chat_history(self):
        """测试获取聊天历史"""
        # 先创建一个会话
        response1 = client.post(
            "/api/v1/chat",
            json={"message": "测试消息"}
        )
        session_id = response1.json()["session_id"]

        # 获取历史
        response2 = client.get(f"/api/v1/chat/history/{session_id}")
        assert response2.status_code == 200
        history = response2.json()["history"]
        assert len(history) > 0

    def test_clear_session(self):
        """测试清除会话"""
        # 创建会话
        response1 = client.post(
            "/api/v1/chat",
            json={"message": "测试"}
        )
        session_id = response1.json()["session_id"]

        # 清除会话
        response2 = client.delete(f"/api/v1/chat/session/{session_id}")
        assert response2.status_code == 200

        # 尝试获取已清除的会话（应该返回 404 或创建新会话）
        response3 = client.get(f"/api/v1/chat/history/{session_id}")
        # 会话不存在时应该返回错误
        assert response3.status_code in [404, 400]


class TestSearchAPI:
    """搜索接口测试"""

    def test_basic_search(self):
        """测试基础搜索"""
        response = client.post(
            "/api/v1/search",
            json={"query": "手机"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data

    def test_search_with_filters(self):
        """测试带过滤的搜索"""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "手机",
                "min_price": 1000,
                "max_price": 5000,
                "category": "电子产品"
            }
        )
        assert response.status_code == 200
        data = response.json()

        # 验证价格过滤
        for product in data["results"]:
            assert 1000 <= product["price"] <= 5000

    def test_search_pagination(self):
        """测试分页"""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "手机",
                "page": 1,
                "page_size": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert len(data["results"]) <= 5

    def test_ai_enhanced_search(self):
        """测试 AI 增强搜索"""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "性价比高的智能手机",
                "use_ai": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        # AI 增强搜索可能返回 insights
        assert "ai_insights" in data or "results" in data

    def test_get_product_detail(self):
        """测试获取商品详情"""
        response = client.get("/api/v1/products/p001")
        assert response.status_code == 200
        product = response.json()
        assert product["id"] == "p001"

    def test_get_categories(self):
        """测试获取分类"""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0

    def test_get_trending_products(self):
        """测试获取热门商品"""
        response = client.get("/api/v1/trending?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert len(data["products"]) <= 5


@pytest.mark.asyncio
class TestIntentClassifier:
    """意图分类器测试"""

    async def test_search_intent(self):
        """测试搜索意图"""
        from app.services.intent_classifier import IntentClassifier
        classifier = IntentClassifier()

        result = await classifier.classify("我想买手机")
        assert result["intent"] == "search_product"
        assert result["confidence"] > 0

    async def test_price_inquiry(self):
        """测试价格询问"""
        from app.services.intent_classifier import IntentClassifier
        classifier = IntentClassifier()

        result = await classifier.classify("这个多少钱？")
        assert result["intent"] == "ask_price"

    async def test_entity_extraction(self):
        """测试实体提取"""
        from app.services.intent_classifier import IntentClassifier
        classifier = IntentClassifier()

        result = await classifier.classify("我想要红色的iPhone")
        entities = result.get("entities", {})
        # 检查是否提取到颜色或产品名称
        assert "color" in entities or "product_name" in entities


@pytest.mark.asyncio
class TestSessionManager:
    """会话管理器测试"""

    async def test_create_session(self):
        """测试创建会话"""
        from app.services.session_manager import SessionManager
        manager = SessionManager()

        session = await manager.create_session()
        assert "session_id" in session
        assert "created_at" in session
        assert "history" in session

    async def test_get_session(self):
        """测试获取会话"""
        from app.services.session_manager import SessionManager
        manager = SessionManager()

        # 创建会话
        session = await manager.create_session()
        session_id = session["session_id"]

        # 获取会话
        retrieved = await manager.get_session(session_id)
        assert retrieved is not None
        assert retrieved["session_id"] == session_id

    async def test_add_message(self):
        """测试添加消息"""
        from app.services.session_manager import SessionManager
        manager = SessionManager()

        session = await manager.create_session()
        session_id = session["session_id"]

        # 添加消息
        success = await manager.add_message(
            session_id,
            {"role": "user", "content": "测试消息"}
        )
        assert success is True

        # 验证消息已添加
        session = await manager.get_session(session_id)
        assert len(session["history"]) == 1
