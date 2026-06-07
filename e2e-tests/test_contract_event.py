import httpx
import pytest

pytestmark = pytest.mark.integration

EVENT_CONTRACT_FIELDS = {
    "id",
    "title",
    "description",
    "date",
    "location",
    "quota",
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
            json={
                "title": "Contract Test Event",
                "description": "API contract validation",
                "date": "2026-11-01",
                "location": "Lab",
                "quota": 20,
                "status": "active",
            },
            headers={"Authorization": f"Bearer {organizer_token}"},
        )
        assert create.status_code == 201
        event_id = create.json()["id"]

        get_resp = client.get(f"{event_url}/events/{event_id}")
        assert get_resp.status_code == 200
        body = get_resp.json()
        assert EVENT_CONTRACT_FIELDS.issubset(body.keys())
        assert body["status"] in ("active", "inactive", "cancelled")
        assert isinstance(body["quota"], int)


def test_event_list_contract(event_url: str) -> None:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{event_url}/events")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
