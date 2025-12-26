"""Text processing utilities for rumor detection."""

import re
from typing import List

import jieba


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.

    Args:
        text: Raw text input

    Returns:
        Cleaned text
    """
    # Remove URLs
    text = re.sub(r"http[s]?://\S+", "", text)

    # Remove @mentions
    text = re.sub(r"@\S+", "", text)

    # Remove hashtags (keep the text, remove #)
    text = re.sub(r"#(\S+)#", r"\1", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def segment_text(text: str) -> List[str]:
    """
    Segment Chinese text into words using jieba.

    Args:
        text: Text to segment

    Returns:
        List of words
    """
    # Clean text first
    cleaned = clean_text(text)

    # Segment using jieba
    words = jieba.cut(cleaned, cut_all=False)

    # Filter out single characters and common stopwords
    stopwords = {
        "的", "了", "是", "在", "我", "有", "和", "就", "不", "人",
        "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
        "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "他",
    }

    filtered = [
        word.strip()
        for word in words
        if len(word.strip()) > 1 and word.strip() not in stopwords
    ]

    return filtered


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extract keywords from text.

    Args:
        text: Text to analyze
        top_n: Number of keywords to extract

    Returns:
        List of keywords
    """
    import jieba.analyse

    keywords = jieba.analyse.extract_tags(text, topK=top_n)
    return list(keywords)


def detect_exaggeration_patterns(text: str) -> List[str]:
    """
    Detect common exaggeration patterns in text.

    Args:
        text: Text to analyze

    Returns:
        List of detected patterns
    """
    patterns = []

    # Check for exaggerated numbers
    if re.search(r"[0-9]+万|[0-9]+亿|数万|数十万|数百万", text):
        patterns.append("large_numbers")

    # Check for urgent language
    urgent_words = ["紧急", "速看", "快转", "震惊", "惊爆", "重磅", "突发"]
    for word in urgent_words:
        if word in text:
            patterns.append(f"urgent_language:{word}")

    # Check for vague sources
    vague_sources = ["据说", "听说", "有人说", "网传", "传言"]
    for source in vague_sources:
        if source in text:
            patterns.append(f"vague_source:{source}")

    # Check for emotional manipulation
    emotional_words = ["一定要看", "不转不是", "良心", "必须转发"]
    for word in emotional_words:
        if word in text:
            patterns.append(f"emotional_manipulation:{word}")

    return patterns
