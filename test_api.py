import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Survey API" in response.json()["message"]

def test_submit_survey():
    data = {
        "answers": [
            {"question": "Как тебя зовут?", "answer": "Тест"},
            {"question": "Сколько тебе лет?", "answer": "25"},
            {"question": "В каком городе ты живёшь?", "answer": "Тестовск"}
        ]
    }
    response = client.post("/survey/submit", json=data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_get_analytics():
    response = client.get("/survey/analytics")
    assert response.status_code == 200
    assert "ages" in response.json()
    assert "cities" in response.json()