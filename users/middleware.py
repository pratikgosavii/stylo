from django.urls import resolve
from django.http import HttpResponseForbidden

class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if not request.user.is_authenticated or request.user.is_superuser:
            return self.get_response(request)

        try:
            url_name = resolve(request.path_info).url_name
        except:
            return self.get_response(request)

        user_roles = request.user.roles.all()

        allowed_urls = set()
        for role in user_roles:
            allowed_urls.update(role.allowed_url_names)

        if url_name not in allowed_urls:
            return HttpResponseForbidden("You are not allowed to access this page.")

        return self.get_response(request)
