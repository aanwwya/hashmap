from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_new_event():
    response = client.post(
        "/events",
        json={
            "user_id": 100,
            "action": "purchase"
        }
    )

    assert response.status_code == 200
    assert response.json()["duplicate"] is False


def test_duplicate_event():
    event = {
        "user_id": 200,
        "action": "purchase"
    }

    first = client.post("/events", json=event)
    second = client.post("/events", json=event)

    assert first.json()["duplicate"] is False
    assert second.json()["duplicate"] is True


def test_different_events():
    first = client.post(
        "/events",
        json={
            "user_id": 300,
            "action": "purchase"
        }
    )

    second = client.post(
        "/events",
        json={
            "user_id": 300,
            "action": "refund"
        }
    )

    assert first.json()["duplicate"] is False
    assert second.json()["duplicate"] is False


def test_invalid_user_id_is_rejected():
    response = client.post(
        "/events",
        json={
            "user_id": "not-a-number",
            "action": "purchase"
        }
    )

    assert response.status_code == 422


def test_missing_action_is_rejected():
    response = client.post(
        "/events",
        json={
            "user_id": 400
        }
    )

    assert response.status_code == 422


def test_stats():
    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    assert "active_events" in data
    assert "accepted" in data
    assert "duplicates" in data