from fastapi.testclient import TestClient


def test_health_endpoint_returns_liveness():
    from api.main import create_app

    client = TestClient(create_app(enable_lifespan=False))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "edumentor-api"


def test_request_id_header_is_added_when_missing():
    from api.main import create_app

    client = TestClient(create_app(enable_lifespan=False))

    response = client.get("/health")

    assert response.headers["X-Request-ID"]


def test_request_id_header_echoes_client_value():
    from api.main import create_app

    client = TestClient(create_app(enable_lifespan=False))

    response = client.get("/health", headers={"X-Request-ID": "req-test-123"})

    assert response.headers["X-Request-ID"] == "req-test-123"


def test_ready_reports_missing_dependencies():
    from api import state
    from api.main import create_app

    state.assistant = None
    state.document_indexer = None
    client = TestClient(create_app(enable_lifespan=False))

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["dependencies"] == {
        "assistant": "missing",
        "document_indexer": "missing",
    }


def test_ready_reports_available_dependencies():
    from api import state
    from api.main import create_app

    state.assistant = object()
    state.document_indexer = object()
    client = TestClient(create_app(enable_lifespan=False))

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["dependencies"] == {
        "assistant": "ready",
        "document_indexer": "ready",
    }
