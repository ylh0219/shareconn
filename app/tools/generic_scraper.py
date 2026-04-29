"""通用网页抓取工具 - 适用于未匹配到专用 Parser 的普通网页"""

from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.tools.base import BaseParseTool, ParseResult
from app.utils.logger import logger


class GenericScraperTool(BaseParseTool):
    """
    通用网页解析器
    使用 HTTP + BeautifulSoup 抓取任意网页正文。
    采用多策略正文提取 (article 标签 → main 标签 → p 标签聚合)。
    """

    name = "generic_scraper"
    description = "抓取并解析通用网页内容，提取标题和正文"
    platform = "generic"

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
        """通用解析器作为兜底，始终返回 True"""
        return True

    async def parse(self, url: str) -> ParseResult:
        """抓取并解析网页"""
        logger.info(f"通用解析器开始抓取: {url}")

        async with httpx.AsyncClient(
            headers=self.HEADERS,
            timeout=30,
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

            # 处理编码
            html = resp.text
            soup = BeautifulSoup(html, "lxml")

            title = self._extract_title(soup)
            author = self._extract_author(soup)
            content = self._extract_content(soup)
            description = self._extract_description(soup)

            return ParseResult(
                title=title,
                author=author,
                content=content,
                description=description,
                platform=self.platform,
                original_url=url,
                extra={
                    "word_count": len(content) if content else 0,
                    "charset": resp.encoding,
                },
            )

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> Optional[str]:
        """提取页面标题"""
        # 优先使用 og:title
        og_title = soup.select_one('meta[property="og:title"]')
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # 其次使用 title 标签
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        # 最后使用 h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return None

    @staticmethod
    def _extract_author(soup: BeautifulSoup) -> Optional[str]:
        """提取作者信息"""
        selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '[class*="author"]',
            '[rel="author"]',
        ]
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == "meta":
                    return elem.get("content", "").strip() or None
                text = elem.get_text(strip=True)
                if text and len(text) < 100:
                    return text
        return None

    @staticmethod
    def _extract_content(soup: BeautifulSoup) -> str:
        """
        多策略正文提取:
        1. article 标签
        2. main 标签
        3. 最大文本密度的 div
        4. 所有 p 标签聚合
        """
        # 移除无关标签
        for tag in soup.find_all(
            ["script", "style", "nav", "header", "footer", "aside", "iframe"]
        ):
            tag.decompose()

        # 策略1: article 标签
        article = soup.find("article")
        if article:
            text = article.get_text(separator="\n", strip=True)
            if len(text) > 100:
                return text

        # 策略2: main 标签
        main = soup.find("main")
        if main:
            text = main.get_text(separator="\n", strip=True)
            if len(text) > 100:
                return text

        # 策略3: 文本密度最高的 div
        best_div = None
        best_text_len = 0
        for div in soup.find_all("div"):
            text = div.get_text(strip=True)
            # 排除过短或过长的 div (可能是整个 body)
            if 100 < len(text) < 50000 and len(text) > best_text_len:
                best_text_len = len(text)
                best_div = div

        if best_div:
            paragraphs = []
            for p in best_div.find_all(["p", "h2", "h3", "h4", "li"]):
                t = p.get_text(strip=True)
                if t and len(t) > 5:
                    paragraphs.append(t)
            if paragraphs:
                return "\n\n".join(paragraphs)

        # 策略4: 聚合所有 p 标签
        paragraphs = [
            p.get_text(strip=True)
            for p in soup.find_all("p")
            if len(p.get_text(strip=True)) > 10
        ]
        if paragraphs:
            return "\n\n".join(paragraphs)

        # Fallback: body 全文
        body = soup.find("body")
        if body:
            return body.get_text(separator="\n", strip=True)[:5000]

        return "未能提取页面内容"

    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> Optional[str]:
        """提取页面描述"""
        for selector in [
            'meta[name="description"]',
            'meta[property="og:description"]',
        ]:
            meta = soup.select_one(selector)
            if meta and meta.get("content"):
                return meta["content"].strip()
        return None
