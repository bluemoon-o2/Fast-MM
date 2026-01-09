# 使用官方推荐的 Python 基础镜像
FROM docker.m.daocloud.io/python:3.12-slim AS builder

# 安装 uv（使用 pip 安装更稳定）
RUN pip install uv -i https://mirrors.aliyun.com/pypi/simple/

# 设置 UV 镜像环境变量
ENV UV_PYPI_MIRROR=https://mirrors.aliyun.com/pypi/simple/

WORKDIR /app

# 先复制依赖文件，利用 Docker 层缓存
COPY pyproject.toml uv.lock ./

# 安装依赖（不安装项目本身，加快后续构建）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# 再复制项目代码
COPY . .

# 安装项目本身
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

EXPOSE 8000

# 直接使用 uvicorn，因为依赖已安装到系统 Python
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ws-ping-interval", "60", "--ws-ping-timeout", "120"]