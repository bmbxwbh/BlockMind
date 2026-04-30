# ═══════════════════════════════════════
# BlockMind — Multi-stage Docker Build
# ═══════════════════════════════════════

# ── Stage 1: Dependencies ──
FROM python:3.11-slim AS deps

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime ──
FROM python:3.11-slim

LABEL maintainer="BlockMind Team"
LABEL description="BlockMind - Minecraft AI Companion Backend"
LABEL org.opencontainers.image.source="https://github.com/bmbxwbh/BlockMind"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# 只复制编译好的依赖
COPY --from=deps /install /usr/local

# 非 root 用户运行
RUN groupadd -r blockmind && useradd -r -g blockmind -d /app blockmind \
    && mkdir -p /data/skills /data/logs /data/memory /data/backups \
    && chown -R blockmind:blockmind /app /data

# 应用代码
COPY --chown=blockmind:blockmind src/ ./src/
COPY --chown=blockmind:blockmind skills/ ./skills/
COPY --chown=blockmind:blockmind config/ ./config/
COPY --chown=blockmind:blockmind config/config.example.yaml config.yaml

# 健康检查
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

EXPOSE 19951

ENV PYTHONPATH=/app
ENV BLOCKMIND_CONFIG=/app/config.yaml
ENV BLOCKMIND_PORT=19951

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
    CMD curl -sf http://localhost:19951/api/system/health || exit 1

USER blockmind

CMD ["python", "-m", "src.main"]
