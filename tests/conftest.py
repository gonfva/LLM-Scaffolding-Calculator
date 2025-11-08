"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Provide a test client for HTTP requests."""
    return TestClient(app)
