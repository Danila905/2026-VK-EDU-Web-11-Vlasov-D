from uuid import uuid4

from django import forms
from django.db import transaction
from django.utils.text import slugify

from .models import Answer, Question, Tag


class QuestionForm(forms.ModelForm):
    title = forms.CharField(label='Заголовок вопроса', min_length=10, max_length=150)
    tag_names = forms.CharField(label='Теги', help_text='Укажите теги через запятую.')

    class Meta:
        model = Question
        fields = ('title', 'text', 'tag_names')
        labels = {'text': 'Текст вопроса'}

    def clean_tag_names(self):
        names = {}
        for part in self.cleaned_data['tag_names'].split(','):
            name = part.strip()
            if not name or len(name) > 80:
                raise forms.ValidationError('Каждый тег должен содержать от 1 до 80 символов.')
            names.setdefault(name.casefold(), name)
        return [names[key] for key in sorted(names)]

    def get_tag(self, name):
        tag = Tag.objects.filter(name__iexact=name).first()
        if tag:
            return tag

        slug = slugify(name)
        if slug:
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={'name': name})
            if tag.name.casefold() == name.casefold():
                return tag

        tag, _ = Tag.objects.get_or_create(name=name, defaults={'slug': uuid4().hex})
        return tag

    @transaction.atomic
    def save(self, author):
        self.instance.author = author
        question = super().save()
        question.tags.set([self.get_tag(name) for name in self.cleaned_data['tag_names']])
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        labels = {'text': 'Ваш ответ'}
        widgets = {'text': forms.Textarea(attrs={'placeholder': 'Напишите ответ...'})}

    def save(self, author, question):
        self.instance.author = author
        self.instance.question = question
        return super().save()


class VoteForm(forms.Form):
    id = forms.IntegerField(min_value=1, max_value=2**63 - 1)
    value = forms.TypedChoiceField(choices=((1, 'Лайк'), (-1, 'Дизлайк')), coerce=int)

    def __init__(self, data, *, user, model):
        super().__init__(data)
        self.user = user
        self.model = model
        self.error_status = 400

    def clean(self):
        data = super().clean()
        if self.errors:
            return data

        self.item = self.model.objects.select_for_update().filter(pk=data['id']).first()
        if self.item is None:
            self.error_status = 404
            raise forms.ValidationError('Запись не найдена.')

        if self.item.likes.filter(user=self.user, value=data['value']).exists():
            self.error_status = 409
            raise forms.ValidationError('Вы уже поставили эту оценку.')

        return data

    def save(self):
        from django.db.models import Sum

        value = self.cleaned_data['value']
        self.item.likes.update_or_create(user=self.user, defaults={'value': value})
        rating = self.item.likes.aggregate(total=Sum('value'))['total']
        return {'rating': rating, 'value': value}


class CorrectAnswerForm(forms.Form):
    question = forms.IntegerField(min_value=1, max_value=2**63 - 1)
    answer = forms.IntegerField(min_value=1, max_value=2**63 - 1)

    def __init__(self, data, *, user):
        super().__init__(data)
        self.user = user
        self.error_status = 400

    def clean(self):
        data = super().clean()
        if self.errors:
            return data

        question = Question.objects.select_for_update().filter(pk=data['question']).first()
        if question is None:
            self.error_status = 404
            raise forms.ValidationError('Вопрос не найден.')

        if question.author_id != self.user.pk:
            self.error_status = 403
            raise forms.ValidationError('Выбирать правильный ответ может только автор вопроса.')

        self.answer = question.answers.filter(pk=data['answer']).first()
        if self.answer is None:
            self.error_status = 404
            raise forms.ValidationError('У этого вопроса нет такого ответа.')

        if self.answer.correct:
            self.error_status = 409
            raise forms.ValidationError('Этот ответ уже отмечен как правильный.')

        return data

    def save(self):
        Answer.objects.filter(question_id=self.answer.question_id, correct=True).update(correct=False)
        self.answer.correct = True
        self.answer.save(update_fields=['correct'])
        return {'answer': self.answer.pk, 'correct': True}
