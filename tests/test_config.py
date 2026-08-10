import pytest


def test_parse_csv_list_trims_and_drops_empty_values():
    from config.settings import parse_csv_list

    assert parse_csv_list(" http://localhost:5173, ,https://app.example.com ") == [
        "http://localhost:5173",
        "https://app.example.com",
    ]


def test_production_rejects_default_jwt_secret():
    from config.settings import AppSettings, DEFAULT_JWT_SECRET, validate_production_settings

    settings = AppSettings(
        ENVIRONMENT="production",
        JWT_SECRET_KEY=DEFAULT_JWT_SECRET,
        CORS_ALLOW_ORIGINS=["https://app.example.com"],
    )

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        validate_production_settings(settings)


def test_production_rejects_wildcard_cors():
    from config.settings import AppSettings, validate_production_settings

    settings = AppSettings(
        ENVIRONMENT="production",
        JWT_SECRET_KEY="a-production-secret-with-enough-length",
        CORS_ALLOW_ORIGINS=["*"],
    )

    with pytest.raises(RuntimeError, match="CORS_ALLOW_ORIGINS"):
        validate_production_settings(settings)


def test_development_allows_default_local_settings():
    from config.settings import AppSettings, DEFAULT_JWT_SECRET, validate_production_settings

    settings = AppSettings(
        ENVIRONMENT="development",
        JWT_SECRET_KEY=DEFAULT_JWT_SECRET,
        CORS_ALLOW_ORIGINS=["*"],
    )

    validate_production_settings(settings)


def test_get_settings_disables_reload_by_default():
    from config.settings import get_settings

    settings = get_settings({})

    assert settings.API_RELOAD is False


def test_production_rejects_reload_enabled():
    from config.settings import AppSettings, validate_production_settings

    settings = AppSettings(
        ENVIRONMENT="production",
        JWT_SECRET_KEY="a-production-secret-with-enough-length",
        CORS_ALLOW_ORIGINS=["https://app.example.com"],
        API_RELOAD=True,
    )

    with pytest.raises(RuntimeError, match="API_RELOAD"):
        validate_production_settings(settings)


def test_get_settings_reads_litellm_gateway_config():
    from config.settings import get_settings

    settings = get_settings(
        {
            "LITELLM_BASE_URL": "http://litellm:4000/v1",
            "LITELLM_MASTER_KEY": "sk-test",
        }
    )

    assert settings.LITELLM_BASE_URL == "http://litellm:4000/v1"
    assert settings.LITELLM_MASTER_KEY == "sk-test"


def test_get_settings_reads_nvidia_and_embedding_runtime_config():
    from config.settings import get_settings

    settings = get_settings(
        {
            "NVIDIA_API_KEY": "nvapi-test",
            "NVIDIA_API_BASE_URL": "https://integrate.api.nvidia.com/v1",
            "LLM_CHAT_MODEL": "openai/gpt-oss-20b",
            "EMBEDDING_API_BASE_URL": "http://localhost:8001/v1",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
            "EMBEDDING_DIMENSIONS": "384",
        }
    )

    assert settings.NVIDIA_API_KEY == "nvapi-test"
    assert settings.NVIDIA_API_BASE_URL == "https://integrate.api.nvidia.com/v1"
    assert settings.LLM_CHAT_MODEL == "openai/gpt-oss-20b"
    assert settings.EMBEDDING_API_BASE_URL == "http://localhost:8001/v1"
    assert settings.EMBEDDING_MODEL == "sentence-transformers/all-MiniLM-L6-v2"
    assert settings.EMBEDDING_DIMENSIONS == 384
