from django.conf import settings
from django.db import models
from django.db.models import Count, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone

# Create your models here.


class TagManager(models.Manager):
    def popular(self):
        return self.annotate(
            question_count=Count('questions'),
        ).order_by('-question_count', 'name')[:5]


class Tag(models.Model):
    name = models.CharField('Название', max_length=80, unique=True)
    slug = models.SlugField('Адрес', max_length=100, unique=True)
    created = models.DateTimeField('Дата создания', default=timezone.now)

    objects = TagManager()

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('questions:tag', args=[self.slug])


def vote_annotations(likes, target_field, user):
    related = likes.filter(**{target_field: OuterRef('pk')})
    totals = related.values(target_field).annotate(total=Sum('value'))
    fields = {'votes': Coalesce(Subquery(totals.values('total')), 0)}

    if user is not None and user.is_authenticated:
        fields['user_vote'] = Subquery(related.filter(user=user).values('value')[:1])

    return fields


class QuestionManager(models.Manager):
    def for_display(self, user=None):
        answers = Answer.objects.filter(question_id=OuterRef('pk'))
        counts = answers.values('question_id').annotate(total=Count('pk'))
        return self.select_related('author').prefetch_related('tags').annotate(
            answer_count=Coalesce(Subquery(counts.values('total')), 0),
            **vote_annotations(QuestionLike.objects, 'question_id', user),
        )

    def newest(self, search='', user=None):
        questions = self.for_display(user).order_by('-created', '-pk')
        if search.strip():
            questions = questions.filter(title__icontains=search.strip())
        return questions

    def best(self, user=None):
        return self.for_display(user).order_by('-votes', '-created', '-pk')

    def by_tag(self, tag, user=None):
        return self.newest(user=user).filter(tags=tag)


class Question(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Автор',
    )
    title = models.CharField('Заголовок', max_length=150)
    text = models.TextField('Текст')
    created = models.DateTimeField('Дата создания', default=timezone.now, db_index=True)
    tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='Теги', blank=True)

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('questions:question', args=[self.pk])


class AnswerManager(models.Manager):
    def for_question(self, question, user=None):
        return self.filter(question=question).select_related('author').annotate(
            **vote_annotations(AnswerLike.objects, 'answer_id', user),
        ).order_by('-correct', 'created', 'pk')


class Answer(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Автор',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос',
    )
    text = models.TextField('Текст')
    created = models.DateTimeField('Дата создания', default=timezone.now, db_index=True)
    correct = models.BooleanField('Правильный ответ', default=False)

    objects = AnswerManager()

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return self.text[:80]


class VoteValue(models.IntegerChoices):
    UP = 1, 'Лайк'
    DOWN = -1, 'Дизлайк'


class QuestionLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Вопрос',
    )
    value = models.SmallIntegerField('Оценка', choices=VoteValue.choices, default=VoteValue.UP)

    class Meta:
        verbose_name = 'Оценка вопроса'
        verbose_name_plural = 'Оценки вопросов'
        unique_together = (('user', 'question'),)
        constraints = [
            models.CheckConstraint(condition=models.Q(value__in=[-1, 1]), name='question_vote_sign'),
        ]

    def __str__(self):
        return f'{self.get_value_display()} · вопрос №{self.question_id}'


class AnswerLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Ответ',
    )
    value = models.SmallIntegerField('Оценка', choices=VoteValue.choices, default=VoteValue.UP)

    class Meta:
        verbose_name = 'Оценка ответа'
        verbose_name_plural = 'Оценки ответов'
        unique_together = (('user', 'answer'),)
        constraints = [
            models.CheckConstraint(condition=models.Q(value__in=[-1, 1]), name='answer_vote_sign'),
        ]

    def __str__(self):
        return f'{self.get_value_display()} · ответ №{self.answer_id}'
