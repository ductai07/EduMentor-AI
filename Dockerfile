FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && python -c "import subprocess, sys, tomllib; deps = tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']; subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', *deps])"

COPY api ./api
COPY auth ./auth
COPY config ./config
COPY core ./core
COPY evals ./evals
COPY indexing ./indexing
COPY retrievers ./retrievers
COPY tools ./tools
COPY utils ./utils
COPY ingest_data ./ingest_data

EXPOSE 5000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5000"]
