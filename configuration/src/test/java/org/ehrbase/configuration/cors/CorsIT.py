import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Define your FastAPI app with CORS middleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://client.ehrbase.org"],
    allow_methods=["*"],  # Adjust methods as needed
    allow_headers=["*"],  # Adjust headers as needed
)

@app.get("/rest/openehr/v1/definition/template/adl1.4")
async def get_template():
    return {"message": "This is a test endpoint"}

client = TestClient(app)

class TestCors:

    def test_cors_headers(self):
        response = client.options(
            "/rest/openehr/v1/definition/template/adl1.4",
            headers={"Access-Control-Request-Method": "GET", "Origin": "https://client.ehrbase.org"}
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "https://client.ehrbase.org"
