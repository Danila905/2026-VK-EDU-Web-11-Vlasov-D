from django.db import transaction
from django.http import JsonResponse
from django.views.csrf import csrf_failure as django_csrf_failure


def csrf_failure(request, reason=''):
    if request.path_info.startswith('/api/'):
        return JsonResponse({'error': 'Проверка CSRF не прошла. Обновите страницу.'}, status=403)
    return django_csrf_failure(request, reason=reason)


@transaction.atomic
def action(request, form_class, **options):
    if request.method != 'POST':
        response = JsonResponse({'error': 'Требуется POST.'}, status=405)
        response['Allow'] = 'POST'
        return response

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Войдите в аккаунт.'}, status=401)

    form = form_class(request.POST, user=request.user, **options)
    if form.is_valid():
        return JsonResponse(form.save())

    errors = [str(error) for messages in form.errors.values() for error in messages]
    return JsonResponse({'error': ' '.join(errors)}, status=form.error_status)
