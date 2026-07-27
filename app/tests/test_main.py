from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "bjcf-devops-portfolio"


def test_hello_default():
    r = client.get("/api/v1/hello")
    assert r.status_code == 200
    body = r.json()
    assert body["message"] == "Hello, world!"
    assert "host" in body and "version" in body


def test_hello_named():
    r = client.get("/api/v1/hello", params={"name": "recruiter"})
    assert r.json()["message"] == "Hello, recruiter!"


def test_liveness():
    assert client.get("/health/live").json() == {"status": "alive"}


def test_readiness():
    assert client.get("/health/ready").json() == {"status": "ready"}


def test_metrics_exposed():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text
