from database.FileDatabase import DatabaseInterop
from uuid import uuid4
from dotenv import load_dotenv
from os import getenv as env
from typing import Optional, Any, TypeVar
from datetime import timedelta

import scrypt
import firebase_admin
from firebase_admin import auth
from firebase_admin._auth_utils import UserNotFoundError

from database.user import PublicUser
from database.group import Group

load_dotenv()

config = {
  "apiKey": env("API_KEY"),
  "authDomain": env("AUTH_DOMAIN"),
  "projectId": env("PROJECT_ID"),
  "storageBucket": env("STORAGE_BUCKET"),
  "messagingSenderId": env("MESSAGING_SENDER_ID"),
  "appId": env("APP_ID"),
  "measurementId": env("MEASUREMENT_ID"),
}

Cookie = TypeVar("Cookie")
ID = TypeVar("ID")
Token = TypeVar("Token")
class FirebaseDatabase(DatabaseInterop):
    firebase: firebase_admin.App
    def __init__(self):
        self.firebase = firebase_admin.initialize_app(config)
        super().__init__()


    def user_public_get(self, email: str) -> PublicUser: pass

    # Done
    def user_exists(self, email: str) -> bool:
        try:
            _ = auth.get_user_by_email(email)
            return True
        except UserNotFoundError:
            return False

    # Done
    def user_authenticate(self, email: str, password: str) -> bool:
        for user in auth.list_users().users:
            return scrypt.hash(password, user.password_salt) == user.password_hash
        return False

    # Done
    def user_create(
            self,
            email: str,
            display_name: str,
            password: str,
            profile_picture: Optional[str] = None
    ) -> Token:
        user = auth.create_user(
            uid=str(uuid4()),
            display_name=display_name,
            email=email,
            email_verified=False,
            photo_url=profile_picture,
            password=password,
        )
        return auth.create_session_cookie(
            user.uid,
            timedelta(days=30)
        )

    def user_login(self, email: str, password: str) -> Optional[Token]: pass
    def user_change_password(self, email: str, new_password: str) -> bool: pass
    def user_logout(self, cookie: Cookie): pass
    def user_get(self, cookie: Cookie): pass
    def user_change_username(self, cookie: Cookie, new_user_name: str) -> bool: pass
    def user_change_email(self, cookie: Cookie, new_email: str) -> bool: pass
    def user_change_profile_picture(self, cookie: Cookie, new_profile_picture: str) -> bool: pass
    def user_groups_get(self, search_query: str) -> list[Group]: pass
    def user_join_group(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_leave_group(self, cookie: Cookie, group_id: str, wipe_messages: bool) -> bool: pass
    def user_pin_group(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_unpin_group(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_admin_promote_group(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_wipe_all_messages(self, cookie: Cookie) -> bool: pass
    def user_wipe_all_group_messages(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_wipe_all_left_group_messages(self, cookie: Cookie) -> bool: pass
    def message_send(
            self,
            cookie: Cookie,
            group_id: str,
            content: str,
            is_reply: bool,
            reply_to_user: Optional[str],
            reply_to_content: Optional[str]
    ) -> bool: pass
    def message_get(self, cookie: Cookie, group_id: str, pagination: int = 0, amount: int = 1) -> list[Any]: pass
    def message_edit(self, cookie: Cookie, group_id: str, message_id: str, new_content: str) -> bool: pass
    def message_delete(self, cookie: Cookie, group_id: str, message_id: str) -> bool: pass
    def group_private_create(self, name: str, creator_id: str) -> Optional[Group]: pass
    def group_contact_create(self, user1_id: str, user1_name: str, user2_id: str, user2_name: str) -> Optional[Group]: pass
    def group_delete(self, cookie: Cookie, group_id: str) -> bool: pass
    def group_get(self, cookie: Cookie, group_id: str) -> Optional[Group]: pass
    def group_rename(self, cookie: Cookie, group_id: str, new_group_name: str) -> bool: pass
    def request_send(self, cookie: Cookie, to_id: str) -> bool: pass
    def request_exists(self, cookie: Cookie, to_id: str) -> bool: pass
    def request_cancel(self, cookie: Cookie, to_id: str) -> bool: pass
