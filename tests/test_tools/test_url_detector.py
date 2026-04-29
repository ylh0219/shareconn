"""URL 检测工具测试"""

from app.utils.url_detector import detect_platform, extract_urls, is_url


def test_detect_bilibili():
    assert detect_platform("https://www.bilibili.com/video/BV1xx411c7mD") == "bilibili"
    assert detect_platform("https://b23.tv/abc123") == "bilibili"


def test_detect_wechat():
    assert detect_platform("https://mp.weixin.qq.com/s/abc123") == "wechat"


def test_detect_generic():
    assert detect_platform("https://example.com/article") is None


def test_extract_urls():
    text = "看看这个 https://bilibili.com/video/BV123 还有这个 https://example.com"
    urls = extract_urls(text)
    assert len(urls) == 2


def test_is_url():
    assert is_url("https://example.com") is True
    assert is_url("just some text") is False
