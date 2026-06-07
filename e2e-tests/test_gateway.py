import httpx
import pytest

from conftest import start_event_for_check_in, upcoming_event_payload

pytestmark = pytest.mark.integration

GATEWAY_URL = "http://localhost:8080"


@pytest.fixture(scope="session")
def gateway_url() -> str:
    import os
    return os.getenv("E2E_GATEWAY_URL", GATEWAY_URL)


def test_gateway_health(gateway_url: str) -> None:
    response = httpx.get(f"{gateway_url}/gateway/health", timeout=5.0)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["gateway"] == "nginx"


def test_gateway_routes_auth_login(gateway_url: str) -> None:
    response = httpx.post(
        f"{gateway_url}/auth/login",
        json={"email": "organizer@campus.edu", "password": "organizer123"},
        timeout=10.0,
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_gateway_routes_events(gateway_url: str, organizer_token: str) -> None:
    response = httpx.get(
        f"{gateway_url}/events",
        headers={"Authorization": f"Bearer {organizer_token}"},
        timeout=10.0,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_gateway_full_flow_via_gateway(gateway_url: str) -> None:
    """End-to-end flow through API Gateway only."""
    organizer = httpx.post(
        f"{gateway_url}/auth/login",
        json={"email": "organizer@campus.edu", "password": "organizer123"},
        timeout=10.0,
    )
    organizer_token = organizer.json()["access_token"]

    create_event = httpx.post(
        f"{gateway_url}/events",
        json=upcoming_event_payload(
            title="Gateway Flow Event",
            location="Aula",
            quota=10,
        ),
        headers={"Authorization": f"Bearer {organizer_token}"},
        timeout=10.0,
    )
    assert create_event.status_code == 201
    event_id = create_event.json()["id"]

    participant = httpx.post(
        f"{gateway_url}/auth/login",
        json={"email": "participant@campus.edu", "password": "participant123"},
        timeout=10.0,
    )
    participant_token = participant.json()["access_token"]

    register = httpx.post(
        f"{gateway_url}/registrations",
        json={"event_id": event_id},
        headers={"Authorization": f"Bearer {participant_token}"},
        timeout=10.0,
    )
    assert register.status_code == 201
    ticket_code = register.json()["ticket_code"]

    with httpx.Client(timeout=10.0) as client:
        start_event_for_check_in(client, gateway_url, event_id, organizer_token)

    check_in = httpx.post(
        f"{gateway_url}/attendance/check-in",
        json={"ticket_code": ticket_code},
        headers={"Authorization": f"Bearer {organizer_token}"},
        timeout=10.0,
    )
    assert check_in.status_code == 201


def test_zzz_gateway_rate_limit_returns_429(gateway_url: str) -> None:
    """Strict rate limit on /auth/login — expect 429 after burst exceeded."""
    responses = []
    for _ in range(40):
        resp = httpx.post(
            f"{gateway_url}/auth/login",
            json={"email": "nonexistent@test.com", "password": "wrong"},
            timeout=5.0,
        )
        responses.append(resp.status_code)

    assert 429 in responses, "Expected rate limit 429 from gateway"
