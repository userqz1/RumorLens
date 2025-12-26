"""DeepSeek API integration service."""

import json
import logging
from typing import Optional

import httpx

from app.core.config import settings
from app.schemas.detection import AnalysisResult

logger = logging.getLogger(__name__)


class DeepSeekService:
    """Service for interacting with DeepSeek API."""

    DETECTION_PROMPT = """你是一个专业的谣言检测分析师。请分析以下微博文本，判断其是否为谣言。

## 待分析文本
{content}

## 分析要求
1. 判断该文本是否为谣言（is_rumor: true/false）
2. 给出可信度评分（confidence: 0.0-1.0，1.0表示完全可信，0.0表示完全不可信）
3. 提供详细的分析说明（explanation）
4. 提取关键词（keywords）
5. 判断情感倾向（sentiment: positive/negative/neutral）
6. 分类（category: 政治/健康/社会/科技/娱乐/财经/其他）
7. 列出事实核查要点（fact_check_points）
8. 列出风险指标（risk_indicators）

## 输出格式
请严格以JSON格式输出，结构如下：
```json
{{
  "is_rumor": boolean,
  "confidence": float,
  "explanation": "string",
  "keywords": ["string"],
  "sentiment": "string",
  "category": "string",
  "fact_check_points": ["string"],
  "risk_indicators": ["string"]
}}
```

## 判断标准
- 信息来源是否可靠
- 是否有夸大、煽动性表述
- 是否违背常识或科学原理
- 是否存在逻辑漏洞
- 是否可被官方渠道证实
- 是否使用模糊的时间地点描述
- 是否包含未经证实的数据

请只输出JSON，不要输出其他内容。"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_base = settings.DEEPSEEK_API_BASE
        self.model = settings.DEEPSEEK_MODEL
        self.timeout = 60.0

    async def detect_rumor(
        self,
        content: str,
    ) -> dict:
        """
        Detect if content is a rumor using DeepSeek API.

        Args:
            content: The text content to analyze

        Returns:
            Detection result dictionary
        """
        prompt = self.DETECTION_PROMPT.format(content=content)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是一个专业的谣言检测分析师，擅长分析社交媒体内容的真实性。请始终以JSON格式输出分析结果。",
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],
                        "temperature": 0.1,
                        "max_tokens": 2000,
                    },
                )

                if response.status_code != 200:
                    logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                    return self._get_fallback_result(content)

                result = response.json()
                content_text = result["choices"][0]["message"]["content"]

                # Parse JSON from response
                return self._parse_response(content_text)

        except httpx.TimeoutException:
            logger.error("DeepSeek API timeout")
            return self._get_fallback_result(content)
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return self._get_fallback_result(content)

    def _parse_response(self, content: str) -> dict:
        """Parse JSON response from DeepSeek."""
        try:
            # Try to extract JSON from markdown code block
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()

            result = json.loads(content)

            # Validate and normalize result
            return {
                "is_rumor": bool(result.get("is_rumor", False)),
                "confidence": float(result.get("confidence", 0.5)),
                "explanation": str(result.get("explanation", "")),
                "keywords": list(result.get("keywords", [])),
                "sentiment": str(result.get("sentiment", "neutral")),
                "category": str(result.get("category", "other")),
                "fact_check_points": list(result.get("fact_check_points", [])),
                "risk_indicators": list(result.get("risk_indicators", [])),
            }
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse DeepSeek response: {e}")
            return self._get_fallback_result("")

    def _get_fallback_result(self, content: str) -> dict:
        """Get fallback result when API fails."""
        return {
            "is_rumor": False,
            "confidence": 0.5,
            "explanation": "Unable to analyze content due to service error. Please try again later.",
            "keywords": [],
            "sentiment": "neutral",
            "category": "other",
            "fact_check_points": ["Manual verification required"],
            "risk_indicators": ["Analysis incomplete"],
        }

    def extract_analysis(self, result: dict) -> AnalysisResult:
        """Extract analysis result from detection result."""
        return AnalysisResult(
            keywords=result.get("keywords", []),
            sentiment=result.get("sentiment", "neutral"),
            category=result.get("category", "other"),
            sources=result.get("sources", []),
            fact_check_points=result.get("fact_check_points", []),
            risk_indicators=result.get("risk_indicators", []),
        )
