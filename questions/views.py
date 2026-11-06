from django.http import Http404
from django.shortcuts import render
from .data import QUESTIONS, get_answers
from .pagination import paginate


def show_list(request, items, template, section, tag_name=''):
    page = paginate(items, request)
    numbers = page.paginator.get_elided_page_range(page.number)
    return render(request, template, {
        'page': page, 'page_numbers': numbers,
        'section': section, 'tag_name': tag_name,
    })


def index(request):
    search = request.GET.get('q', '').strip().lower()
    items = [q for q in QUESTIONS if search in q['title'].lower()]
    return show_list(request, items, 'questions/index.html', 'index')


def hot(request):
    items = sorted(QUESTIONS, key=lambda q: q['votes'], reverse=True)
    return show_list(request, items, 'questions/hot.html', 'hot')


def tag(request, tag):
    items = [q for q in QUESTIONS if tag.lower() in [t['slug'] for t in q['tags']]]
    return show_list(request, items, 'questions/tag.html', 'tag', tag)


def question(request, question_id):
    item = next((q for q in QUESTIONS if q['id'] == question_id), None)
    if item is None:
        raise Http404('Вопрос не найден')
    page = paginate(get_answers(item), request, per_page=2)
    numbers = page.paginator.get_elided_page_range(page.number)
    return render(request, 'questions/question.html', {
        'question': item, 'page': page,
        'page_numbers': numbers, 'section': 'question',
    })


def ask(request):
    return render(request, 'questions/ask.html', {'section': 'ask'})
