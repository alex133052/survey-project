import pytest
from pathlib import Path
import sys
import tempfile
import os
import gc

# Добавляем путь к проекту, чтобы видеть src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import DatabaseManager
from survey import SurveyController

# --- ФИКСТУРЫ (Подготовка данных для тестов) ---

@pytest.fixture
def db_manager():
    """Создает временную базу данных для тестов, чтобы не ломать настоящую"""
    # Создаём временный файл
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_fd)
    
    db = DatabaseManager(Path(temp_path))
    db.init_db()
    
    yield db
    
    # Закрываем соединение и освобождаем файл
    db.close()
    gc.collect()  # Принудительная сборка мусора
    
    # Удаляем файл после теста
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except PermissionError:
            pass  # Игнорируем, если файл ещё заблокирован

@pytest.fixture
def controller(db_manager):
    """Создает контроллер с подключенной временной базой"""
    return SurveyController(db_manager)

# --- ТЕСТЫ ---

def test_valid_survey(controller):
    """Тест: Правильные данные должны сохраняться"""
    data = [
        ("Как тебя зовут?", "Иван"),
        ("Сколько тебе лет?", "25"),  # Число - ОК
        ("Цвет", "Синий"),
        ("Город", "Москва"),
        ("Хобби", "Спорт"),
        ("Авто", "BMW")
    ]
    assert controller.save(data) is True

def test_invalid_age(controller):
    """Тест: Текст вместо возраста должен вызывать ошибку"""
    data = [
        ("Как тебя зовут?", "Иван"),
        ("Сколько тебе лет?", "Двадцать"),  # ОШИБКА
        ("Цвет", "Синий"),
        ("Город", "Москва"),
        ("Хобби", "Спорт"),
        ("Авто", "BMW")
    ]
    with pytest.raises(ValueError) as excinfo:
        controller.save(data)
    assert "Возраст должен быть числом" in str(excinfo.value)

def test_empty_field(controller):
    """Тест: Пустое поле должно вызывать ошибку"""
    data = [
        ("Как тебя зовут?", ""),  # ОШИБКА
        ("Сколько тебе лет?", "25"),
        ("Цвет", "Синий"),
        ("Город", "Москва"),
        ("Хобби", "Спорт"),
        ("Авто", "BMW")
    ]
    with pytest.raises(ValueError) as excinfo:
        controller.save(data)
    # Проверяем, что в ошибке есть упоминание пустого поля
    assert "пустым" in str(excinfo.value)

def test_analytics_empty(controller):
    """Тест: Аналитика на пустой базе не должна падать"""
    report = controller.db.get_analytics_data()  # Прямой доступ к БД для проверки
    assert report["ages"] == []
    assert report["cities"] == []