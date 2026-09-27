import os

# Test Environment
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["DEBUG"] = "true"
os.environ["SECURITY_ENABLED"] = "true"
os.environ["OBSERVABILITY_ENABLED"] = "true"
os.environ["TELEMETRY_ENABLED"] = "true"
os.environ["FEEDBACK_ENABLED"] = "true"
os.environ["REDIS_ENABLED"] = "false"
os.environ["RESEARCH_ENABLED"] = "true"
os.environ["DATASET_BUILDER_ENABLED"] = "true"
os.environ["TRAINING_ENABLED"] = "true"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client