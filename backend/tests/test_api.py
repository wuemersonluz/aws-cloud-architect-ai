from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommend_endpoint_returns_services():
    response = client.post(
        "/recommend",
        json={"description": "Preciso de um site estático com CDN"},
    )
    assert response.status_code == 200

    body = response.json()
    services = {s["service"] for s in body["matched_services"]}
    assert "Amazon S3" in services
    assert "Amazon CloudFront" in services
    assert "architecture_summary" in body


def test_recommend_endpoint_rejects_too_short_description():
    response = client.post("/recommend", json={"description": "oi"})
    assert response.status_code == 422
