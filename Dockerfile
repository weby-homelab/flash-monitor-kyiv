FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data

RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libpng-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копіюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код
COPY . .

# Створюємо структуру для даних
RUN mkdir -p /app/data/static

EXPOSE 5050

# За замовчуванням запускаємо веб-сервер
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5050", "--workers", "4"]
