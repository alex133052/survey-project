import sqlite3
import csv
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

# --- НАСТРОЙКИ ПУТЕЙ ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_FILE = DATA_DIR / "survey.db"
RAW_DATA_FILE = DATA_DIR / "raw_data.json"

DATA_DIR.mkdir(exist_ok=True)

QUESTIONS = [
    "Как тебя зовут?",
    "Сколько тебе лет?",
    "Какой твой любимый цвет?",
    "В каком городе ты живёшь?",
    "Какое у тебя хобби?",
    "Какой у тебя автомобиль?"
]

# === БЛОК РАБОТЫ С БАЗОЙ ДАННЫХ ===

def clean_keys(obj):
    """Рекурсивно убирает пробелы из ключей"""
    if isinstance(obj, dict):
        return {k.strip(): clean_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_keys(item) for item in obj]
    return obj

def init_db():
    """Создаёт таблицы и импортирует данные из JSON"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Таблица ответов опроса
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица пользователей (из data.json)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    
    # Проверяем, есть ли уже пользователи
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Пытаемся импортировать из JSON
        try:
            with open(RAW_DATA_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            # Очищаем ключи от пробелов
            clean_data = clean_keys(raw_data)
            
            # Вставляем в базу
            for user in clean_data:
                cursor.execute(
                    "INSERT INTO users (name, city, status) VALUES (?, ?, ?)",
                    (user.get("name", ""), user.get("city", ""), user.get("status", ""))
                )
            
            conn.commit()
            print(f"✅ Импортировано {len(clean_data)} пользователей из JSON")
        except FileNotFoundError:
            print("⚠️ Файл raw_data.json не найден")
        except Exception as e:
            print(f" Ошибка при импорте JSON: {e}")
    
    conn.close()

def get_city_hints():
    """Возвращает список городов из таблицы users"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT city FROM users ORDER BY city")
        cities = [row[0] for row in cursor.fetchall()]
        conn.close()
        return cities
    except:
        return []

def save_to_db(answers_list):
    """Сохраняет ответы опроса в БД"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        for q, a in answers_list:
            cursor.execute("INSERT INTO responses (question, answer) VALUES (?, ?)", (q, a))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", str(e))
        return False

def get_analytics():
    """Возвращает полную аналитику из обеих таблиц"""
    analytics_text = ""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # === СТАТИСТИКА ПО ПОЛЬЗОВАТЕЛЯМ (из JSON) ===
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        if users_count > 0:
            analytics_text += "👥 БАЗА ПОЛЬЗОВАТЕЛЕЙ (из data.json)\n"
            analytics_text += "=" * 40 + "\n"
            analytics_text += f"Всего пользователей: {users_count}\n\n"
            
            # Статусы
            cursor.execute("""
                SELECT status, COUNT(*) as cnt 
                FROM users 
                GROUP BY status 
                ORDER BY cnt DESC
            """)
            statuses = cursor.fetchall()
            analytics_text += "📊 Статусы:\n"
            for status, count in statuses:
                emoji = "✅" if status == "active" else "⏸️" if status == "inactive" else "⏳"
                analytics_text += f"   {emoji} {status}: {count}\n"
            
            # Города
            cursor.execute("""
                SELECT city, COUNT(*) as cnt 
                FROM users 
                GROUP BY city 
                ORDER BY cnt DESC
            """)
            cities = cursor.fetchall()
            analytics_text += "\n🌍 Города:\n"
            for city, count in cities:
                analytics_text += f"   • {city}: {count}\n"
        
        analytics_text += "\n" + "=" * 40 + "\n"
        
        # === СТАТИСТИКА ПО ОПРОСУ ===
        cursor.execute("SELECT COUNT(DISTINCT id/6) FROM responses")
        # Грубый подсчёт анкет (каждые 6 ответов = 1 анкета)
        cursor.execute("SELECT COUNT(*) FROM responses")
        total_responses = cursor.fetchone()[0]
        analytics_text += f"📝 ОТВЕТЫ НА ОПРОС\n"
        analytics_text += f"Всего ответов: {total_responses}\n\n"

        if total_responses == 0:
            return analytics_text + "📭 Пока нет данных опроса."

        # Возраст
        analytics_text += "🎂 Возраст:\n"
        cursor.execute("""
            SELECT answer, COUNT(*) as cnt 
            FROM responses 
            WHERE question LIKE '%лет%' 
            GROUP BY answer 
            ORDER BY CAST(answer AS INTEGER)
        """)
        age_stats = cursor.fetchall()
        if age_stats:
            for age, count in age_stats:
                analytics_text += f"   • {age} лет: {count}\n"
        else:
            analytics_text += "   (Нет данных)\n"

        # Города из опроса
        analytics_text += "\n🏙️ Города из опроса:\n"
        cursor.execute("""
            SELECT answer, COUNT(*) as cnt 
            FROM responses 
            WHERE question LIKE '%город%' 
            GROUP BY answer 
            ORDER BY cnt DESC 
            LIMIT 5
        """)
        cities_survey = cursor.fetchall()
        if cities_survey:
            for city, count in cities_survey:
                analytics_text += f"   • {city}: {count}\n"
        else:
            analytics_text += "   (Нет данных)\n"

        conn.close()
    except sqlite3.Error as e:
        return f" Ошибка SQL: {e}"
    
    return analytics_text

def export_db_to_csv(csv_path):
    """Экспорт ответов опроса в CSV"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM responses ORDER BY id")
        rows = cursor.fetchall()
        conn.close()

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer"])
            for row in rows:
                writer.writerow(row)
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", str(e))
        return False

