from django.conf.global_settings import SESSION_COOKIE_NAME
from django.utils.deprecation import MiddlewareMixin
from firebase_admin import auth

from database.cookie import Cookie


class FirebaseAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        session_cookie = request.COOKIES.get(SESSION_COOKIE_NAME)
        if not session_cookie:
            request.user = None
            return None

        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
            request.user = Cookie(
                decoded_claims['uid'],
                decoded_claims['email'],
                decoded_claims['name']
            )
        except auth.InvalidIdTokenError:
            request.user = None
        return None