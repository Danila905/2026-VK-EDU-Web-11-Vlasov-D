from django import forms
from django.contrib import admin

from .models import Answer, AnswerLike, Question, QuestionLike, Tag

# Register your models here.


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('author', 'text', 'correct', 'created')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['widget'] = forms.NumberInput(attrs={'min': 1})
            kwargs['label'] = 'ID автора'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created')
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('created',)
    list_select_related = ('author',)
    raw_id_fields = ('author', 'tags')
    inlines = (AnswerInline,)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'correct', 'created')
    search_fields = ('text', 'question__title', 'author__username')
    list_filter = ('correct', 'created')
    list_select_related = ('question', 'author')
    raw_id_fields = ('question', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created')
    search_fields = ('name', 'slug')
    list_filter = ('created',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'value')
    search_fields = ('user__username', 'question__title')
    list_filter = ('value',)
    list_select_related = ('user', 'question')
    raw_id_fields = ('user', 'question')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'answer', 'value')
    search_fields = ('user__username', 'answer__text')
    list_filter = ('value',)
    list_select_related = ('user', 'answer')
    raw_id_fields = ('user', 'answer')
