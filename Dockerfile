FROM python:3.11-slim

# Обновляем pip и ставим системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем зависимости (сначала отдельно — для кэша)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Отключаем буферизацию вывода (для docker logs)
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "bot.py"]
# ----------------------------------------------------

