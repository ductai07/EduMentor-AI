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
COPY --chown=airflow:0 evals ./evals
COPY --chown=airflow:0 indexing ./indexing
COPY --chown=airflow:0 retrievers ./retrievers
COPY --chown=airflow:0 tools ./tools
COPY --chown=airflow:0 utils ./utils
COPY --chown=airflow:0 ingest_data ./ingest_data

RUN pip install --no-cache-dir \
    pymilvus==3.0.1 \
    sentence-transformers==5.7.0 \
    langchain==1.3.14 \
    mistralai==2.9.1 \
    python-docx==1.2.0 \
    docx2txt==0.9 \
    python-dotenv==1.0.1 \
    click==8.1.7
