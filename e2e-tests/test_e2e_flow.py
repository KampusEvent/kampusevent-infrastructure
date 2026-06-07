import httpx
import pytest


@pytest.mark.asyncio
async def test_full_event_flow(
    auth_url: str,
    event_url: str,
    registration_url: str,
    attendance_url: str,
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
        # Step 1: Organizer login
        organizer_login = await client.post(
            f"{auth_url}/login",
            json={"email": "organizer@campus.edu", "password": "organizer123"},
        )
        assert organizer_login.status_code == 200
        organizer_token = organizer_login.json()["access_token"]

        # Step 2: Create event
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

        # Step 3: Participant login
        participant_login = await client.post(
            f"{auth_url}/login",
            json={"email": "participant@campus.edu", "password": "participant123"},
        )
        assert participant_login.status_code == 200
        participant_token = participant_login.json()["access_token"]

        # Step 4: Register for event
        register = await client.post(
            f"{registration_url}/registrations",
            json={"event_id": event_id},
            headers={"Authorization": f"Bearer {participant_token}"},
        )
        assert register.status_code == 201
        ticket_code = register.json()["ticket_code"]

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
        assert len(attendance_list.json()) >= 1


def test_all_services_health(
    auth_url: str,
    event_url: str,
    registration_url: str,
    attendance_url: str,
) -> None:
    """Verify all services are reachable (run after docker compose up)."""
    services = {
        "auth": auth_url,
        "event": event_url,
        "registration": registration_url,
        "attendance": attendance_url,
    }
    for name, url in services.items():
        response = httpx.get(f"{url}/health", timeout=5.0)
        assert response.status_code == 200, f"{name} service unhealthy"
        assert response.json() == {"status": "ok"}
