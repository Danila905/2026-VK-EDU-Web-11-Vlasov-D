# AskSmth

Сайт вопросов и ответов на Django, HTML, CSS и Bootstrap.

## Первый запуск

Проект использует Django и PostgreSQL 16. Все команды выполняются из папки с manage.py.

### Настройки окружения

В свежей копии проекта создайте `.env.local` из образца:

    cp .env.example .env.local

Откройте `.env.local` и заполните `DJANGO_SECRET_KEY` и `POSTGRES_PASSWORD`.
Для каждого значения отдельно сгенерируйте случайную строку командой:

    python3 -c "import secrets; print(secrets.token_hex(32))"

Оставьте `POSTGRES_HOST=127.0.0.1` для запуска Django на компьютере.
Создайте `.env.docker` с теми же значениями и адресом базы `db`:

    sed 's/^POSTGRES_HOST=.*/POSTGRES_HOST=db/' .env.local > .env.docker

### Запуск через Docker

Запустите Docker Desktop, затем выполните:

    docker compose build web
    docker compose up -d --wait db
    docker compose run --rm web python manage.py migrate
    docker compose up -d web

Сайт доступен по адресу http://127.0.0.1:8000/.
На пустой базе главная страница показывает сообщение «Пока нет ни одного вопроса».

### Админка и тестовые данные

Создайте администратора и войдите на http://127.0.0.1:8000/admin/:

    docker compose exec web python manage.py createsuperuser

Для быстрой проверки добавьте 10 пользователей, 10 тегов, 100 вопросов,
1 000 ответов и 2 000 оценок:

    docker compose exec web python manage.py fill_db 10

Для проверки полного объёма после малого запуска выполните:

    docker compose exec -e DJANGO_DEBUG=0 web python manage.py fill_db 10000

Каждый запуск добавляет новую порцию данных. Коэффициент 10001 позволяет
превысить все пороги задания за один запуск на пустой базе.

Остановка проекта с сохранением данных PostgreSQL:

    docker compose down

### Локальный запуск Django

Можно запустить в Docker только PostgreSQL, а Django — в виртуальном окружении.
Если контейнер web уже запущен, сначала освободите порт 8000 командой
`docker compose stop web`. Затем выполните:

    docker compose up -d --wait db
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

Django использует `.env.local` и подключается к той же базе.
При `DJANGO_DEBUG=1` на локальных страницах доступна Django Debug Toolbar.

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
