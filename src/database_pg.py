import psycopg2
import os  # <--- ОБЯЗАТЕЛЬНО должен быть здесь
from psycopg2.extras import RealDictCursor
from typing import List, Tuple
from pathlib import Path

class PostgresDatabaseManager:
    """Управление базой данных PostgreSQL"""
    
    def __init__(self):
        # Берем хост из переменной окружения (в CI/CD это localhost)
        host = os.getenv("DATABASE_HOST", "localhost")
        
        # Берем пароль из переменной окружения (в CI/CD это test_password)
        password = os.getenv("DATABASE_PASSWORD", "secret")
        
        # Формируем строку подключения ДИНАМИЧЕСКИ
        self.dsn = f"dbname=survey_db user=postgres password={password} host={host} port=5432"
        self._conn = None

    def _get_connection(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.dsn)
            self._conn.cursor_factory = RealDictCursor
        return self._conn

    def init_db(self) -> None:
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id SERIAL PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_answers(self, answers: List[Tuple[str, str]]) -> bool:
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO responses (question, answer) VALUES (%s, %s)",
                    answers
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False

    def get_analytics_data(self) -> dict:
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT answer, COUNT(*) as cnt 
                FROM responses 
                WHERE question LIKE '%лет%' 
                GROUP BY answer 
                ORDER BY CAST(answer AS INTEGER)
            """)
            ages = cur.fetchall()
            
            cur.execute("""
                SELECT answer, COUNT(*) as cnt 
                FROM responses 
                WHERE question LIKE '%город%' 
                GROUP BY answer 
                ORDER BY cnt DESC 
                LIMIT 5
            """)
            cities = cur.fetchall()
            
            return {"ages": ages, "cities": cities}

    def export_to_csv(self, csv_path: Path) -> bool:
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT question, answer FROM responses ORDER BY id")
                rows = cur.fetchall()
            
            import csv
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Question", "Answer"])
                writer.writerows(rows)
            return True
        except Exception as e:
            print(f"Export Error: {e}")
            return False

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None