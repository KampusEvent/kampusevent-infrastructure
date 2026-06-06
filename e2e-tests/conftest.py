import os

import pytest


@pytest.fixture(scope="session")
def auth_url() -> str:
    return os.getenv("E2E_AUTH_URL", "http://localhost:8001")


@pytest.fixture(scope="session")
def event_url() -> str:
    return os.getenv("E2E_EVENT_URL", "http://localhost:8002")


@pytest.fixture(scope="session")
def registration_url() -> str:
    return os.getenv("E2E_REGISTRATION_URL", "http://localhost:8003")


@pytest.fixture(scope="session")
def attendance_url() -> str:
    return os.getenv("E2E_ATTENDANCE_URL", "http://localhost:8004")
