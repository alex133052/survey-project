import json
from pathlib import Path

def clean_data(obj):
    """Рекурсивно очищает ключи и строки от пробелов"""
    if isinstance(obj, dict):
        return {k.strip(): clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(item) for item in obj]
    elif isinstance(obj, str):
        return obj.strip()
    return obj

# Определение папки
base_dir = Path(__file__).parent

# Чтение data.json
print("📖 Чтение data.json...")
with open(base_dir / "data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"🔴 Найдено записей: {len(raw_data)}")
print(f"🔴 Пример 'грязных' ключей: {list(raw_data[0].keys())}")

# Очистка
cleaned_data = clean_data(raw_data)

# Сохранение в clean_data.json
with open(base_dir / "clean_data.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

print(f"🟢 Очищено записей: {len(cleaned_data)}")
print(f"🟢 Пример 'чистых' ключей: {list(cleaned_data[0].keys())}")
print("\n✅ Файл clean_data.json создан!")
print(f"📁 Расположение: {base_dir / 'clean_data.json'}")