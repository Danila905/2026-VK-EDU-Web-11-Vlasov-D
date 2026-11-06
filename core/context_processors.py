def sidebars(request):
    return {
        'popular_tags': [('Python', 'python', 128), ('Django', 'django', 96),
                         ('HTML', 'html', 84), ('CSS', 'css', 76),
                         ('Bootstrap', 'bootstrap', 54)],
        'best_members': [('Alex Developer', 987), ('Maria Code', 742), ('Max Coder', 615)],
    }
