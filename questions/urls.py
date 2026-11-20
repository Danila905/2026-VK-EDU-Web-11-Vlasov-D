from django.urls import path
from . import api, views
from .forms import CorrectAnswerForm, VoteForm
from .models import Answer, Question

app_name = 'questions'
urlpatterns = [
    path('api/vote/question/', api.action, {'form_class': VoteForm, 'model': Question}, name='vote_question'),
    path('api/vote/answer/', api.action, {'form_class': VoteForm, 'model': Answer}, name='vote_answer'),
    path('api/correct/', api.action, {'form_class': CorrectAnswerForm}, name='correct_answer'),
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<slug:tag>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
]
