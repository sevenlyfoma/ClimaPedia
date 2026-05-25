FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies (Debian equivalent)
# We add curl for pipx/poetry and build-essential/libgeos-dev just in case
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    npm \
    pipx \
    build-essential \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

ENV PATH="${PATH}:/root/.local/bin"

RUN pipx install poetry && \
    poetry install --no-root

COPY . .

RUN cd frontend && \
    npm ci && \
    npm run build

ENTRYPOINT ["sh", "/workspace/entrypoint.sh"]