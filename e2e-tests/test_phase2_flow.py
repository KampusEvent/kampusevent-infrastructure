import httpx
import pytest

from conftest import upcoming_event_payload

pytestmark = pytest.mark.integration


def test_phase2_registration_flow(
    event_url: str,
    registration_url: str,
    organizer_token: str,
    participant_token: str,
    internal_api_key: str,
) -> None:
    """Phase 2: organizer creates event, participant registers and receives ticket."""
    with httpx.Client(timeout=15.0) as client:
        create_event = client.post(
            f"{event_url}/events",
            json=upcoming_event_payload(
                title="Registration Test Event",
                description="Phase 2 E2E",
                location="Aula",
                quota=5,
            ),
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert create_event.status_code == 201, create_event.text
        event_id = create_event.json()["id"]

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

        ticket_lookup = client.get(
            f"{registration_url}/registrations/ticket/{body['ticket_code']}",
            headers={"X-Internal-API-Key": internal_api_key},
        )
        assert ticket_lookup.status_code == 200
        assert ticket_lookup.json()["id"] == body["id"]
