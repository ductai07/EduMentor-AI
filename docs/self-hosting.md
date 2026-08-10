# Self-Hosting Guide

EduMentor can run as a production-like single-VM stack before moving to Kubernetes.

## Required Services

| Layer | Service | Required | Notes |
| --- | --- | --- | --- |
| Web UI | `ui` | Yes | React/Vite static app served by Nginx. |
| API | `api` | Yes | FastAPI app with health/readiness endpoints. |
| User state | `mongodb` | Yes | User profile and chat history. |
| Vector DB | `standalone`, `etcd`, `minio` | Yes | Milvus standalone stack. |
| Cache | `redis` | Yes | Retrieval cache and future semantic cache. |
| LLM gateway | `litellm` | Yes | OpenAI-compatible model router/fallback boundary. |
| Ingestion orchestration | Airflow in `ingest_data/` | Recommended | Batch document ingestion with manifest/idempotency. |
| Observability | Langfuse | Recommended | Use cloud Langfuse or self-host separately. |
| HTTPS | Caddy/Nginx/Traefik | Required for public prod | Terminate TLS and proxy to API/UI. |

## Minimum API Keys

Choose one model path:

- NVIDIA hosted NIM path: set `NVIDIA_API_KEY`, `NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1`, and `LLM_CHAT_MODEL=openai/gpt-oss-20b`.
- Cloud path: `GOOGLE_API_KEY`, `OPENAI_API_KEY`, or `GROQ_API_KEY` configured in LiteLLM.
- Local path: `LOCAL_OPENAI_BASE_URL` and `LOCAL_OPENAI_API_KEY` pointing to LM Studio, vLLM, Ollama OpenAI-compatible proxy, or another local model server.

Optional:

- `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` for tracing.
- `SERPER_API_KEY` or `TAVILY_API_KEY` for web search tools.

## Local Production-Like Run

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

Smoke checks:

```powershell
curl http://localhost:5000/health
curl http://localhost:5000/ready
curl http://localhost:5173
python -m evals.run_eval --dataset evals/datasets/edumentor_v1.jsonl --output reports/eval-baseline-v1.json
```

## Production Hardening Checklist

- Set `ENVIRONMENT=production`.
- Set a strong `JWT_SECRET_KEY` with at least 32 characters.
- Set explicit `CORS_ALLOW_ORIGINS`; do not use `*`.
- Keep `API_RELOAD=false`.
- Configure one LiteLLM cloud or local model route.
- For the default NVIDIA route, keep LiteLLM pointing at `edumentor-fast` and `edumentor-quality`; both resolve to `LLM_CHAT_MODEL`.
- Start Airflow from `ingest_data/` for batch ingestion and keep `ingest_data/reports/manifest.json` as evidence.
- Configure volume backups for MongoDB, Milvus, MinIO, and Redis.
- Put UI/API behind HTTPS reverse proxy.
- Capture Langfuse dashboard evidence after traffic.
- Run load smoke before publishing production claims.
