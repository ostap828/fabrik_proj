# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-tk \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Создаем директорию для изображений
RUN mkdir -p images

# Устанавливаем переменные окружения для базы данных
ENV DB_NAME=clothing_factory
ENV DB_USER=postgres
ENV DB_PASSWORD=Ostap_628
ENV DB_HOST=db
ENV DB_PORT=5433

# Запускаем приложение
CMD ["python", "clothing_factory_gui.py"]
