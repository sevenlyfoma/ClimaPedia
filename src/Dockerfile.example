FROM python:3.11-alpine

WORKDIR /workspace
COPY pyproject.toml poetry.lock ./

ENV PATH="${PATH}:/root/.local/bin"

RUN apk add --update nodejs npm pipx gcc g++ python3-dev geos-dev && \
    pipx install poetry && \
    poetry install

COPY . .

RUN cd frontend && \
    npm ci && \
    npm run build

ENTRYPOINT ["sh", "/workspace/entrypoint.sh"]
