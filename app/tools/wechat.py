"""微信公众号文章解析工具 - 提取文章标题、作者和正文"""

import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.tools.base import BaseParseTool, ParseResult
from app.utils.logger import logger


class WeChatArticleTool(BaseParseTool):
    """
    微信公众号文章解析器
    通过 HTTP 抓取页面 HTML，使用 BeautifulSoup 解析正文。
    微信文章页面服务端渲染，无需无头浏览器。
    """

    name = "wechat_article_parser"
    description = "解析微信公众号文章，提取标题、公众号名称和正文内容"
    platform = "wechat"

    PATTERNS = ["mp.weixin.qq.com", "weixin.qq.com"]

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return any(p in url.lower() for p in cls.PATTERNS)

    async def parse(self, url: str) -> ParseResult:
        """解析微信公众号文章"""
        logger.info(f"开始解析微信公众号文章: {url}")

        async with httpx.AsyncClient(
            headers=self.HEADERS,
            timeout=30,
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

            html = resp.text
            soup = BeautifulSoup(html, "lxml")

            # 提取标题
            title = self._extract_title(soup)

            # 提取公众号名称 (作者)
            author = self._extract_author(soup)

            # 提取正文
            content = self._extract_content(soup)

            # 提取发布时间
            publish_time = self._extract_publish_time(html)

            # 提取摘要
            description = self._extract_description(soup)

            return ParseResult(
                title=title,
                author=author,
                content=content,
                description=description,
                platform=self.platform,
                original_url=url,
                extra={
                    "publish_time": publish_time,
                    "word_count": len(content) if content else 0,
                },
            )

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> Optional[str]:
        """提取文章标题"""
        # 尝试多种选择器
        selectors = [
            "h1#activity-name",
            "h1.rich_media_title",
            'meta[property="og:title"]',
        ]
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == "meta":
                    return elem.get("content", "").strip()
                return elem.get_text(strip=True)
        return None

    @staticmethod
    def _extract_author(soup: BeautifulSoup) -> Optional[str]:
        """提取公众号名称"""
        selectors = [
            "a#js_name",
            "span.rich_media_meta_nickname",
            'meta[property="og:article:author"]',
        ]
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == "meta":
                    return elem.get("content", "").strip()
                return elem.get_text(strip=True)
        return None

    @staticmethod
    def _extract_content(soup: BeautifulSoup) -> str:
        """提取文章正文"""
        content_div = soup.select_one("div#js_content") or soup.select_one(
            "div.rich_media_content"
        )
        if not content_div:
            return "未能提取文章正文"

        # 移除脚本和样式标签
        for tag in content_div.find_all(["script", "style"]):
            tag.decompose()

        # 获取纯文本，保留段落换行
        paragraphs = []
        for elem in content_div.find_all(["p", "section", "h2", "h3", "h4", "blockquote"]):
            text = elem.get_text(strip=True)
            if text:
                paragraphs.append(text)

        if paragraphs:
            return "\n\n".join(paragraphs)

        # fallback: 直接获取全部文本
        return content_div.get_text(separator="\n", strip=True)

    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> Optional[str]:
        """提取文章摘要"""
        meta = soup.select_one('meta[name="description"]') or soup.select_one(
            'meta[property="og:description"]'
        )
        if meta:
            return meta.get("content", "").strip()
        return None

    @staticmethod
    def _extract_publish_time(html: str) -> Optional[str]:
        """从 HTML 源码中提取发布时间"""
        # 微信文章中的发布时间通常嵌入在 JS 变量中
        patterns = [
            r'var\s+ct\s*=\s*"(\d+)"',
            r'"create_time"\s*:\s*"?(\d+)"?',
            r's="(\d{10})"',
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        return None
