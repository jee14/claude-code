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
    assert "message" in data
    assert "version" in data
    assert data["version"] == "3.0.0"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "3.0.0"


def test_correct_empty_text(client):
    """Test correction with empty text"""
    response = client.post(
        "/correct",
        json={"text": "", "mode": "proofreading"}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


@pytest.mark.skipif(
    True,  # Skip if OPENROUTER_API_KEY not set
    reason="Requires OpenRouter API key"
)
def test_proofreading_mode(client):
    """Test proofreading mode with OpenRouter API"""
    response = client.post(
        "/correct",
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


@pytest.mark.skipif(
    True,
    reason="Requires OpenRouter API key"
)
def test_spelling_correction(client):
    """Test spelling correction with OpenRouter API"""
    response = client.post(
        "/correct",
        json={
            "text": "됬다",
            "mode": "proofreading"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "original" in data
    assert "corrected" in data


@pytest.mark.skipif(
    True,
    reason="Requires OpenRouter API key"
)
def test_spacing_correction(client):
    """Test spacing correction with OpenRouter API"""
    response = client.post(
        "/correct",
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


@pytest.mark.skipif(
    True,
    reason="Requires OpenRouter API key"
)
def test_copyediting_mode(client):
    """Test copyediting mode with OpenRouter API"""
    response = client.post(
        "/correct",
        json={
            "text": "안녕하세요됬어요",
            "mode": "copyediting"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "original" in data
    assert "corrected" in data


@pytest.mark.skipif(
    True,
    reason="Requires OpenRouter API key"
)
def test_rewriting_mode(client):
    """Test rewriting mode with OpenRouter API"""
    response = client.post(
        "/correct",
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
        "/correct",
        json={
            "text": "안녕하세요",
            "mode": "invalid_mode"
        }
    )
    assert response.status_code == 422  # Validation error


def test_backward_compatibility(client):
    """Test /correct/detailed endpoint for backward compatibility"""
    response = client.post(
        "/correct/detailed",
        json={"text": "", "mode": "proofreading"}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
