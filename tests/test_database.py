import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database_pg import PostgresDatabaseManager

@pytest.fixture
def db():
    """Фикстура для создания менеджера БД"""
    database = PostgresDatabaseManager()
    yield database
    database.close()

def test_init_db(db):
    """Тест создания таблицы"""
    # Если ошибок нет — таблица создана успешно
    db.init_db()
    assert True

def test_save_answers(db):
    """Тест сохранения ответов"""
    answers = [
        ("Вопрос 1", "Ответ 1"),
        ("Вопрос 2", "Ответ 2")
    ]
    result = db.save_answers(answers)
    assert result == True

def test_get_analytics_data(db):
    """Тест получения аналитики"""
    # Сначала добавим тестовые данные
    answers = [
        ("Сколько тебе лет?", "30"),
        ("В каком городе ты живёшь?", "Казань")
    ]
    db.save_answers(answers)
    
    # Получаем аналитику
    analytics = db.get_analytics_data()
    
    assert "ages" in analytics
    assert "cities" in analytics
    assert isinstance(analytics["ages"], list)
    assert isinstance(analytics["cities"], list)