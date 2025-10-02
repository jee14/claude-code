import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Korean Text Corrector API"
    assert data["version"] == "1.0.0"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_correct_empty_text(client):
    """Test correction with empty text"""
    response = client.post(
        "/api/correct",
        json={"text": "", "mode": "proofreading"}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_proofreading_mode(client):
    """Test proofreading mode"""
    response = client.post(
        "/api/correct",
        json={
            "text": "안녕하세요 할수있습니다",
            "mode": "proofreading"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "original" in data
    assert "corrected" in data
    assert "corrections" in data
    assert data["original"] == "안녕하세요 할수있습니다"


def test_spelling_correction(client):
    """Test spelling correction"""
    response = client.post(
        "/api/correct",
        json={
            "text": "됬다",
            "mode": "proofreading"
        }
    )
    assert response.status_code == 200
    data = response.json()
    # Should correct 됬다 -> 됐다
    assert len(data["corrections"]) > 0
    assert any(c["type"] == "spelling" for c in data["corrections"])


def test_spacing_correction(client):
    """Test spacing correction"""
    response = client.post(
        "/api/correct",
        json={
            "text": "할수있어요",
            "mode": "proofreading"
        }
    )
    assert response.status_code == 200
    data = response.json()
    # Should correct 할수있어요 -> 할 수 있어요
    assert len(data["corrections"]) > 0
    corrections_text = " ".join([c["corrected"] for c in data["corrections"]])
    assert "할 수 있" in corrections_text or data["corrected"] == "할 수 있어요"


def test_copyediting_mode(client):
    """Test copyediting mode"""
    response = client.post(
        "/api/correct",
        json={
            "text": "안녕하세요됬어요",
            "mode": "copyediting"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "original" in data
    assert "corrected" in data


def test_rewriting_mode(client):
    """Test rewriting mode"""
    response = client.post(
        "/api/correct",
        json={
            "text": "좋아요 좋아요",
            "mode": "rewriting"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "original" in data
    assert "corrected" in data


def test_invalid_mode(client):
    """Test with invalid mode"""
    response = client.post(
        "/api/correct",
        json={
            "text": "안녕하세요",
            "mode": "invalid_mode"
        }
    )
    assert response.status_code == 422  # Validation error


def test_correction_structure(client):
    """Test correction item structure"""
    response = client.post(
        "/api/correct",
        json={
            "text": "됬다",
            "mode": "proofreading"
        }
    )
    assert response.status_code == 200
    data = response.json()

    if len(data["corrections"]) > 0:
        correction = data["corrections"][0]
        assert "type" in correction
        assert "original" in correction
        assert "corrected" in correction
        assert "explanation" in correction
        assert "position" in correction
        assert "start" in correction["position"]
        assert "end" in correction["position"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
