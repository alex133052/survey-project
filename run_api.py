from api import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Запуск Survey API на http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)