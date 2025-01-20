from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve

class DisableCSRFOnTokenView(MiddlewareMixin):
    def process_request(self, request):
        if resolve(request.path_info).url_name in ['token_obtain_pair', 'token_refresh']:
            setattr(request, '_dont_enforce_csrf_checks', True)