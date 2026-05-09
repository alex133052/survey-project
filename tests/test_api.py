import pytest
from fastapi.testclient import TestClient
import sys
import os

# Добавляем корень проекта в path для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api import app

client = TestClient(app)

def test_root():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Survey API" in data["message"]

def test_submit_survey():
    """Тест отправки опроса"""
    data = {
        "answers": [
            {"question": "Как тебя зовут?", "answer": "Иван"},
            {"question": "Сколько тебе лет?", "answer": "25"},
            {"question": "В каком городе ты живёшь?", "answer": "Москва"}
        ]
    }
    response = client.post("/survey/submit", json=data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_submit_survey_empty_answers():
    """Тест отправки пустого опроса"""
    data = {"answers": []}
    response = client.post("/survey/submit", json=data)
    assert response.status_code == 400

def test_get_analytics():
    """Тест получения статистики"""
    response = client.get("/survey/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "ages" in data
    assert "cities" in data
    assert isinstance(data["ages"], dict)
    assert isinstance(data["cities"], dict)

def test_get_responses():
    """Тест получения всех ответов"""
    response = client.get("/survey/responses")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "data" in data
    assert isinstance(data["count"], int)
    assert isinstance(data["data"], list)