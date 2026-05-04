"""
================================================================================
 СИСТЕМА СБОРА ДАННЫХ v1.0
================================================================================

ОПИСАНИЕ:
    Консольное приложение для проведения опросов, анализа данных и экспорта.

ВОЗМОЖНОСТИ:
    1. Интерактивный опрос с валидацией (возраст — только числа)
    2. Просмотр отчёта по заполненным анкетам
    3. Аналитика по базе данных (статусы, топ городов, средний возраст)
    4. Экспорт результатов в Excel/CSV
    5. Умные подсказки из clean_data.json

ИНСТРУКЦИЯ ПО ЗАПУСКУ:
    1. Запустите скрипт: python main.py
    2. Выберите пункт меню (1-5)
    3. Для выхода используйте пункт 5 или Ctrl+C

ТРЕБУЕМЫЕ ФАЙЛЫ:
    - data.json (база пользователей для аналитики)
    - clean_data.json (очищенная версия, создаётся скриптом очистки)

АВТОР: Создано в рамках курса по промт-инженерингу
ВЕРСИЯ: 1.0
ДАТА: 2026
================================================================================
"""

import json
import csv
from pathlib import Path
from collections import Counter
import time

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
APP_VERSION = "1.0"
try:
    base_dir = Path(__file__).parent
except NameError:
    base_dir = Path.cwd()

SURVEY_FILE = base_dir / "survey_responses.json"
CLEAN_DATA_FILE = base_dir / "clean_data.json"

QUESTIONS = [
    "Как тебя зовут? ",
    "Сколько тебе лет? ",
    "Какой твой любимый цвет? ",
    "В каком городе ты живёшь? ",
    "Какое у тебя хобби? ",
    "Какой у тебя автомобиль? "
]

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def clean_keys(obj):
    """Рекурсивно очищает ключи и строки от пробелов"""
    if isinstance(obj, dict):
        return {k.strip(): clean_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_keys(item) for item in obj]
    return obj

