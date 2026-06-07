import re

import httpx
import pytest


@pytest.mark.asyncio
async def test_full_event_flow(
    event_url: str,
    registration_url: str,
    attendance_url: str,
    organizer_token: str,
    participant_token: str,
) -> None:
    """
    End-to-end scenario:
    1. Organizer login
    2. Create event
    3. Participant login
    4. Register for event
    5. Receive ticket code
    6. Check-in at event
    7. Verify attendance recorded
    """
    async with httpx.AsyncClient() as client:
        # Step 1–2: Create event (organizer token from fixture)
        create_event = await client.post(
            f"{event_url}/events",
            json={
                "title": "Workshop Microservices",
                "description": "E2E test event",
                "date": "2026-12-01",
                "location": "Lab Komputer",
                "quota": 50,
                "status": "active",
            },
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert create_event.status_code == 201
        event_id = create_event.json()["id"]

        # Step 3–4: Register for event
        register = await client.post(
            f"{registration_url}/registrations",
            json={"event_id": event_id},
            headers={"Authorization": f"Bearer {participant_token}"},
        )
        assert register.status_code == 201
        ticket_code = register.json()["ticket_code"]
        assert re.match(r"^EVT-\d{4}-[A-Z0-9]{8}$", ticket_code)

        # Step 5: Check-in
        check_in = await client.post(
            f"{attendance_url}/attendance/check-in",
            json={"ticket_code": ticket_code},
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert check_in.status_code == 201

        # Step 6: Verify attendance
        attendance_list = await client.get(
            f"{attendance_url}/attendance",
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert attendance_list.status_code == 200
        records = attendance_list.json()
        assert len(records) >= 1
        assert any(r["ticket_code"] == ticket_code for r in records)


def test_all_services_health(gateway_url: str) -> None:
    """Verify all services are reachable via API Gateway."""
    services = {
        "auth": f"{gateway_url}/auth/health",
        "event": f"{gateway_url}/events/health",
        "registration": f"{gateway_url}/registrations/health",
        "attendance": f"{gateway_url}/attendance/health",
    }
    for name, url in services.items():
        response = httpx.get(url, timeout=5.0)
        assert response.status_code == 200, f"{name} service unhealthy"
        assert response.json() == {"status": "ok"}
