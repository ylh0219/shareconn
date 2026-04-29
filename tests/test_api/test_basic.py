"""API 基础测试"""

import pytest


@pytest.mark.asyncio
async def test_root(client):
    """测试根路径"""
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Share Helper"


@pytest.mark.asyncio
async def test_health(client):
    """测试健康检查"""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