def load_city_hints():
    """Загружает уникальные города из clean_data.json"""
    try:
        with open(CLEAN_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data = clean_keys(data)
        cities = list(set(item.get("city", "") for item in data if item.get("city")))
        return cities
    except Exception:
        return []

# === ОСНОВНЫЕ ФУНКЦИИ ===

def run_survey():
    """1. Запускает интерактивный опрос с валидацией"""
    print("\n🚀 ЗАПУСК ОПРОСНИКА")
    print("=" * 40)
    
    city_hints = load_city_hints()
    responses = []
    
    for i, q in enumerate(QUESTIONS, 1):
        while True:
            if "город" in q.lower() and city_hints:
                print(f"💡 Подсказка из базы: {', '.join(city_hints)}")
            
            ans = input(f"Вопрос {i}: {q}")
            
            if not ans.strip():
                print("⚠️ Ответ не может быть пустым. Попробуйте ещё раз.")
                continue
            
            if "лет" in q.lower() or "возраст" in q.lower():
                if not ans.strip().isdigit():
                    print("❌ Ошибка: возраст должен быть числом! (например, 25)")
                    continue
            
            responses.append({"question": q.strip(), "answer": ans.strip()})
            break
    
    with open(SURVEY_FILE, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
    
    print("-" * 40)
    print(f"✅ Готово! {len(responses)} ответов сохранены.")
    print(f"📁 Файл: {SURVEY_FILE.name}")
    time.sleep(1.5)

def show_report():
    """2. Показывает отчёт по заполненной анкете"""
    print("\n📋 ОТЧЁТ ПО ОПРОСУ")
    print("=" * 40)
    
    try:
        with open(SURVEY_FILE, "r", encoding="utf-8") as f:
            responses = json.load(f)
        
        total, filled = 6, 0
        for item in responses:
            q = item.get("question", "Неизвестный вопрос")
            a = item.get("answer", "")
            print(f" Вопрос: {q}\n💬 Ответ: {a}\n" + "-" * 30)
            if a.strip():
                filled += 1
        
        print("=" * 40)
        if filled == total:
            print("✅ Анкета полная")
        else:
            print(f"⚠️ Заполнены {filled} из {total}")
            
    except FileNotFoundError:
        print("❌ Файл не найден.")
        print("💡 Сначала пройдите опрос (пункт 1).")
    except json.JSONDecodeError:
        print("❌ Ошибка формата JSON. Файл повреждён.")
    
    time.sleep(1.5)

def show_analytics():
    """3. Показывает аналитику по базе данных"""
    print("\n📊 АНАЛИТИКА ПО БАЗЕ ДАННЫХ")
    print("=" * 40)
    
    try:
        with open(CLEAN_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data = clean_keys(data)
        
        if not data:
            print("⚠️ База данных пуста.")
            return
        
        # Статусы
        statuses = Counter(item.get("status", "unknown") for item in data)
        print("🔹 Статусы пользователей:")
        for status, count in statuses.most_common():
            print(f"   • {status}: {count}")
        
        # Топ городов
        cities = Counter(item.get("city", "") for item in data if item.get("city"))
        print("\n🔹 Топ-3 города:")
        for city, count in cities.most_common(3):
            print(f"   • {city}: {count}")
        
        # Средний возраст (если есть поле age)
        ages = [item["age"] for item in data if "age" in item and isinstance(item["age"], (int, float))]
        if ages:
            avg_age = sum(ages) / len(ages)
            print(f"\n Средний возраст: {avg_age:.1f} лет")
        
        print(f"\n✅ Всего записей: {len(data)}")
        
    except FileNotFoundError:
        print("❌ Файл clean_data.json не найден.")
        print(" Сначала запустите скрипт очистки данных.")
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
    
    time.sleep(2)

def export_to_csv():
    """4. Экспортирует результаты опроса в CSV"""
    print("\n📤 ЭКСПОРТ В CSV")
    print("=" * 40)
    
    try:
        with open(SURVEY_FILE, "r", encoding="utf-8") as f:
            responses = json.load(f)
        
        csv_path = base_dir / "survey_results.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            for item in responses:
                writer.writerow([item.get("question", ""), item.get("answer", "")])
        
        print(f"✅ Экспортировано {len(responses)} записей.")
        print(f"📁 Файл: {csv_path.resolve()}")
        print("💡 Откройте в Excel или Google Таблицах.")
        
    except FileNotFoundError:
        print(" Файл опроса не найден.")
        print("💡 Сначала пройдите опрос (пункт 1).")
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {type(e).__name__}: {e}")
    
    time.sleep(2)

def main_menu():
    """5. Главное меню приложения"""
    while True:
        print("\n" + "=" * 40)
        print("🎯 СИСТЕМА СБОРА ДАННЫХ")
        print("=" * 40)
        print("1. Пройти опрос")
        print("2. Показать отчёт")
        print("3. Аналитика по базе")
        print("4. Экспорт в Excel/CSV")
        print("5. Выйти")
        print("=" * 40)
        
        try:
            choice = input("Выберите пункт (1-5): ").strip()
            
            if choice == "1":
                run_survey()
            elif choice == "2":
                show_report()
            elif choice == "3":
                show_analytics()
            elif choice == "4":
                export_to_csv()
            elif choice == "5":
                print("\n До встречи! Данные сохранены.")
                break
            else:
                print("❌ Неверный выбор. Введите 1, 2, 3, 4 или 5.")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Прерывание работы (Ctrl+C)")
            print("👋 Завершение работы...")
            break

# === ТОЧКА ВХОДА ===
if __name__ == "__main__":
    print("\n" + "=" * 40)
    print(f" Система сбора данных v{APP_VERSION} запущена!")
    print("=" * 40)
    time.sleep(0.5)
    main_menu()