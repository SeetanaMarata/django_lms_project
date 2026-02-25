# Dockerfile
# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости (например, для PostgreSQL клиента)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы с зависимостями Python
COPY pyproject.toml poetry.lock* /app/

# Конфигурируем poetry: не создавать виртуальное окружение, т.к. мы уже в контейнере
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости проекта
RUN poetry install --no-interaction --no-ansi

# Копируем весь код проекта
COPY . .

# Указываем порт, который будет слушать приложение
EXPOSE 8000

# Команда по умолчанию (может быть переопределена в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]