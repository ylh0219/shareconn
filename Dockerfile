FROM python:3.12-slim

WORKDIR /code

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制项目文件
COPY pyproject.toml uv.lock* ./

# 安装依赖
RUN uv sync --no-dev --no-install-project

# 复制源码
COPY . .

# 暴露端口
EXPOSE 8000

# 默认启动命令
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
