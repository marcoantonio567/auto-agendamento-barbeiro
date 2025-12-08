import base64
from django.conf import settings
from django.http import HttpResponse


def basic_auth_required(view):
    def _wrapped(request, *args, **kwargs):
        header = request.META.get('HTTP_AUTHORIZATION')
        if header and header.startswith('Basic '):
            try:
                user_pass = base64.b64decode(header.split(' ')[1]).decode('utf-8')
                user, pwd = user_pass.split(':', 1)
            except Exception:
                return HttpResponse(status=401, headers={'WWW-Authenticate': 'Basic realm="Admin"'})
            if user == getattr(settings, 'ADMIN_BASIC_USER', '') and pwd == getattr(settings, 'ADMIN_BASIC_PASSWORD', ''):
                return view(request, *args, **kwargs)
        return HttpResponse(status=401, headers={'WWW-Authenticate': 'Basic realm="Admin"'})
    return _wrapped
