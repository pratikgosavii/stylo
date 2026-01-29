def sidebar_menus(request):
    menus = []
    if request.user.is_authenticated:
        allowed_urls = set()
        for role in request.user.roles.all():
            allowed_urls.update(role.allowed_url_names)
        menus = allowed_urls  # or fetch full menu info if stored in DB
    return {'allowed_urls': menus}
