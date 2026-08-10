FROM apache/airflow:2.10.3

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

USER airflow
WORKDIR /opt/edumentor

COPY --chown=airflow:0 pyproject.toml README.md ./
COPY --chown=airflow:0 api ./api
COPY --chown=airflow:0 auth ./auth
COPY --chown=airflow:0 config ./config
COPY --chown=airflow:0 core ./core
COPY --chown=airflow:0 indexing ./indexing
COPY --chown=airflow:0 retrievers ./retrievers
COPY --chown=airflow:0 tools ./tools
COPY --chown=airflow:0 utils ./utils
COPY --chown=airflow:0 ingest_data ./ingest_data

RUN pip install --no-cache-dir -e .
