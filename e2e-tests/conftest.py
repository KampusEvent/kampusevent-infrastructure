import os
from datetime import datetime, timedelta, timezone

import httpx
import pytest

GATEWAY_URL = os.getenv("E2E_GATEWAY_URL", "http://localhost:8080")


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def upcoming_event_payload(**overrides: object) -> dict:
    now = datetime.now(timezone.utc)
    starts = now + timedelta(days=1)
    payload = {
        "title": "Test Event",
        "description": "",
        "starts_at": iso_utc(starts),
        "ends_at": iso_utc(starts + timedelta(hours=8)),
        "location": "Aula",
        "quota": 10,
        "status": "active",
    }
    payload.update(overrides)
    return payload


def ongoing_schedule_payload() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "starts_at": iso_utc(now - timedelta(hours=1)),
        "ends_at": iso_utc(now + timedelta(hours=2)),
    }


def start_event_for_check_in(client: httpx.Client, event_url: str, event_id: str, token: str) -> None:
    """Shift event schedule so effective status becomes ongoing (for check-in E2E)."""
    response = client.put(
        f"{event_url}/events/{event_id}",
        json=ongoing_schedule_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ongoing"


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
