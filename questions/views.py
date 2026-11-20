from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db.models import Q
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from .forms import AnswerForm, QuestionForm

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


ANSWERS_PER_PAGE = 2


@require_http_methods(['GET', 'POST'])
def question(request, question_id):
    item = get_object_or_404(Question.objects.for_display(request.user), pk=question_id)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(request.user, item)
            earlier = item.answers.filter(
                Q(correct=True) | Q(created__lt=answer.created)
                | Q(created=answer.created, pk__lt=answer.pk)
            ).count()
            page_number = earlier // ANSWERS_PER_PAGE + 1
            return redirect(f'{item.get_absolute_url()}?page={page_number}#answer-{answer.pk}')
    else:
        form = AnswerForm()

    answers = Answer.objects.for_question(item, request.user)
    return show_page(
        request, answers, 'questions/question.html', 'question',
        per_page=ANSWERS_PER_PAGE, question=item, form=form,
    )


@login_required
@require_http_methods(['GET', 'POST'])
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            return redirect(form.save(request.user))
    else:
        form = QuestionForm()

    return render(request, 'questions/ask.html', {'section': 'ask', 'form': form})
