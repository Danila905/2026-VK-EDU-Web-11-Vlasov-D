from django.shortcuts import get_object_or_404, render

from .models import Answer, Question, Tag
from .pagination import paginate


def show_page(request, items, template, section, per_page=10, **context):
    page = paginate(items, request, per_page)
    context['page'] = page
    context['page_numbers'] = page.paginator.get_elided_page_range(page.number)
    context['section'] = section
    return render(request, template, context)


def index(request):
    search = request.GET.get('q', '')
    questions = Question.objects.newest(search=search, user=request.user)
    return show_page(
        request, questions, 'questions/index.html', 'index',
    )


def hot(request):
    questions = Question.objects.best(user=request.user)
    return show_page(
        request, questions, 'questions/hot.html', 'hot',
    )


def tag(request, tag):
    item = get_object_or_404(Tag, slug=tag)
    questions = Question.objects.by_tag(item, user=request.user)
    return show_page(
        request, questions, 'questions/tag.html', 'tag', tag_name=item.name,
    )


def question(request, question_id):
    questions = Question.objects.for_display(request.user)
    item = get_object_or_404(questions, pk=question_id)
    answers = Answer.objects.for_question(item, request.user)
    return show_page(
        request, answers, 'questions/question.html', 'question', per_page=2, question=item,
    )


def ask(request):
    return render(
        request,
        'questions/ask.html',
        {'section': 'ask'},
    )
