import httpx
import pytest

from conftest import start_event_for_check_in, upcoming_event_payload

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
            json=upcoming_event_payload(
                title="Attendance Test Event",
                description="Phase 3 E2E",
                location="Aula",
                quota=10,
            ),
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

        start_event_for_check_in(client, event_url, event_id, organizer_token)

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


def test_phase3_delete_check_in(
    event_url: str,
    registration_url: str,
    attendance_url: str,
    organizer_token: str,
    participant_token: str,
) -> None:
    """Organizer can undo check-in; attendance record is removed."""
    with httpx.Client(timeout=15.0) as client:
        create_event = client.post(
            f"{event_url}/events",
            json=upcoming_event_payload(
                title="Delete Check-in Event",
                description="Phase 3 undo check-in",
                location="Aula",
                quota=10,
            ),
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

        start_event_for_check_in(client, event_url, event_id, organizer_token)

        check_in = client.post(
            f"{attendance_url}/attendance/check-in",
            json={"ticket_code": ticket_code},
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert check_in.status_code == 201
        attendance_id = check_in.json()["id"]

        delete_resp = client.delete(
            f"{attendance_url}/attendance/{attendance_id}",
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert delete_resp.status_code == 204

        attendance_list = client.get(
            f"{attendance_url}/attendance",
            params={"event_id": event_id},
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert attendance_list.status_code == 200
        assert not any(r["ticket_code"] == ticket_code for r in attendance_list.json())

        retry_check_in = client.post(
            f"{attendance_url}/attendance/check-in",
            json={"ticket_code": ticket_code},
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert retry_check_in.status_code == 201
