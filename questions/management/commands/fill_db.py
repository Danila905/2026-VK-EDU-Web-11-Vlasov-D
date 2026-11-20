from datetime import timedelta
from random import Random
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, reset_queries, transaction
from django.utils import timezone
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


User = get_user_model()
TOPICS = ('Python', 'Django', 'CSS', 'HTML', 'Bootstrap', 'PostgreSQL', 'Docker', 'Git')
BATCH_SIZE = 500


def batches(total):
    for start in range(0, total, BATCH_SIZE):
        yield range(start, min(start + BATCH_SIZE, total))


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми пользователями, тегами, вопросами, ответами и оценками.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Количество новых пользователей и тегов')

    @transaction.atomic
    def handle(self, *args, ratio, **options):
        if ratio < 1:
            raise CommandError('ratio должен быть положительным числом.')

        extra_voter = None
        if ratio == 1:
            extra_voter = User.objects.values_list('pk', flat=True).first()
            if extra_voter is None:
                raise CommandError(
                    'Для ratio=1 нужен ещё один пользователь для голосования. '
                    'Создайте суперпользователя или укажите ratio не меньше 2.'
                )

        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')

        self.fake = Faker('ru_RU')
        self.random = Random()
        self.run_id = uuid4().hex[:16]
        self.now = timezone.now()
        self.texts = [self.fake.paragraph(nb_sentences=3) for _ in range(512)]

        users, tags = self.create_users_and_tags(ratio)
        voters = users if extra_voter is None else [*users, extra_voter]

        for indices in batches(ratio * 10):
            self.create_questions_and_answers(indices, users, tags, voters)
            reset_queries()

        self.stdout.write(self.style.SUCCESS(
            f'Добавлено пользователей: {ratio}, тегов: {ratio}, '
            f'вопросов: {ratio * 10}, ответов: {ratio * 100}, оценок: {ratio * 200}.'
        ))

    def create_users_and_tags(self, ratio):
        user_ids = []
        tag_ids = []
        used_slugs = set(
            Tag.objects.filter(slug__in=[topic.lower() for topic in TOPICS])
            .values_list('slug', flat=True)
        )
        used_names = set(
            Tag.objects.filter(name__in=TOPICS).values_list('name', flat=True)
        )

        for indices in batches(ratio):
            accounts = []
            for i in indices:
                username = f'user_{self.run_id}_{i}'
                accounts.append(User(
                    username=username,
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    email=f'{username}@example.org',
                    password='!',
                ))

            accounts = User.objects.bulk_create(accounts)
            Profile.objects.bulk_create([Profile(user_id=user.pk) for user in accounts])
            user_ids.extend(user.pk for user in accounts)

            tags = []
            for i, user in zip(indices, accounts):
                topic = TOPICS[i % len(TOPICS)]
                slug = topic.lower()
                if i < len(TOPICS) and topic not in used_names and slug not in used_slugs:
                    tags.append(Tag(name=topic, slug=slug))
                else:
                    tags.append(Tag(
                        name=f'{topic} · {self.fake.word()} {user.pk}',
                        slug=f'{slug}-{self.run_id}-{i}',
                    ))

            tag_ids.extend(tag.pk for tag in Tag.objects.bulk_create(tags))
            reset_queries()

        return user_ids, tag_ids

    def create_questions_and_answers(self, indices, users, tags, voters):
        questions = []
        for i in indices:
            tag_index = i % len(tags)
            topic = TOPICS[tag_index % len(TOPICS)]
            title = self.random.choice((
                f'Как настроить {topic} для учебного проекта?',
                f'С чего начать работу с {topic}?',
                f'Как проверить настройки {topic}?',
            ))
            questions.append(Question(
                author_id=self.random.choice(users),
                title=title,
                text=self.random.choice(self.texts),
                created=self.now - timedelta(minutes=self.random.randrange(365 * 24 * 60)),
            ))

        questions = Question.objects.bulk_create(questions)
        links = []
        answers = []
        question_likes = []

        for i, question in zip(indices, questions):
            tag_index = i % len(tags)
            links.append(Question.tags.through(
                question_id=question.pk,
                tag_id=tags[tag_index],
            ))

            for user_id in self.random.sample(voters, 2):
                question_likes.append(QuestionLike(
                    question_id=question.pk,
                    user_id=user_id,
                    value=self.random.choice((1, 1, -1)),
                ))

            for j in range(10):
                answers.append(Answer(
                    question_id=question.pk,
                    author_id=self.random.choice(users),
                    text=self.random.choice(self.texts),
                    correct=(j == 0 and i % 3 == 0),
                    created=min(self.now, question.created + timedelta(minutes=j + 1)),
                ))

        Question.tags.through.objects.bulk_create(links)
        QuestionLike.objects.bulk_create(question_likes)
        answers = Answer.objects.bulk_create(answers, batch_size=2000)

        answer_likes = []
        for i, answer in enumerate(answers):
            voter_count = 2 if i % 10 < 8 else 1
            for user_id in self.random.sample(voters, voter_count):
                answer_likes.append(AnswerLike(
                    answer_id=answer.pk,
                    user_id=user_id,
                    value=self.random.choice((1, 1, -1)),
                ))

        AnswerLike.objects.bulk_create(answer_likes, batch_size=2000)