# === ИНТЕРФЕЙС (GUI) ===

def build_survey_tab(notebook):
    """Вкладка 1: Опрос с подсказками"""
    frame = ttk.Frame(notebook, padding=20)
    notebook.add(frame, text=" Опрос")

    entries = []
    city_hints = get_city_hints()
    
    for i, q in enumerate(QUESTIONS):
        ttk.Label(frame, text=q).grid(row=i, column=0, sticky="w", pady=5)
        entry = ttk.Entry(frame, width=40)
        entry.grid(row=i, column=1, padx=10, pady=5)
        
        # Добавляем подсказку для города
        if "город" in q.lower() and city_hints:
            hint_text = ", ".join(city_hints[:5])  # Показываем первые 5
            ttk.Label(frame, text=f"💡 {hint_text}", 
                     foreground="gray", font=("Arial", 8)).grid(
                row=i, column=2, padx=5, sticky="w")
        
        entries.append(entry)

    def save_action():
        if not entries[1].get().strip().isdigit():
            messagebox.showerror("Ошибка", "Возраст должен быть числом!")
            return

        answers = []
        for i, entry in enumerate(entries):
            val = entry.get().strip()
            if not val:
                messagebox.showwarning("Внимание", f"Заполните поле: '{QUESTIONS[i]}'")
                return
            answers.append((QUESTIONS[i], val))

        if save_to_db(answers):
            messagebox.showinfo("Успех", "✅ Данные сохранены в базу!")
            for entry in entries:
                entry.delete(0, tk.END)

    btn_save = ttk.Button(frame, text="Сохранить в базу", command=save_action)
    btn_save.grid(row=len(QUESTIONS), column=0, columnspan=2, pady=20)

def build_analytics_tab(notebook):
    """Вкладка 2: Аналитика"""
    frame = ttk.Frame(notebook, padding=20)
    notebook.add(frame, text=" Аналитика")

    text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
    text.pack(fill=tk.BOTH, expand=True, pady=10)
    text.config(state='disabled')

    def load_action():
        text.config(state='normal')
        text.delete('1.0', tk.END)
        stats = get_analytics()
        text.insert(tk.END, stats)
        text.config(state='disabled')

    btn_load = ttk.Button(frame, text="Обновить аналитику", command=load_action)
    btn_load.pack()

def build_export_tab(notebook):
    """Вкладка 3: Экспорт"""
    frame = ttk.Frame(notebook, padding=20)
    notebook.add(frame, text="📤 Экспорт")

    lbl = ttk.Label(frame, text="Экспорт ответов опроса в CSV", wraplength=300)
    lbl.pack(pady=20)

    def export_action():
        path = DATA_DIR / "survey_export.csv"
        if export_db_to_csv(path):
            messagebox.showinfo("Успех", f"Экспорт завершен!\nФайл: {path}")
    
    btn = ttk.Button(frame, text="Экспортировать в CSV", command=export_action)
    btn.pack()

# === ГЛАВНАЯ ФУНКЦИЯ ===

def main():
    init_db()

    root = tk.Tk()
    root.title("Система сбора данных v3.1 (SQLite + JSON)")
    root.geometry("700x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    build_survey_tab(notebook)
    build_analytics_tab(notebook)
    build_export_tab(notebook)

    root.mainloop()

if __name__ == "__main__":
    main()