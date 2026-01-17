from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class IntentClassifier:
    """意图分类器 - 识别用户意图和提取实体"""

    def __init__(self):
        # 意图关键词映射
        self.intent_patterns = {
            "search_product": [
                r"找|搜|推荐|有没有|想买|看看",
                r"什么.*好|哪个.*好|求推荐"
            ],
            "ask_price": [
                r"多少钱|价格|贵不贵|便宜",
                r".*价|.*费"
            ],
            "ask_stock": [
                r"有货|库存|还有吗|能买吗",
                r"什么时候.*货"
            ],
            "order_query": [
                r"订单|查.*单|物流|快递|发货",
                r"什么时候.*到|追踪"
            ],
            "return_refund": [
                r"退货|退款|换货|不想要",
                r"质量问题|不满意"
            ],
            "ask_usage": [
                r"怎么用|使用方法|教程|说明",
                r"如何.*|怎样.*"
            ],
            "compare": [
                r"对比|比较|区别|哪个好",
                r".*和.*区别"
            ],
            "complaint": [
                r"投诉|差评|不满|骗人",
                r"态度.*差|服务.*差"
            ]
        }

        # 实体提取模式
        self.entity_patterns = {
            "product_name": r"(iPhone|MacBook|AirPods|iPad|Nike|Adidas|戴森|小米|华为)",
            "color": r"(红色|蓝色|黑色|白色|金色|银色|粉色|绿色)",
            "size": r"(XS|S|M|L|XL|XXL|加大|加小|\d+码)",
            "price_range": r"(\d+).*到.*(\d+)|(\d+).*以下|(\d+).*以上",
            "order_number": r"订单号[:：]?\s*([A-Z0-9]{10,})"
        }

    async def classify(
            self,
            message: str,
            history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        分类用户意图并提取实体

        Args:
            message: 用户消息
            history: 对话历史

        Returns:
            {
                "intent": "意图类型",
                "confidence": 0.95,
                "entities": {...}
            }
        """
        try:
            # 识别意图
            intent, confidence = self._classify_intent(message)

            # 提取实体
            entities = self._extract_entities(message)

            # 考虑上下文（如果有历史记录）
            if history and len(history) > 0:
                context_intent = self._infer_from_context(message, history)
                if context_intent:
                    intent = context_intent

            logger.info(f"意图分类: {intent} (置信度: {confidence:.2f})")

            return {
                "intent": intent,
                "confidence": confidence,
                "entities": entities
            }

        except Exception as e:
            logger.error(f"意图分类失败: {str(e)}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {}
            }

    def _classify_intent(self, message: str) -> tuple:
        """分类意图"""
        message_lower = message.lower()

        # 匹配所有意图模式
        matches = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            if score > 0:
                matches[intent] = score

        # 如果没有匹配，返回通用意图
        if not matches:
            return "general_inquiry", 0.5

        # 返回得分最高的意图
        best_intent = max(matches.items(), key=lambda x: x[1])
        confidence = min(best_intent[1] * 0.3 + 0.4, 1.0)

        return best_intent[0], confidence

    def _extract_entities(self, message: str) -> Dict:
        """提取实体"""
        entities = {}

        for entity_type, pattern in self.entity_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                if entity_type == "price_range":
                    # 处理价格范围
                    groups = [g for g in match.groups() if g]
                    if len(groups) >= 2:
                        entities["min_price"] = int(groups[0])
                        entities["max_price"] = int(groups[1])
                    elif len(groups) == 1:
                        if "以下" in message:
                            entities["max_price"] = int(groups[0])
                        elif "以上" in message:
                            entities["min_price"] = int(groups[0])
                else:
                    entities[entity_type] = match.group(1)

        return entities

    def _infer_from_context(
            self,
            message: str,
            history: List[Dict]
    ) -> Optional[str]:
        """从上下文推断意图"""
        if not history:
            return None

        # 获取最近的对话
        recent_messages = [msg for msg in history[-5:] if msg.get("role") == "user"]

        if not recent_messages:
            return None

        # 简单的上下文推断逻辑
        # 如果用户说"是的"、"对"、"好的"等，可能是在确认之前的操作
        confirmation_words = ["是", "对", "好", "行", "可以", "yes", "ok"]
        if any(word in message.lower() for word in confirmation_words):
            # 查看上一轮助手的回复，推断用户在确认什么
            for msg in reversed(history):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "").lower()
                    if "购买" in content or "下单" in content:
                        return "confirm_purchase"
                    elif "退货" in content:
                        return "confirm_return"
                    break

        return None