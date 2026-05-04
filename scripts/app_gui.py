"""
================================================================================
 СИСТЕМА СБОРА ДАННЫХ v2.0 (GUI)
================================================================================
Запуск: python app_gui.py
"""

import json
import csv
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
from collections import Counter

# --- НАСТРОЙКИ ПУТЕЙ ---
try:
    base_dir = Path(__file__).parent
except NameError:
    base_dir = Path.cwd()

SURVEY_FILE = base_dir / "survey_responses.json"
CLEAN_DATA_FILE = base_dir / "clean_data.json"
CSV_FILE = base_dir / "survey_results.csv"

# Вопросы для опроса
QUESTIONS = [
    "Как тебя зовут?",
    "Сколько тебе лет?",
    "Какой твой любимый цвет?",
    "В каком городе ты живёшь?",
    "Какое у тебя хобби?",
    "Какой у тебя автомобиль?"
]

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def clean_keys(obj):
    """Рекурсивная очистка пробелов"""
    if isinstance(obj, dict):
        return {k.strip(): clean_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_keys(item) for item in obj]
    return obj

def get_city_hints():
    """Загрузка городов для подсказки (если нужно)"""
    try:
        with open(CLEAN_DATA_FILE, "r", encoding="utf-8") as f:
            data = clean_keys(json.load(f))
        return list(set(item.get("city", "") for item in data if item.get("city")))
    except Exception:
        return []

# === ВКЛАДКА 1: ОПРОС ===

def run_survey_gui(root, entries):
    """Сбор данных из полей ввода"""
    responses = []
    
    # Валидация возраста
    age_val = entries[1].get().strip()
    if not age_val.isdigit():
        messagebox.showerror("Ошибка", "Возраст должен быть числом!")
        return

    # Сбор ответов
    for i, entry in enumerate(entries):
        val = entry.get().strip()
        if not val:
            messagebox.showwarning("Внимание", f"Заполните поле: '{QUESTIONS[i]}'")
            return
        
        responses.append({
            "question": QUESTIONS[i],
            "answer": val
        })

    # Сохранение
    try:
        with open(SURVEY_FILE, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Успех", f"✅ {len(responses)} ответов сохранены!")
        
        # Очистка полей после успеха
        for entry in entries:
            entry.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

def build_survey_tab(notebook):
    """Создание интерфейса опроса"""
    frame = ttk.Frame(notebook, padding=20)
    notebook.add(frame, text=" Опрос")

    entries = []
    
    # Генерация полей ввода
    for i, q in enumerate(QUESTIONS):
        ttk.Label(frame, text=q).grid(row=i, column=0, sticky="w", pady=5)
        entry = ttk.Entry(frame, width=40)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    # Кнопка сохранения
    btn_save = ttk.Button(frame, text="Сохранить ответы", command=lambda: run_survey_gui(root, entries))
    btn_save.grid(row=len(QUESTIONS), column=0, columnspan=2, pady=20)

    return entries

# === ВКЛАДКА 2: АНАЛИТИКА ===

def load_analytics_gui(text_widget):
    """Чтение и вывод аналитики"""
    text_widget.config(state='normal')
    text_widget.delete('1.0', tk.END)

    try:
        with open(CLEAN_DATA_FILE, "r", encoding="utf-8") as f:
            data = clean_keys(json.load(f))
        
        # ✅ ИСПРАВЛЕНО: добавлено условие "if not data:"
        if not data:
            text_widget.insert(tk.END, "⚠️ База данных пуста.")
            text_widget.config(state='disabled')
            return

        # Статусы
        statuses = Counter(item.get("status", "unknown") for item in data)
        text_widget.insert(tk.END, "🔹 Статусы:\n")
        for s, c in statuses.most_common():
            text_widget.insert(tk.END, f"   • {s}: {c}\n")
        
        # Города
        cities = Counter(item.get("city", "") for item in data if item.get("city"))
        text_widget.insert(tk.END, "\n🔹 Топ-3 города:\n")
        for city, c in cities.most_common(3):
            text_widget.insert(tk.END, f"   • {city}: {c}\n")

        # Средний возраст
        ages = [item["age"] for item in data if "age" in item and isinstance(item["age"], (int, float))]
        if ages:
            avg = sum(ages) / len(ages)
            text_widget.insert(tk.END, f"\n🔹 Средний возраст: {avg:.1f} лет")

    except FileNotFoundError:
        text_widget.insert(tk.END, "❌ Файл clean_data.json не найден.")
    except Exception as e:
        text_widget.insert(tk.END, f"❌ Ошибка: {e}")

    text_widget.config(state='disabled')

def build_analytics_tab(notebook):
    """Создание интерфейса аналитики"""
    frame = ttk.Frame(notebook, padding=20)
    notebook.add(frame, text="📊 Аналитика")

    text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=15)
    text.pack(fill=tk.BOTH, expand=True, pady=10)
    text.config(state='disabled') # Только чтение

    btn_load = ttk.Button(frame, text="Загрузить аналитику", command=lambda: load_analytics_gui(text))
    btn_load.pack()

# === ВКЛАДКА 3: ЭКСПОРТ ===

def run_export_gui():
    """Экспорт в CSV"""
    try:
        with open(SURVEY_FILE, "r", encoding="utf-8") as f:
            responses = json.load(f)
        
        with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            for item in responses:
                writer.writerow([item.get("question"), item.get("answer")])
        
        messagebox.showinfo("Успех", f"✅ Экспортировано {len(responses)} записей.\nФайл: {CSV_FILE.name}")
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Сначала пройдите опрос, чтобы были данные для экспорта.")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def build_export_tab(notebook):
    """Создание интерфейса экспорта"""
    frame = ttk.Frame(notebook, padding=20)
    notebook.add(frame, text="📤 Экспорт")

    lbl = ttk.Label(frame, text="Нажмите кнопку для сохранения данных в Excel (CSV)", wraplength=300)
    lbl.pack(pady=20)

    btn = ttk.Button(frame, text="Экспортировать в CSV", command=run_export_gui)
    btn.pack()

# === ГЛАВНОЕ ОКНО ===

if __name__ == "__main__":
    root = tk.Tk()
    root.title(f"Система сбора данных v2.0")
    root.geometry("500x450")

    # Создание вкладок
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    build_survey_tab(notebook)
    build_analytics_tab(notebook)
    build_export_tab(notebook)

    root.mainloop()