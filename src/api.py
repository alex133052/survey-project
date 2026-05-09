from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pathlib import Path

from .database_pg import PostgresDatabaseManager
from .survey import SurveyController

app = FastAPI(title="Survey API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = PostgresDatabaseManager()
db.init_db()
controller = SurveyController(db)

class SurveyAnswer(BaseModel):
    question: str
    answer: str

class SurveySubmit(BaseModel):
    answers: List[SurveyAnswer]

@app.get("/")
def root():
    return {"message": "Survey API (PostgreSQL)", "docs": "/docs"}

@app.post("/survey/submit")
def submit_survey(data: SurveySubmit):
    try:
        answers_tuple = [(item.question, item.answer) for item in data.answers]
        success = controller.save(answers_tuple)
        if success:
            return {"status": "success", "message": "Сохранено"}
        raise HTTPException(status_code=500, detail="Не удалось сохранить")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/survey/analytics")
def get_analytics():
    try:
        raw_data = db.get_analytics_data()
        ages = {str(row["answer"]): row["cnt"] for row in raw_data["ages"]}
        cities = {str(row["answer"]): row["cnt"] for row in raw_data["cities"]}
        return {"ages": ages, "cities": cities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/survey/responses")
def get_responses():
    try:
        conn = db._get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM responses ORDER BY id DESC")
            rows = cur.fetchall()
        return {"count": len(rows), "data": [dict(row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/survey/export")
def export_csv():
    csv_path = Path(__file__).parent.parent / "data" / "export_api.csv"
    if db.export_to_csv(csv_path):
        return {"status": "success", "path": str(csv_path)}
    raise HTTPException(status_code=500, detail="Ошибка экспорта")