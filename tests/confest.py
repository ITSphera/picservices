from fastapi.testclient import TestClient
from src.config import app

test_client = TestClient(app)
