import os

import httpx
import pytest


@pytest.fixture(scope="session")
def auth_url() -> str:
    return os.getenv("E2E_AUTH_URL", "http://localhost:8001")


@pytest.fixture(scope="session")
def event_url() -> str:
    return os.getenv("E2E_EVENT_URL", "http://localhost:8002")


@pytest.fixture(scope="session")
def registration_url() -> str:
    return os.getenv("E2E_REGISTRATION_URL", "http://localhost:8003")


@pytest.fixture(scope="session")
def attendance_url() -> str:
    return os.getenv("E2E_ATTENDANCE_URL", "http://localhost:8004")


@pytest.fixture(scope="session")
def prometheus_url() -> str:
    return os.getenv("E2E_PROMETHEUS_URL", "http://localhost:9090")


@pytest.fixture(scope="session")
def organizer_token(auth_url: str) -> str:
    response = httpx.post(
        f"{auth_url}/login",
        json={"email": "organizer@campus.edu", "password": "organizer123"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def participant_token(auth_url: str) -> str:
    response = httpx.post(
        f"{auth_url}/login",
        json={"email": "participant@campus.edu", "password": "participant123"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def internal_api_key() -> str:
    return os.getenv("INTERNAL_API_KEY", "change-me-internal-key")


@pytest.fixture(scope="session")
def admin_token(auth_url: str) -> str:
    response = httpx.post(
        f"{auth_url}/login",
        json={"email": "admin@campus.edu", "password": "admin123"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()["access_token"]
