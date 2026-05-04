import sqlite3

conn = sqlite3.connect("survey.db")
cursor = conn.cursor()

# Показываем все записи
cursor.execute("SELECT * FROM responses ORDER BY id")
rows = cursor.fetchall()

print(f"{'ID':<5} {'Вопрос':<30} {'Ответ':<20} {'Дата':<20}")
print("-" * 80)

for row in rows:
    id_, question, answer, created_at = row
    print(f"{id_:<5} {question:<30} {answer:<20} {created_at:<20}")

conn.close()