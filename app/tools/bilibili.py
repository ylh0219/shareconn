"""B站视频解析工具 - 提取视频标题、UP主、简介、字幕和时长"""

import re
from typing import Optional

import httpx

from app.tools.base import BaseParseTool, ParseResult
from app.utils.logger import logger


class BilibiliParserTool(BaseParseTool):
    """
    Bilibili 视频解析器
    通过 B 站公开 API 获取视频信息，
    尝试提取字幕文本作为主要内容。
    """

    name = "bilibili_parser"
    description = "解析 B 站视频，提取标题、UP主、简介、字幕和时长"
    platform = "bilibili"

    PATTERNS = ["bilibili.com", "b23.tv"]

    # B站 API 端点
    VIDEO_INFO_API = "https://api.bilibili.com/x/web-interface/view"
    SUBTITLE_API = "https://api.bilibili.com/x/player/v2"

    # 通用请求头 (模拟浏览器)
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.bilibili.com",
    }

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return any(p in url.lower() for p in cls.PATTERNS)

    async def parse(self, url: str) -> ParseResult:
        """解析 B 站视频"""
        bvid = self._extract_bvid(url)
        if not bvid:
            raise ValueError(f"无法从 URL 中提取 BV 号: {url}")

        logger.info(f"开始解析 B 站视频: bvid={bvid}")

        async with httpx.AsyncClient(headers=self.HEADERS, timeout=30) as client:
            # 1. 获取视频基本信息
            video_data = await self._fetch_video_info(client, bvid)

            # 2. 尝试获取字幕
            subtitle_text = await self._fetch_subtitle(
                client, bvid, video_data.get("cid", 0)
            )

            # 3. 构造内容: 优先使用字幕，否则使用简介
            content_parts = []
            if video_data.get("desc"):
                content_parts.append(f"【视频简介】\n{video_data['desc']}")
            if subtitle_text:
                content_parts.append(f"【字幕内容】\n{subtitle_text}")

            content = "\n\n".join(content_parts) if content_parts else "未能获取视频内容"

            return ParseResult(
                title=video_data.get("title"),
                author=video_data.get("owner", {}).get("name"),
                content=content,
                description=video_data.get("desc"),
                duration_seconds=video_data.get("duration"),
                cover_url=video_data.get("pic"),
                platform=self.platform,
                original_url=url,
                extra={
                    "bvid": bvid,
                    "aid": video_data.get("aid"),
                    "view_count": video_data.get("stat", {}).get("view"),
                    "like_count": video_data.get("stat", {}).get("like"),
                    "tags": video_data.get("tname"),
                },
            )

    async def _fetch_video_info(self, client: httpx.AsyncClient, bvid: str) -> dict:
        """获取视频基本信息"""
        resp = await client.get(self.VIDEO_INFO_API, params={"bvid": bvid})
        resp.raise_for_status()

        data = resp.json()
        if data.get("code") != 0:
            raise ValueError(f"B站 API 返回错误: {data.get('message', '未知错误')}")

        return data.get("data", {})

    async def _fetch_subtitle(
        self, client: httpx.AsyncClient, bvid: str, cid: int
    ) -> Optional[str]:
        """尝试获取视频字幕"""
        try:
            resp = await client.get(
                self.SUBTITLE_API,
                params={"bvid": bvid, "cid": cid},
            )
            resp.raise_for_status()
            data = resp.json()

            subtitle_info = (
                data.get("data", {})
                .get("subtitle", {})
                .get("subtitles", [])
            )

            if not subtitle_info:
                logger.debug(f"视频 {bvid} 没有字幕")
                return None

            # 获取第一个字幕（通常是中文）
            subtitle_url = subtitle_info[0].get("subtitle_url", "")
            if subtitle_url.startswith("//"):
                subtitle_url = "https:" + subtitle_url

            if not subtitle_url:
                return None

            # 下载字幕 JSON
            sub_resp = await client.get(subtitle_url)
            sub_resp.raise_for_status()
            sub_data = sub_resp.json()

            # 拼接字幕文本
            lines = [
                item.get("content", "")
                for item in sub_data.get("body", [])
            ]
            return "\n".join(lines) if lines else None

        except Exception as e:
            logger.warning(f"获取字幕失败: {e}")
            return None

    @staticmethod
    def _extract_bvid(url: str) -> Optional[str]:
        """从 URL 中提取 BV 号"""
        # 匹配 BV 号模式
        match = re.search(r'(BV[a-zA-Z0-9]+)', url)
        return match.group(1) if match else None
