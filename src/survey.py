from typing import List, Tuple

class SurveyController:
    def __init__(self, db):
        self.db = db

    def save(self, answers: List[Tuple[str, str]]) -> bool:
        if not answers:
            raise ValueError("Нет ответов для сохранения")
        
        for question, answer in answers:
            if not question or not answer:
                raise ValueError("Вопрос и ответ не могут быть пустыми")
        
        return self.db.save_answers(answers)

    def get_analytics(self) -> dict:
        return self.db.get_analytics_data()