import pytest
from pathlib import Path
import sys
import tempfile
import os
import gc

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import DatabaseManager

@pytest.fixture
def db():
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_fd)
    
    database = DatabaseManager(Path(temp_path))
    database.init_db()
    
    yield database
    
    database.close()
    gc.collect()
    
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except PermissionError:
            pass

def test_db_creation(db):
    cursor = db._get_connection().cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='responses'")
    result = cursor.fetchone()
    assert result is not None

def test_save_and_retrieve(db):
    data = [("Вопрос 1", "Ответ 1"), ("Вопрос 2", "Ответ 2")]
    result = db.save_answers(data)
    assert result is True
    
    stats = db.get_analytics_data()
    assert "ages" in stats