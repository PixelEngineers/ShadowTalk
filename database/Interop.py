from typing import Optional, Any, TypeVar

from database.group import Group
from database.user import PublicUser, PrivateUser
from database.cookie import Cookie

ID = TypeVar("ID")
Token = TypeVar("Token")
class DatabaseInterop:
    def __init__(self): pass
    def deinit(self): pass

    """User Interaction"""
    """Functions which don't require authentication"""
    """dont show group information here, ig"""
    def user_public_get(self, email: str) -> Optional[PublicUser]: pass
    def user_exists(self, email: str) -> bool: pass
    def user_authenticate(self, email: str, password: str) -> bool: pass
    def user_create(
            self,
            email: str,
            display_name: str,
            password: str,
            profile_picture: Optional[str] = None
    ) -> Optional[Token]: pass
    def user_login(self, email: str, password: str) -> Optional[Token]: pass
    def user_change_password(self, email: str, new_password: str) -> bool: pass

    """Functions which do require authentication (use cookie)"""
    def user_logout(self, cookie: Cookie): pass
    def user_get(self, cookie: Cookie) -> Optional[PrivateUser]: pass
    """User Edit actions"""
    def user_change_username(self, cookie: Cookie, new_user_name: str) -> bool: pass
    def user_change_email(self, cookie: Cookie, new_email: str) -> bool: pass
    def user_change_profile_picture(self, cookie: Cookie, new_profile_picture: str) -> bool: pass

    """User group interactions"""
    def user_groups_get(self, cookie: Cookie, search_query: str) -> list[Group]: pass
    def user_interacted_groups_get(self, cookie: Cookie, search_query: str) -> list[Group]: pass
    def user_join_group(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_leave_group(self, cookie: Cookie, group_id: str, wipe_messages: bool) -> bool: pass
    def user_pin_group(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_unpin_group(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_admin_promote_group(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_admin_demote_group(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_wipe_all_messages(self, cookie: Cookie) -> bool: pass
    def user_wipe_all_group_messages(self, cookie: Cookie, group_id: str) -> bool: pass
    def user_wipe_all_left_group_messages(self, cookie: Cookie) -> bool: pass

    """User message interaction"""
    def message_send(
            self,
            cookie: Cookie,
            group_id: str,
            content: str,
            is_reply: bool,
            reply_to_user: Optional[str],
            reply_to_content: Optional[str]
    ) -> bool: pass
    def message_get(
            self,
            cookie: Cookie,
            group_id: str,
            pagination_last_message_key: Optional[str] = None,
            amount: int = 1
    ) -> list[Any]: pass
    def message_edit(self, cookie: Cookie, group_id: str, message_id: str, new_content: str) -> bool: pass
    def message_delete(self, cookie: Cookie, group_id: str, message_id: str) -> bool: pass

    """Group Interaction"""
    def group_private_create(self, name: str, creator_id: str) -> Optional[Group]: pass
    def group_contact_create(self, user1_id: str, user1_name: str, user2_id: str, user2_name: str) -> Optional[Group]: pass
    # def group_public_create(self, name: str, creator_id: str) -> str: pass
    def group_delete(self, cookie: Cookie, group_id: str) -> bool: pass
    def group_get(self, cookie: Cookie, group_id: str) -> Optional[Group]: pass
    def group_rename(self, cookie: Cookie, group_id: str, new_group_name: str) -> bool: pass

    """User request Interaction"""
    def request_send(self, cookie: Cookie, to_id: str) -> bool: pass
    def request_exists(self, cookie: Cookie, to_id: str) -> bool: pass
    def request_cancel(self, cookie: Cookie, to_id: str) -> bool: pass
