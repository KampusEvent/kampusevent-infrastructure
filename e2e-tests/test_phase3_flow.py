import httpx
import pytest

pytestmark = pytest.mark.integration


def test_phase3_attendance_flow(
    event_url: str,
    registration_url: str,
    attendance_url: str,
    organizer_token: str,
    participant_token: str,
) -> None:
    """Phase 3: full flow through check-in and attendance listing."""
    with httpx.Client(timeout=15.0) as client:
        create_event = client.post(
            f"{event_url}/events",
            json={
                "title": "Attendance Test Event",
                "description": "Phase 3 E2E",
                "date": "2026-12-25",
                "location": "Aula",
                "quota": 10,
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
        ticket_code = register.json()["ticket_code"]

        check_in = client.post(
            f"{attendance_url}/attendance/check-in",
            json={"ticket_code": ticket_code},
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert check_in.status_code == 201, check_in.text
        assert check_in.json()["ticket_code"] == ticket_code

        duplicate = client.post(
            f"{attendance_url}/attendance/check-in",
            json={"ticket_code": ticket_code},
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert duplicate.status_code == 409

        attendance_list = client.get(
            f"{attendance_url}/attendance",
            params={"event_id": event_id},
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert attendance_list.status_code == 200
        assert len(attendance_list.json()) >= 1
