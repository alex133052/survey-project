FROM python:3.11-slim

WORKDIR /app

# Копируем всё в контейнер
COPY . .

# Устанавливаем uv и все нужные библиотеки одной командой
RUN pip install --no-cache-dir uv
RUN uv pip install --system fastapi uvicorn[standard] pydantic psycopg2-binary

# Создаем папку для данных
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]