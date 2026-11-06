# AskSmth

Сайт вопросов и ответов на Django, HTML, CSS и Bootstrap.

## Локальный запуск

В терминале из корневой папки проекта выполните:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

Сайт доступен по адресу: http://127.0.0.1:8000/

## Запуск через Docker

Для запуска необходим установленный Docker.

    docker compose up --build

Сайт доступен по адресу: http://localhost:8000/

Для остановки сервера нажмите Ctrl+C.

## Страницы

- `/` — главная страница со списком новых вопросов.
- `/hot/` — популярные вопросы.
- `/tag/css/` — вопросы по тегу.
- `/question/35/` — вопрос и ответы.
- `/ask/` — создание вопроса.
- `/login/` — вход.
- `/signup/` — регистрация.
- `/profile/` — редактирование профиля.

## Структура проекта

- `application/` — настройки Django и маршрутизация.
- `core/` — страницы пользователей и статические файлы.
- `questions/` — вопросы, ответы и пагинация.
- `templates/` — базовый шаблон и общие компоненты.
- `public/` — исходная статическая версия сайта.
