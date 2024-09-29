import pytest
from fastapi.testclient import TestClient
from myapp import app

client = TestClient(app)

@pytest.mark.parametrize("endpoint", ["env", "health", "info", "metrics", "prometheus", "loggers"])
def test_endpoints_disabled_default(endpoint):
    response = client.get(f"/management/{endpoint}")
    assert response.status_code == 404

@pytest.mark.parametrize("endpoint", ["env", "health", "info", "metrics", "prometheus", "loggers"])
def test_endpoints_enabled(endpoint):
    # Set up configuration for enabled endpoints
    response = client.get(f"/management/{endpoint}")
    
    if endpoint == "health":
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/vnd.spring-boot.actuator.v3+json"
        assert response.json() == {"status": "UP"}
    elif endpoint == "info":
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/vnd.spring-boot.actuator.v3+json"
    elif endpoint == "metrics":
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/vnd.spring-boot.actuator.v3+json"
    elif endpoint == "prometheus":
        assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
    elif endpoint == "loggers":
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/vnd.spring-boot.actuator.v3+json"

def test_post_loggers_csrf_enabled_default():
    response = client.post("/management/loggers/org.ehrbase.test", json={"configuredLevel": "debug"})
    assert response.status_code == 403

def test_post_loggers_csrf_disabled():
    # Set up configuration for CSRF disabled
    response = client.post("/management/loggers/org.ehrbase.test", json={"configuredLevel": "debug"})
    assert response.status_code == 204
