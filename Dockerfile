FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY ead_agent ./ead_agent
COPY ead_api ./ead_api
COPY ead_ui ./ead_ui
COPY migrations ./migrations
COPY alembic.ini ./

RUN pip install --upgrade pip \
    && pip install ".[local,ui]"

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/artifacts /app/.cache /app/charts_out \
    && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000 7860

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD curl --fail --silent http://127.0.0.1:8000/health/live || exit 1

CMD ["uvicorn", "ead_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
