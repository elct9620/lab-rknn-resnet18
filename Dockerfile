FROM debian:12-slim AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv pipx gcc wget libpython3-dev && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip setuptools wheel

FROM build AS build-venv

ARG RKNN_VERSION=1.6.0
ARG POETRY_VERSION=1.8.1

RUN pipx install poetry==${POETRY_VERSION}

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN . /venv/bin/activate && \
    pipx run poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
RUN wget https://github.com/rockchip-linux/rknn-toolkit2/raw/v${RKNN_VERSION}/rknpu2/runtime/Linux/librknn_api/aarch64/librknnrt.so -O /usr/lib/librknnrt.so
RUN wget https://github.com/rockchip-linux/rknn-toolkit2/raw/v${RKNN_VERSION}/rknpu2/examples/rknn_yolov5_demo/model/RK3588/yolov5s-640-640.rknn -O /app/yolov5s-640-640.rknn

FROM gcr.io/distroless/python3-debian12

ENV PYTHONUNBUFFERED True

COPY --from=build-venv /venv /venv
COPY --from=build-venv /usr/lib/librknnrt.so /usr/lib/librknnrt.so
COPY --from=build-venv /app/yolov5s-640-640.rknn /app/yolov5s-640-640.rknn
COPY . /app
WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["/venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
