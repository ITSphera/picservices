from fastapi.testclient import TestClient
from src.main import app

test_client = TestClient(app)
