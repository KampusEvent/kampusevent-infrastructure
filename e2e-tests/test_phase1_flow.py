import httpx
import pytest

pytestmark = pytest.mark.integration


def test_phase1_auth_and_event_flow(
    event_url: str,
    organizer_token: str,
    participant_token: str,
) -> None:
    """Phase 1: login organizer, create event, participant can view."""
    with httpx.Client(timeout=10.0) as client:
        create_event = client.post(
            f"{event_url}/events",
            json={
                "title": "Workshop Microservices",
                "description": "Phase 1 integration test",
                "date": "2026-12-15",
                "location": "Lab Komputer",
                "quota": 50,
                "status": "active",
            },
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert create_event.status_code == 201, create_event.text
        event_id = create_event.json()["id"]

        list_events = client.get(f"{event_url}/events")
        assert list_events.status_code == 200
        assert any(e["id"] == event_id for e in list_events.json())

        forbidden = client.post(
            f"{event_url}/events",
            json={
                "title": "Should Fail",
                "date": "2026-12-20",
                "location": "X",
                "quota": 10,
            },
            headers={"Authorization": f"Bearer {participant_token}"},
        )
        assert forbidden.status_code == 403
