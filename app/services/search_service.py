from typing import List, Dict, Optional
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """商品搜索服务"""

    def __init__(self):
        self.db = None

    async def search(
            self,
            query: str,
            category: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            sort_by: str = "relevance",
            page: int = 1,
            page_size: int = 20
    ) -> Dict:
        """
        搜索商品
        """
        try:
            # 模拟搜索逻辑（实际应该连接数据库或搜索引擎）
            # 这里提供示例数据

            # 计算偏移量
            offset = (page - 1) * page_size

            # 模拟数据库查询
            products = self._mock_search(
                query, category, min_price, max_price, sort_by
            )

            # 分页
            total = len(products)
            paginated_products = products[offset:offset + page_size]

            return {
                "total": total,
                "products": paginated_products
            }

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            raise

    async def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """根据 ID 获取商品详情"""
        try:
            # 模拟数据
            products = self._get_mock_products()
            for product in products:
                if product["id"] == product_id:
                    return product
            return None
        except Exception as e:
            logger.error(f"获取商品失败: {str(e)}")
            raise

    async def get_categories(self) -> List[str]:
        """获取所有分类"""
        return [
            "电子产品",
            "服装鞋包",
            "家居生活",
            "美妆个护",
            "食品饮料",
            "运动户外",
            "图书音像",
            "母婴玩具"
        ]

    async def get_trending_products(self, limit: int = 10) -> List[Dict]:
        """获取热门商品"""
        products = self._get_mock_products()
        # 按评分排序
        sorted_products = sorted(
            products,
            key=lambda x: x.get("rating", 0) * x.get("reviews_count", 0),
            reverse=True
        )
        return sorted_products[:limit]

    async def get_suggestions(self, query: str) -> List[str]:
        """获取搜索建议"""
        # 模拟搜索建议
        all_suggestions = [
            "iPhone 15 Pro",
            "MacBook Pro",
            "AirPods Pro",
            "运动鞋",
            "连衣裙",
            "笔记本电脑",
            "无线耳机",
            "智能手表"
        ]

        # 简单的模糊匹配
        suggestions = [s for s in all_suggestions if query.lower() in s.lower()]
        return suggestions[:5]

    def _mock_search(
            self,
            query: str,
            category: Optional[str],
            min_price: Optional[float],
            max_price: Optional[float],
            sort_by: str
    ) -> List[Dict]:
        """模拟搜索"""
        products = self._get_mock_products()

        # 关键词过滤
        if query:
            query_lower = query.lower()
            products = [
                p for p in products
                if query_lower in p["name"].lower()
                   or query_lower in p["description"].lower()
            ]

        # 分类过滤
        if category:
            products = [p for p in products if p["category"] == category]

        # 价格过滤
        if min_price is not None:
            products = [p for p in products if p["price"] >= min_price]
        if max_price is not None:
            products = [p for p in products if p["price"] <= max_price]

        # 排序
        if sort_by == "price_asc":
            products.sort(key=lambda x: x["price"])
        elif sort_by == "price_desc":
            products.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "rating":
            products.sort(key=lambda x: x.get("rating", 0), reverse=True)

        return products

    def _get_mock_products(self) -> List[Dict]:
        """获取模拟商品数据"""
        return [
            {
                "id": "p001",
                "name": "iPhone 15 Pro Max 256GB",
                "description": "Apple 最新旗舰手机，钛金属边框，A17 Pro 芯片",
                "price": 9999.00,
                "category": "电子产品",
                "image_url": "https://example.com/iphone15.jpg",
                "rating": 4.8,
                "reviews_count": 1520,
                "stock": 50
            },
            {
                "id": "p002",
                "name": "Nike Air Max 270 运动鞋",
                "description": "经典气垫跑鞋，舒适透气",
                "price": 899.00,
                "category": "运动户外",
                "image_url": "https://example.com/nike.jpg",
                "rating": 4.6,
                "reviews_count": 890,
                "stock": 120
            },
            {
                "id": "p003",
                "name": "戴森 V15 无线吸尘器",
                "description": "激光探测技术，深度清洁",
                "price": 4990.00,
                "category": "家居生活",
                "image_url": "https://example.com/dyson.jpg",
                "rating": 4.9,
                "reviews_count": 650,
                "stock": 30
            },
            {
                "id": "p004",
                "name": "雅诗兰黛小棕瓶精华液 50ml",
                "description": "经典修护精华，改善肌肤状态",
                "price": 780.00,
                "category": "美妆个护",
                "image_url": "https://example.com/estee.jpg",
                "rating": 4.7,
                "reviews_count": 2340,
                "stock": 200
            },
            {
                "id": "p005",
                "name": "优衣库羽绒服",
                "description": "轻薄保暖，时尚百搭",
                "price": 499.00,
                "category": "服装鞋包",
                "image_url": "https://example.com/uniqlo.jpg",
                "rating": 4.5,
                "reviews_count": 3200,
                "stock": 500
            }
        ]