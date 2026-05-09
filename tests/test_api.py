import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import app

client = TestClient(app)

def test_root():
    """Тест корневого endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "docs" in data
    assert data["message"] == "Survey API"

def test_submit_survey():
    """Тест отправки опроса"""
    data = {
        "answers": [
            {"question": "Как тебя зовут?", "answer": "Тест"},
            {"question": "Сколько тебе лет?", "answer": "25"},
            {"question": "В каком городе ты живёшь?", "answer": "Тестовск"}
        ]
    }
    
    response = client.post("/survey/submit", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"

def test_submit_invalid_age():
    """Тест валидации: возраст должен быть числом"""
    data = {
        "answers": [
            {"question": "Как тебя зовут?", "answer": "Тест"},
            {"question": "Сколько тебе лет?", "answer": "двадцать"},  # Ошибка
        ]
    }
    
    response = client.post("/survey/submit", json=data)
    assert response.status_code == 400  # Bad Request

def test_get_analytics():
    """Тест получения аналитики"""
    response = client.get("/survey/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "ages" in data
    assert "cities" in data

def test_get_responses():
    """Тест получения всех ответов"""
    response = client.get("/survey/responses")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "data" in data
    assert isinstance(data["count"], int)