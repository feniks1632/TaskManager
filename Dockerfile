# Dockerfile
FROM python:3.11-slim


WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

RUN python manage.py collectstatic --noinput

# Команда запуска ASGI-сервера
CMD ["daphne", "taskflow.asgi:application", "-b", "0.0.0.0", "-p", "8080"]