FROM python:3.9 AS builder

ARG RKNN_VERSION=1.6.0
RUN pip install poetry==1.8.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
RUN wget https://github.com/rockchip-linux/rknn-toolkit2/raw/v${RKNN_VERSION}/rknpu2/runtime/Linux/librknn_api/aarch64/librknnrt.so -O /usr/lib/librknnrt.so

FROM python:3.9-slim

ENV PYTHONUNBUFFERED True \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder /usr/lib/librknnrt.so /usr/lib/librknnrt.so
COPY . /app

EXPOSE 8080

WORKDIR /app
ENTRYPOINT ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
