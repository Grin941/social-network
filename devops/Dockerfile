FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
COPY ../uv.lock pyproject.toml ./
RUN uv sync --no-dev --frozen --no-install-project

FROM python:3.12-slim-bookworm
WORKDIR /app
COPY --from=builder /.venv /app/.venv
COPY ../src /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="${PYTHONPATH}:/app/social_network"
