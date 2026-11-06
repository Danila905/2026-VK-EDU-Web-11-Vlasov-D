EXAMPLES = [
    ('Как правильно подключить Bootstrap?', 'Изучаю HTML и CSS. Подскажите, как правильно использовать сетку Bootstrap?', ['Bootstrap', 'CSS']),
    ('Как создать адаптивную страницу?', 'Хочу сделать сайт, который хорошо выглядит на компьютере и телефоне.', ['CSS']),
    ('Почему CSS не применяется к элементу?', 'Подключил файл стилей, но цвет текста не меняется. Что проверить?', ['CSS', 'HTML']),
    ('Как установить Django?', 'Как создать виртуальное окружение и запустить первый Django-проект?', ['Django', 'Python']),
    ('Как работают HTML-формы?', 'В чём разница между GET и POST?', ['HTML', 'Django']),
    ('Как использовать CSS Grid?', 'Как расположить карточки на странице?', ['CSS', 'Bootstrap']),
    ('Как сделать пагинацию?', 'Как разбить список вопросов на страницы?', ['Django', 'Python']),
    ('Как сортировать массив?', 'Хочу разобраться с сортировкой слиянием.', ['Python']),
    ('Как хранить данные?', 'Когда применять SQLite и PostgreSQL?', ['Django']),
    ('Как установить Git?', 'Как настроить Git и отправить изменения?', ['Python']),
]
AUTHORS = ['Danila Vlasov', 'Alex Developer', 'Maria Code', 'Max Coder']
QUESTIONS = []
for i in range(1, 36):
    title, text, tags = EXAMPLES[(i - 1) % len(EXAMPLES)]
    QUESTIONS.append({
        'id': i,
        'title': title,
        'text': text,
        'tags': [{'name': t, 'slug': t.lower()} for t in tags],
        'author': AUTHORS[(i - 1) % len(AUTHORS)],
        'created': '2 нояб. 2026, 14:27',
        'votes': 12 if i == 1 else 6 if i == 2 else i % 14,
        'vote_state': 'up' if i == 1 else 'down' if i == 2 else 'none',
        'answer_count': 3 if i == 1 else 5 if i == 2 else i % 6 + 1,
    })

ANSWER_TEXTS = [
    'Скачай Bootstrap и положи CSS и JS в папку static. Для сетки используй container, row и col.',
    'Для простой страницы достаточно Bootstrap CSS. JavaScript нужен для меню и модальных окон.',
    'Рекомендую начать с официальной документации и примеров Bootstrap.',
    'Также проверь путь к CSS и кэш браузера.',
    'Адаптивную разметку удобно строить через стандартную сетку Bootstrap.',
]


def get_answers(question):
    return [
        {
            'id': i,
            'text': ANSWER_TEXTS[(i - 1) % len(ANSWER_TEXTS)],
            'author': AUTHORS[i % len(AUTHORS)],
            'created': '3 нояб. 2026, 16:03',
            'votes': 8 if i == 1 else i + 1,
            'vote_state': 'up' if i == 1 else 'none',
            'correct': i == 1,
        }
        for i in range(1, question['answer_count'] + 1)
    ]
