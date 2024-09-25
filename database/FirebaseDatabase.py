import google.cloud.firestore
from firebase_admin.auth import update_user

from database.FileDatabase import DatabaseInterop
from uuid import uuid4
from dotenv import load_dotenv
from os import getenv as env
from typing import Optional, Any, TypeVar
from datetime import timedelta

import scrypt
import firebase_admin
from firebase_admin import auth, db
from firebase_admin._auth_utils import UserNotFoundError
from firebase_admin._user_mgt import ExportedUserRecord
from firebase_admin.firestore import client
from google.cloud.firestore import ArrayUnion, ArrayRemove, CollectionReference

from database.user import PublicUser, PrivateUser
from database.group import Group

load_dotenv()

USER_COLLECTION = "user_data"
GROUP_COLLECTION = "group_data"

USER_GROUP_IDS = "group_ids"
USER_INTERACTED_GROUP_IDS = "interacted_group_ids"
USER_PINNED_GROUP_IDS = "pinned_group_ids"
USER_REQUESTS = "requests"

GROUP_ID = "id"
GROUP_NAME = "name"
GROUP_IS_PUBLIC = "is_public"
GROUP_OWNER_ID = "owner_id"
GROUP_ADMIN_IDS = "admin_ids"
GROUP_MEMBER_IDS = "member_ids"
GROUP_LAST_MESSAGE_ID = "last_message_id"
GROUP_LAST_MESSAGE_CONTENT = "last_message_content"
GROUP_LAST_MESSAGE_AUTHOR_NAME = "last_message_author_name"

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
    firestore: google.cloud.firestore.Client
    user_collection: CollectionReference
    group_collection: CollectionReference

    def __init__(self):
        self.firebase = firebase_admin.initialize_app(config)
        self.firestore = client()
        self.user_collection = self.firestore.collection(USER_COLLECTION)
        self.group_collection = self.firestore.collection(GROUP_COLLECTION)
        super().__init__()

    # Done
    def user_public_get(self, email: str) -> Optional[PublicUser]:
        try:
            user_data = auth.get_user_by_email(email)
        except:
            return None
        return PublicUser(user_data.display_name, user_data.photo_url)

    # Done
    def user_exists(self, email: str) -> bool:
        try:
            _ = auth.get_user_by_email(email)
            return True
        except UserNotFoundError:
            return False

    # Done
    def user_authenticate(self, email: str, password: str) -> tuple[Optional[ExportedUserRecord], bool]:
        try:
            users = auth.list_users().users
        except:
            return None, False
        for user in users:
            if not user.email == email:
                continue
            try:
                if not scrypt.hash(password, user.password_salt) == user.password_hash:
                    return None, False
            except:
                return None, False
        return None, False

    # Done
    def user_create(
            self,
            email: str,
            display_name: str,
            password: str,
            profile_picture: Optional[str] = None
    ) -> Token:
        try:
            user = auth.create_user(
                uid=str(uuid4()),
                display_name=display_name,
                email=email,
                email_verified=False,
                photo_url=profile_picture,
                password=password,
            )
            document_reference = self.user_collection.document(user.uid)
            document_reference.set({
                USER_GROUP_IDS: [],
                USER_INTERACTED_GROUP_IDS: [],
                USER_PINNED_GROUP_IDS: [],
                USER_REQUESTS: []
            })
            return auth.create_session_cookie(
                user.uid,
                timedelta(days=30)
            )
        except:
            return None

    # Done
    def user_login(self, email: str, password: str) -> Optional[Token]:
        user, correct_login = self.user_authenticate(email, password)
        if not correct_login:
            return None
        try:
            return auth.create_session_cookie(user.uid, timedelta(days=30))
        except:
            return None

    def user_logout(self, cookie: Cookie): pass
    def user_get(self, cookie: Cookie) -> Optional[PrivateUser]:
        try:
            user_record = auth.get_user_by_email(cookie.email)
        except:
            return None
        return PrivateUser(
            user_record.display_name,
            user_record.email,
            user_record.email_verified,
            user_record.photo_url
        )

    # Done
    def user_change_password(self, email: str, new_password: str) -> bool:
        try:
            user = auth.get_user_by_email(email)
            auth.update_user(user.uid, password=new_password)
            return True
        except:
            return False

    # Done
    def user_change_username(self, cookie: Cookie, new_user_name: str) -> bool:
        try:
            user = auth.get_user_by_email(cookie.email)
            auth.update_user(user.uid, display_name=new_user_name)
            return True
        except:
            return False

    # Done
    def user_change_email(self, cookie: Cookie, new_email: str) -> bool:
        try:
            user = auth.get_user_by_email(cookie.email)
            auth.update_user(user.uid, email=new_email, email_verified=False)
            return True
        except:
            return False

    # Done
    def user_change_profile_picture(self, cookie: Cookie, new_profile_picture: str) -> bool:
        try:
            user = auth.get_user_by_email(cookie.email)
            auth.update_user(user.uid, photo_url=new_profile_picture)
            return True
        except:
            return False

    # Done
    def user_groups_get(self, cookie: Cookie, search_query: str) -> list[Group]:
        user_data = self.user_collection.document(cookie.uid).get()
        group_ids = user_data.get(USER_GROUP_IDS)
        groups = self.group_collection \
            .where(GROUP_ID, 'in', group_ids) \
            .stream()
        output_groups = []
        for group in groups:
            output_groups.append(Group.from_attr(
                group.get(GROUP_ID),
                group.get(GROUP_NAME),
                group.get(GROUP_IS_PUBLIC),
                group.get(GROUP_OWNER_ID),
                group.get(GROUP_ADMIN_IDS),
                group.get(GROUP_MEMBER_IDS),
                group.get(GROUP_LAST_MESSAGE_ID),
                group.get(GROUP_LAST_MESSAGE_CONTENT),
                group.get(GROUP_LAST_MESSAGE_AUTHOR_NAME),
            ))
        return output_groups

    # Done
    def user_join_group(self, cookie: Cookie, group_id: str) -> bool:
        try:
            self.user_collection.document(cookie.uid).update({
                USER_GROUP_IDS: ArrayUnion([group_id])
            })
            self.group_collection.document(group_id).update({
                GROUP_MEMBER_IDS: ArrayUnion([cookie.uid])
            })
            return True
        except:
            return False

    # Done
    def user_leave_group(self, cookie: Cookie, group_id: str, wipe_messages: bool) -> bool:
        try:
            self.user_collection.document(cookie.uid).update({
                USER_GROUP_IDS: ArrayRemove([group_id])
            })
            self.group_collection.document(group_id).update({
                GROUP_MEMBER_IDS: ArrayRemove([cookie.uid])
            })
            return True
        except:
            return False

    # Done
    def user_pin_group(self, cookie: Cookie, group_id: str) -> bool:
        try:
            self.user_collection.document(cookie.uid).update({
                USER_PINNED_GROUP_IDS: ArrayUnion([group_id])
            })
            return True
        except:
            return False

    # Done
    def user_unpin_group(self, cookie: Cookie, group_id: str) -> bool:
        try:
            self.user_collection.document(cookie.uid).update({
                USER_PINNED_GROUP_IDS: ArrayRemove([group_id])
            })
            return True
        except:
            return False

    # Done
    def user_admin_promote_group(self, cookie: Cookie, group_id: str) -> bool:
        try:
            self.group_collection.document(cookie.uid).update({
                GROUP_ADMIN_IDS: ArrayUnion([cookie.uid]),
                GROUP_MEMBER_IDS: ArrayRemove([cookie.uid])
            })
            return True
        except:
            return False


    # Done
    def user_admin_demote_group(self, cookie: Cookie, group_id: str) -> bool:
        try:
            self.group_collection.document(cookie.uid).update({
                GROUP_ADMIN_IDS: ArrayRemove([cookie.uid]),
                GROUP_MEMBER_IDS: ArrayUnion([cookie.uid])
            })
            return True
        except:
            return False

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

    def __group_create(self, group: Group) -> Optional[Group]:
        try:
            self.group_collection.document(group.id).set({
                GROUP_ID: group.id,
                GROUP_NAME: group.name,
                GROUP_OWNER_ID: group.owner_id,
                GROUP_MEMBER_IDS: group.member_ids,
                GROUP_ADMIN_IDS: group.admin_ids,
                GROUP_LAST_MESSAGE_ID: group.last_message_id,
                GROUP_LAST_MESSAGE_AUTHOR_NAME: group.last_message_author_name,
                GROUP_LAST_MESSAGE_CONTENT: group.last_message_content,
            })
            return group
        except:
            return None

    def __user_has_group_access(self, uid: str, group_id: str) -> str:
        group_reference = self.group_collection.document(group_id)
        members_list = group_reference.get(GROUP_MEMBER_IDS)
        if uid in members_list:
            return "member"
        admin_list = group_reference.get(GROUP_ADMIN_IDS)
        if uid in admin_list:
            return "admin"
        return "none"

    # Done
    def group_private_create(self, name: str, creator_id: str) -> Optional[Group]:
        group = Group.private(name, [creator_id])
        return self.__group_create(group)

    # Done
    def group_contact_create(self, user1_id: str, user1_name: str, user2_id: str, user2_name: str) -> Optional[Group]:
        group = Group.private(f"{user1_name} & {user2_name}", [user1_id, user2_id])
        return self.__group_create(group)

    # Done
    def group_delete(self, cookie: Cookie, group_id: str) -> bool:
        if self.__user_has_group_access(cookie.uid, group_id) != "admin":
            return False
        try:
            self.group_collection.document(group_id).delete()
            return True
        except:
            return False

    # Done
    def group_get(self, cookie: Cookie, group_id: str) -> Optional[Group]:
        if self.__user_has_group_access(cookie.uid, group_id) == "none":
            return None
        group_record = self.group_collection.document(group_id).get()
        return Group.from_attr(
            group_id,
            group_record.get(GROUP_NAME),
            group_record.get(GROUP_IS_PUBLIC),
            group_record.get(GROUP_OWNER_ID),
            group_record.get(GROUP_ADMIN_IDS),
            group_record.get(GROUP_MEMBER_IDS),
            group_record.get(GROUP_LAST_MESSAGE_ID),
            group_record.get(GROUP_LAST_MESSAGE_CONTENT),
            group_record.get(GROUP_LAST_MESSAGE_AUTHOR_NAME),
        )

    # Done
    def group_rename(self, cookie: Cookie, group_id: str, new_group_name: str) -> bool:
        if self.__user_has_group_access(cookie.uid, group_id) != "admin":
            return False
        try:
            self.group_collection.document(group_id).update({
                GROUP_NAME: new_group_name,
            })
            return True
        except:
            return False

    # Done
    def request_send(self, cookie: Cookie, to_id: str) -> bool:
        try:
            self.user_collection.document(to_id).update({
                USER_REQUESTS: ArrayUnion([cookie.uid])
            })
            return True
        except:
            return False

    # Done
    def request_exists(self, cookie: Cookie, to_id: str) -> bool:
        try:
            self.user_collection.document(to_id).update({
                USER_REQUESTS: ArrayUnion([cookie.uid])
            })
            return True
        except:
            return False

    # Done
    def request_cancel(self, cookie: Cookie, to_id: str) -> bool:
        try:
            self.user_collection.document(to_id).update({
                USER_REQUESTS: ArrayRemove([cookie.uid])
            })
            return True
        except:
            return False
