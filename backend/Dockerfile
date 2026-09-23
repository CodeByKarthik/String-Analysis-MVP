FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /backend

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY scripts ./scripts

ENV UV_PROJECT_ENVIRONMENT="/backend/.venv"
RUN uv sync --no-dev --frozen
RUN chmod +x ./scripts/bootstrap_nltk_data.sh && ./scripts/bootstrap_nltk_data.sh

CMD ["sh", "-c", "uv run uvicorn backend.api.app:app --host ${API_HOST} --port ${API_PORT}"]