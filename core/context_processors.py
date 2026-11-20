from questions.models import Tag

from .models import Profile


def sidebars(request):
    return {
        'popular_tags': Tag.objects.popular(),
        'best_members': Profile.objects.best_members(),
    }
