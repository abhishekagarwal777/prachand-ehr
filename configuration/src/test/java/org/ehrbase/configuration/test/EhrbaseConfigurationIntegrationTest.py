import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

# Define your FastAPI app and include necessary configurations
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://client.ehrbase.org"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example endpoint
@app.get("/example")
async def example_endpoint():
    return {"message": "This is a test endpoint"}

# Create a TestClient instance
client = TestClient(app)

@pytest.fixture
def test_client():
    # This fixture will provide the TestClient instance to your tests
    return client


def test_example_endpoint(test_client):
    response = test_client.get("/example")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a test endpoint"}


import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

@pytest.fixture
def custom_config_app():
    app = FastAPI()
    # Apply custom configurations here
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://client.ehrbase.org"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

@pytest.fixture
def test_client(custom_config_app):
    return TestClient(custom_config_app)

def test_example_endpoint(test_client):
    response = test_client.get("/example")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a test endpoint"}
