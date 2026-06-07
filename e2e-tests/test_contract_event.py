import httpx
import pytest

from conftest import upcoming_event_payload

pytestmark = pytest.mark.integration

EVENT_CONTRACT_FIELDS = {
    "id",
    "title",
    "description",
    "date",
    "starts_at",
    "ends_at",
    "location",
    "quota",
    "manual_status",
    "status",
    "created_by",
    "created_at",
    "updated_at",
}


def test_event_get_contract(event_url: str, organizer_token: str) -> None:
    """Registration Service expects these fields from GET /events/{id}."""
    with httpx.Client(timeout=10.0) as client:
        create = client.post(
            f"{event_url}/events",
            json=upcoming_event_payload(
                title="Contract Test Event",
                description="API contract validation",
                location="Lab",
                quota=20,
            ),
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert create.status_code == 201, create.text
        event_id = create.json()["id"]

        get_resp = client.get(f"{event_url}/events/{event_id}")
        assert get_resp.status_code == 200
        body = get_resp.json()
        assert EVENT_CONTRACT_FIELDS.issubset(body.keys())
        assert body["status"] in ("upcoming", "ongoing", "completed", "inactive", "cancelled")
        assert body["manual_status"] in ("active", "inactive", "cancelled")
        assert isinstance(body["quota"], int)


def test_event_list_contract(event_url: str) -> None:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{event_url}/events")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
