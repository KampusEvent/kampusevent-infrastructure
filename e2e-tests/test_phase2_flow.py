import httpx
import pytest

pytestmark = pytest.mark.integration


def test_phase2_registration_flow(
    auth_url: str,
    event_url: str,
    registration_url: str,
) -> None:
    """Phase 2: organizer creates event, participant registers and receives ticket."""
    with httpx.Client(timeout=15.0) as client:
        organizer_login = client.post(
            f"{auth_url}/login",
            json={"email": "organizer@campus.edu", "password": "organizer123"},
        )
        assert organizer_login.status_code == 200
        organizer_token = organizer_login.json()["access_token"]

        create_event = client.post(
            f"{event_url}/events",
            json={
                "title": "Registration Test Event",
                "description": "Phase 2 E2E",
                "date": "2026-12-20",
                "location": "Aula",
                "quota": 5,
                "status": "active",
            },
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert create_event.status_code == 201, create_event.text
        event_id = create_event.json()["id"]

        participant_login = client.post(
            f"{auth_url}/login",
            json={"email": "participant@campus.edu", "password": "participant123"},
        )
        assert participant_login.status_code == 200
        participant_token = participant_login.json()["access_token"]

        register = client.post(
            f"{registration_url}/registrations",
            json={"event_id": event_id},
            headers={"Authorization": f"Bearer {participant_token}"},
        )
        assert register.status_code == 201, register.text
        body = register.json()
        assert body["ticket_code"].startswith("EVT-")
        assert body["event_id"] == event_id

        duplicate = client.post(
            f"{registration_url}/registrations",
            json={"event_id": event_id},
            headers={"Authorization": f"Bearer {participant_token}"},
        )
        assert duplicate.status_code == 409

        ticket_lookup = client.get(f"{registration_url}/registrations/ticket/{body['ticket_code']}")
        assert ticket_lookup.status_code == 200
        assert ticket_lookup.json()["id"] == body["id"]
