import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.survey import SurveyController
from src.database_pg import PostgresDatabaseManager

@pytest.fixture
def controller():
    """Фикстура для создания контроллера"""
    db = PostgresDatabaseManager()
    db.init_db()
    return SurveyController(db)

def test_save_success(controller):
    """Тест успешного сохранения"""
    answers = [
        ("Имя", "Алексей"),
        ("Возраст", "28")
    ]
    result = controller.save(answers)
    assert result == True

def test_save_empty_answers(controller):
    """Тест с пустыми ответами"""
    answers = []
    with pytest.raises(ValueError):
        controller.save(answers)

def test_save_empty_question(controller):
    """Тест с пустым вопросом"""
    answers = [("", "Ответ")]
    with pytest.raises(ValueError):
        controller.save(answers)

def test_save_empty_answer(controller):
    """Тест с пустым ответом"""
    answers = [("Вопрос", "")]
    with pytest.raises(ValueError):
        controller.save(answers)

def test_get_analytics(controller):
    """Тест получения аналитики"""
    analytics = controller.get_analytics()
    assert "ages" in analytics
    assert "cities" in analytics