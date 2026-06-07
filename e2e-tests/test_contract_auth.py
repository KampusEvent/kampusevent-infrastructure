import httpx
import pytest

pytestmark = pytest.mark.integration

AUTH_ME_CONTRACT_FIELDS = {"id", "name", "email", "role", "created_at"}


def test_auth_me_contract(auth_url: str, participant_token: str) -> None:
    """Registration and other services expect JWT claims {sub, role}; Auth /me exposes user profile."""
    response = httpx.get(
        f"{auth_url}/me",
        headers={"Authorization": f"Bearer {participant_token}"},
        timeout=10.0,
    )
    assert response.status_code == 200
    body = response.json()
    assert AUTH_ME_CONTRACT_FIELDS.issubset(body.keys())
    assert body["role"] == "participant"
    assert body["email"] == "participant@campus.edu"
    assert isinstance(body["id"], str) and body["id"]


def test_auth_me_rejects_missing_token(auth_url: str) -> None:
    response = httpx.get(f"{auth_url}/me", timeout=10.0)
    assert response.status_code == 401
