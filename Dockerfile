# Используем базовый образ Python
FROM python:3.11-slim

# Устанавливаем дополнительные зависимости, если они необходимы
RUN apt update && \
    apt install ffmpeg -y && \
    apt clean -y && \
    rm -rf /var/lib/apt/* /var/log/* /var/cache/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл requirements.txt и устанавливаем зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в рабочую директорию контейнера
COPY . .

# Устанавливаем команду по умолчанию для запуска контейнера
CMD ["python", "test.py"]
