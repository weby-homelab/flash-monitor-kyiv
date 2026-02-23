FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Kyiv \
    DATA_DIR=/app/data

RUN apt-get update && apt-get install -y \
    tzdata \
    libfreetype6-dev \
    libpng-dev \
    curl \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
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
CMD ["gunicorn", "--workers", "4", "--threads", "4", "-b", "0.0.0.0:5050", "app:app"]
