"""
Запуск приложения Survey System
Просто выполните: python run.py
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь импорта
sys.path.insert(0, str(Path(__file__).parent))

# Импортируем и запускаем GUI
from src.gui_app import main

if __name__ == "__main__":
    main()