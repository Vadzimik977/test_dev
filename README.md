### Установка

1. Заполнить `data_test/config.py`
2. Запустить `docker compose up -d`

### При изменении данных

1. Запустить `docker compose down` (остановить контейнер)
2. Запустить `docker compose up -d --build` (пересобрать контейнер и запустить его)

docker compose stop && docker compose up --build -d
