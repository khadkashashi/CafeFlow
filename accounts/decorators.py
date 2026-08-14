from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator

#@wraps(view_func) preserves the original view's name/docstring for Django's introspection and debugging — skipping this is a common subtle bug source (things like the admin or error pages showing "wrapper" instead of the real view name).
#PermissionDenied triggers Django's built-in 403 error page automatically — no need to build our own.
#Superusers always pass