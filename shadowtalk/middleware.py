import json
import pickle

from django.conf.global_settings import SESSION_COOKIE_NAME
from django.utils.deprecation import MiddlewareMixin
from firebase_admin import auth
from types import SimpleNamespace as Blank

from database.cookie import Cookie


class FirebaseAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        session_cookie = request.COOKIES.get(SESSION_COOKIE_NAME)

        # Hack around
        if str(session_cookie) == "None":
            request.user = Blank()
            request.user.is_authenticated = False
            return None

        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
            request.user = Cookie(
                decoded_claims['uid'],
                decoded_claims['email'],
                decoded_claims['name']
            )
            request.user.is_authenticated = True
        except auth.InvalidIdTokenError:
            request.user = Blank()
            request.user.is_authenticated = False
        return None

class FileAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        session_cookie = request.COOKIES.get(SESSION_COOKIE_NAME)

        # Hack around
        if str(session_cookie) == "None":
            request.user = Blank()
            request.user.is_authenticated = False
            return None

        try:
            request.user = Cookie.from_dict(json.loads(session_cookie))
            request.user.is_authenticated = True
        except auth.InvalidIdTokenError:
            request.user = Blank()
            request.user.is_authenticated = False
        return None
