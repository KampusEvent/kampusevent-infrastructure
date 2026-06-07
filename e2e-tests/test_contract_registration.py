import re

import httpx
import pytest

pytestmark = pytest.mark.integration

REGISTRATION_CONTRACT_FIELDS = {"id", "event_id", "user_id", "ticket_code", "status", "created_at"}
TICKET_PATTERN = re.compile(r"^EVT-\d{4}-[A-Z0-9]{8}$")


def test_registration_ticket_contract(
    event_url: str,
    registration_url: str,
    organizer_token: str,
    participant_token: str,
) -> None:
    """Attendance Service expects these fields from GET /registrations/ticket/{code}."""
    with httpx.Client(timeout=15.0) as client:
        create_event = client.post(
            f"{event_url}/events",
            json={
                "title": "Contract Registration Event",
                "date": "2026-11-15",
                "location": "Aula",
                "quota": 5,
                "status": "active",
            },
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert create_event.status_code == 201
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
            f"{registration_url}/registrations/ticket/{registration['ticket_code']}"
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
            json={
                "title": "Contract Get By ID",
                "date": "2026-11-20",
                "location": "Lab",
                "quota": 5,
                "status": "active",
            },
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
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
