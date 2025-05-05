from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "PV Ninja" in response.text
