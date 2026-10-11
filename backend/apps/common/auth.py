from rest_framework.authentication import SessionAuthentication


class CsrfEnforcingSessionAuthentication(SessionAuthentication):
    """Session authentication that enforces CSRF for every unsafe request.

    DRF's stock SessionAuthentication skips the CSRF check for anonymous
    requests, which would leave login/register endpoints open to login-CSRF.
    Enforcing it unconditionally closes that gap.
    """

    def authenticate(self, request):
        self.enforce_csrf(request)
        return super().authenticate(request)
