
# This disables CSRF protection since it was causing problems.
# For security, we should look into re-enabling it.
class DisableCSRF(object):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)

