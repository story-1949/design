from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.search_service import SearchService
from app.services.copilot_client import CopilotClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="搜索关键词")
    category: Optional[str] = Field(None, description="商品分类")
    min_price: Optional[float] = Field(None, ge=0, description="最低价格")
    max_price: Optional[float] = Field(None, ge=0, description="最高价格")
    sort_by: Optional[str] = Field("relevance", description="排序方式")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    use_ai: bool = Field(False, description="是否使用 AI 增强搜索")


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    stock: int = 0
    relevance_score: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    total: int
    page: int
    page_size: int
    results: List[Product]
    suggestions: Optional[List[str]] = None
    ai_insights: Optional[str] = None


search_service = SearchService()
copilot = CopilotClient()


@router.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    商品搜索接口

    支持：
    - 关键词搜索
    - 分类筛选
    - 价格范围筛选
    - 多种排序方式
    - AI 增强搜索（理解用户意图，提供个性化结果）
    """
    try:
        logger.info(f"搜索请求: {request.query}")

        # 如果启用 AI，先让 AI 理解用户意图
        enhanced_query = request.query
        ai_insights = None

        if request.use_ai:
            intent_result = await copilot.analyze_search_intent(request.query)
            enhanced_query = intent_result.get("enhanced_query", request.query)
            ai_insights = intent_result.get("insights")
            logger.info(f"AI 增强查询: {enhanced_query}")

        # 执行搜索
        results = await search_service.search(
            query=enhanced_query,
            category=request.category,
            min_price=request.min_price,
            max_price=request.max_price,
            sort_by=request.sort_by,
            page=request.page,
            page_size=request.page_size
        )

        # 获取搜索建议
        suggestions = await search_service.get_suggestions(request.query)

        return SearchResponse(
            query=request.query,
            total=results["total"],
            page=request.page,
            page_size=request.page_size,
            results=results["products"],
            suggestions=suggestions,
            ai_insights=ai_insights
        )

    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """获取商品详情"""
    try:
        product = await search_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取商品详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """获取所有商品分类"""
    try:
        categories = await search_service.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"获取分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_products(limit: int = Query(10, ge=1, le=50)):
    """获取热门商品"""
    try:
        products = await search_service.get_trending_products(limit)
        return {"products": products}
    except Exception as e:
        logger.error(f"获取热门商品失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))