import time

import httpx
import pytest

pytestmark = pytest.mark.integration

SERVICE_JOBS = ("auth-service", "event-service", "registration-service", "attendance-service")


def test_all_services_expose_metrics(gateway_url: str) -> None:
    urls = [
        f"{gateway_url}/auth/metrics",
        f"{gateway_url}/events/metrics",
        f"{gateway_url}/registrations/metrics",
        f"{gateway_url}/attendance/metrics",
    ]
    for url in urls:
        response = httpx.get(url, timeout=5.0)
        assert response.status_code == 200
        assert "http_requests_total" in response.text


def test_prometheus_scrapes_services(prometheus_url: str) -> None:
    active_jobs: set[str] = set()
    for _ in range(10):
        response = httpx.get(f"{prometheus_url}/api/v1/targets", timeout=10.0)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        active_jobs = {
            t["labels"]["job"]
            for t in data["data"]["activeTargets"]
            if t.get("health") == "up"
        }
        if all(job in active_jobs for job in SERVICE_JOBS):
            return
        time.sleep(2)

    missing = [job for job in SERVICE_JOBS if job not in active_jobs]
    pytest.fail(f"Prometheus targets not healthy: {missing}")


def test_prometheus_has_service_metrics(prometheus_url: str) -> None:
    query = 'http_requests_total{service="auth-service"}'
    response = httpx.get(
        f"{prometheus_url}/api/v1/query",
        params={"query": query},
        timeout=10.0,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
