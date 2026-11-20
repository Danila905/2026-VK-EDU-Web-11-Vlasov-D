from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, ProfileForm, SignupForm


class Login(LoginView):
    template_name = 'core/login.html'
    authentication_form = LoginForm
    extra_context = {'section': 'login'}

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session.set_expiry(None if form.cleaned_data['remember'] else 0)
        return response


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid() and form.save():
            return redirect('questions:index')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form, 'section': 'signup'})


@login_required
@require_http_methods(['GET', 'POST'])
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('core:profile')
    else:
        form = ProfileForm(instance=request.user)

    questions = request.user.questions.aggregate(total=Sum('likes__value', default=0))
    answers = request.user.answers.aggregate(total=Sum('likes__value', default=0))
    return render(request, 'core/profile.html', {
        'form': form,
        'section': 'profile',
        'rating': questions['total'] + answers['total'],
    })
