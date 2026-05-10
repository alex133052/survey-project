from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse  # <--- Добавлено для отдачи HTML
from pydantic import BaseModel
from typing import List
import os

# Импорт нашего класса базы данных
from src.database_pg import PostgresDatabaseManager

app = FastAPI()

# Инициализация менеджера базы данных
db = PostgresDatabaseManager()

# Пытаемся подключиться и создать таблицы при старте приложения
try:
    db.init_db()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"️ Warning: Could not init DB at startup: {e}")

# --- Модели данных (Pydantic) ---

class Answer(BaseModel):
    question: str
    answer: str

class SurveyRequest(BaseModel):
    answers: List[Answer]

# --- Маршруты (Routes) ---

@app.get("/")
def read_root():
    """
    Главный маршрут. Возвращает HTML-страницу с формой опроса.
    """
    # Путь указывается относительно корня проекта (WORKDIR /app в Docker)
    # Файл index.html лежит в папке src
    return FileResponse("src/index.html")

@app.post("/survey/submit")
def submit_survey(request: SurveyRequest):
    """
    Принимает ответы на опрос и сохраняет их в Базу Данных.
    """
    try:
        # Преобразуем список объектов Answer в список кортежей (question, answer)
        data_to_save = [(ans.question, ans.answer) for ans in request.answers]
        
        # Сохраняем в БД
        success = db.save_answers(data_to_save)
        
        if success:
            return {"status": "success", "message": "Сохранено"}
        else:
            raise HTTPException(status_code=500, detail="Ошибка сохранения в БД")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/survey/analytics")
def get_analytics():
    """
    Возвращает статистику по ответам.
    """
    try:
        data = db.get_analytics_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))