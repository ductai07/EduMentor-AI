FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .

COPY api ./api
COPY auth ./auth
COPY config ./config
COPY core ./core
COPY evals ./evals
COPY indexing ./indexing
COPY retrievers ./retrievers
COPY tools ./tools
COPY utils ./utils
COPY main.py ./main.py

EXPOSE 5000

CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "5000"]
