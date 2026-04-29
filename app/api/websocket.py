"""WebSocket 端点 - 实时推送分享处理进度"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

from app.utils.logger import logger

router = APIRouter()

# 活跃 WebSocket 连接存储
# key: share_id, value: set of WebSocket connections
active_connections: Dict[int, set[WebSocket]] = {}


@router.websocket("/ws/shares/{share_id}")
async def share_progress_ws(websocket: WebSocket, share_id: int):
    """
    分享处理进度 WebSocket

    客户端连接后，实时接收处理进度更新：
    - {"step": "classified", "message": "已识别平台: bilibili"}
    - {"step": "parsed", "message": "内容解析完成"}
    - {"step": "analyzed", "message": "分析完成", "result": {...}}
    """
    await websocket.accept()

    # 注册连接
    if share_id not in active_connections:
        active_connections[share_id] = set()
    active_connections[share_id].add(websocket)

    logger.info(f"[WebSocket] 客户端连接: share_id={share_id}")

    try:
        # 保持连接，等待关闭
        while True:
            # 接收客户端消息 (心跳或其他)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        logger.info(f"[WebSocket] 客户端断开: share_id={share_id}")
    finally:
        # 清理连接
        active_connections.get(share_id, set()).discard(websocket)
        if share_id in active_connections and not active_connections[share_id]:
            del active_connections[share_id]


async def broadcast_progress(share_id: int, step: str, message: str, data: dict = None):
    """
    向指定 share_id 的所有 WebSocket 连接广播进度

    Args:
        share_id: 分享 ID
        step: 当前步骤
        message: 进度描述
        data: 额外数据 (分析结果等)
    """
    connections = active_connections.get(share_id, set())
    if not connections:
        return

    payload = json.dumps({
        "share_id": share_id,
        "step": step,
        "message": message,
        "data": data,
    }, ensure_ascii=False)

    disconnected = set()
    for ws in connections:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)

    # 清理断开的连接
    for ws in disconnected:
        connections.discard(ws)
