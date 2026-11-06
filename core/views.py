from django.shortcuts import render


def login(request):
    return render(request, 'core/login.html', {'section': 'login'})


def signup(request):
    return render(request, 'core/signup.html', {'section': 'signup'})


def profile(request):
    return render(request, 'core/profile.html', {'section': 'profile'})
