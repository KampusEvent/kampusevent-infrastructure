import os

import httpx
import pytest

GATEWAY_URL = os.getenv("E2E_GATEWAY_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def gateway_url() -> str:
    return GATEWAY_URL


@pytest.fixture(scope="session")
def auth_url(gateway_url: str) -> str:
    return os.getenv("E2E_AUTH_URL", f"{gateway_url}/auth")


@pytest.fixture(scope="session")
def event_url(gateway_url: str) -> str:
    return os.getenv("E2E_EVENT_URL", gateway_url)


@pytest.fixture(scope="session")
def registration_url(gateway_url: str) -> str:
    return os.getenv("E2E_REGISTRATION_URL", gateway_url)


@pytest.fixture(scope="session")
def attendance_url(gateway_url: str) -> str:
    return os.getenv("E2E_ATTENDANCE_URL", gateway_url)


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
