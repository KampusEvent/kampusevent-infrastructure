import re

import httpx
import pytest

from conftest import upcoming_event_payload

pytestmark = pytest.mark.integration

REGISTRATION_CONTRACT_FIELDS = {"id", "event_id", "user_id", "ticket_code", "status", "created_at"}
TICKET_PATTERN = re.compile(r"^EVT-\d{4}-[A-Z0-9]{8}$")


def test_registration_ticket_contract(
    event_url: str,
    registration_url: str,
    organizer_token: str,
    participant_token: str,
    internal_api_key: str,
) -> None:
    """Attendance Service expects these fields from GET /registrations/ticket/{code}."""
    with httpx.Client(timeout=15.0) as client:
        create_event = client.post(
            f"{event_url}/events",
            json=upcoming_event_payload(
                title="Contract Registration Event",
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
        assert register.status_code == 201
        registration = register.json()
        assert REGISTRATION_CONTRACT_FIELDS.issubset(registration.keys())
        assert TICKET_PATTERN.match(registration["ticket_code"])

        ticket_lookup = client.get(
            f"{registration_url}/registrations/ticket/{registration['ticket_code']}",
            headers={"X-Internal-API-Key": internal_api_key},
        )
        assert ticket_lookup.status_code == 200
        ticket_body = ticket_lookup.json()
        assert REGISTRATION_CONTRACT_FIELDS.issubset(ticket_body.keys())
        assert ticket_body["status"] == "registered"
        assert ticket_body["id"] == registration["id"]


def test_registration_get_by_id_contract(
    registration_url: str,
    event_url: str,
    organizer_token: str,
    participant_token: str,
) -> None:
    with httpx.Client(timeout=15.0) as client:
        create_event = client.post(
            f"{event_url}/events",
            json=upcoming_event_payload(
                title="Contract Get By ID",
                location="Lab",
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
        reg_id = register.json()["id"]

        get_resp = client.get(
            f"{registration_url}/registrations/{reg_id}",
            headers={"Authorization": f"Bearer {participant_token}"},
        )
        assert get_resp.status_code == 200
        assert REGISTRATION_CONTRACT_FIELDS.issubset(get_resp.json().keys())
