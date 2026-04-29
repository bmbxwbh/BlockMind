FROM python:3.11-slim

LABEL maintainer="BlockMind Team"
LABEL description="BlockMind - Minecraft AI Companion Backend"

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY src/ ./src/
COPY skills/ ./skills/
COPY config/ ./config/

# 默认配置
COPY config/config.example.yaml config.yaml

# 数据目录
RUN mkdir -p /data/skills /data/logs

EXPOSE 8080

ENV PYTHONPATH=/app
ENV BLOCKMIND_CONFIG=/app/config.yaml

CMD ["python", "-m", "src.main"]
