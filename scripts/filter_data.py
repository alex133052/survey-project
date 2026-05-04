import json
from pathlib import Path
import os

# --- Универсальное определение пути к файлу ---
try:
    script_dir = Path(__file__).parent
except NameError:
    script_dir = Path.cwd()

data_path = script_dir / "data.json"

print(f"🔍 Ищу файл: {data_path.resolve()}")
print("-" * 40)

try:
    if not data_path.exists():
        print("❌ Ошибка: Файл 'data.json' не найден!")
        print(f"📍 Полный путь: {data_path.resolve()}")
        print(f"\n📂 Файлы в папке: {os.listdir(script_dir)}")
    else:
        with open(data_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
            # ВОТ ЗДЕСЬ БЫЛА ОШИБКА — должно быть "if not data:"
            if not data:
                print("⚠️ Файл пустой или не содержит записей.")
            else:
                active_users = [user for user in data if user.get("status") == "active"]
                
                if active_users:
                    print(f"✅ Найдено активных пользователей: {len(active_users)}")
                    print("-" * 40)
                    for user in active_users:
                        name = user.get("name", "Не указано")
                        city = user.get("city", "Не указано")
                        print(f"Имя: {name}, Город: {city}")
                else:
                    print("ℹ️ Активных пользователей не найдено.")

except json.JSONDecodeError as e:
    print("❌ Ошибка: Неверный формат JSON!")
    print(f"📝 Детали: {e}")
    
except Exception as e:
    print(f"❌ Ошибка: {type(e).__name__}: {e}")