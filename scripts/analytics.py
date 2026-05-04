import sqlite3

conn = sqlite3.connect("survey.db")
cursor = conn.cursor()

print("🔍 ЗАПУСК СЛОЖНЫХ SQL-ЗАПРОСОВ 🔍")
print("=" * 40)

# 1. Сколько УНИКАЛЬНЫХ городов? (DISTINCT)
cursor.execute("SELECT COUNT(DISTINCT answer) FROM responses WHERE question LIKE '%город%'")
unique_cities = cursor.fetchone()[0]
print(f"🌍 Уникальных городов в базе: {unique_cities}")

# 2. Какие города и сколько раз встречались? (GROUP BY)
print("\n🏆 Топ городов:")
cursor.execute("""
    SELECT answer, COUNT(*) 
    FROM responses 
    WHERE question LIKE '%город%' 
    GROUP BY answer 
    ORDER BY COUNT(*) DESC
""")
for city, count in cursor.fetchall():
    print(f"   - {city}: {count} раз")

# 3. Средний возраст (AVG)
print("\n Средний возраст:")
cursor.execute("SELECT AVG(answer) FROM responses WHERE question LIKE '%лет%'")
avg_age = cursor.fetchone()[0]
if avg_age:
    print(f"   Средний: {avg_age:.1f} лет")
else:
    print("   Нет данных")

conn.close()