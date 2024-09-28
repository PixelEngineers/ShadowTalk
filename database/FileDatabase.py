import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import getenv
from os.path import exists
from smtplib import SMTP_SSL
from ssl import create_default_context
from typing import Optional, TypeVar, Callable

from jwt import encode

from .cookie import Cookie
from scrypt import hash
from bcrypt import gensalt
import pickle
import re

from database.Interop import DatabaseInterop
from database.user import User, PrivateUser, PublicUser
from database.group import Group
from database.message import Message

T = TypeVar("T")
def find_index(to_iter: list[T], expression: Callable[[T], bool]) -> Optional[int]:
    for i, item in enumerate(to_iter):
        if expression(item):
            return i

def create_if_not_exist(name: str, default_data, mode='w'):
    if exists(name):
        return
    f = open(name, mode)
    f.write(default_data)
    f.close()

ID = TypeVar("ID")
Token = TypeVar("Token")
class FileDatabase(DatabaseInterop):
    users: dict[str, User]
    auth: dict[str, tuple[str, str]]
    groups: dict[str, Group]
    messages: dict[str, dict[str, Message]]

    user_db_location: str
    group_db_location: str
    messages_db_location: str
    auth_db_location: str

    def __init__(self, user_db_location: str, group_db_location: str, messages_db_location: str, auth_db_location: str):
        create_if_not_exist(user_db_location, pickle.dumps({}), 'wb')
        create_if_not_exist(group_db_location, pickle.dumps({}), 'wb')
        create_if_not_exist(messages_db_location, pickle.dumps({}), 'wb')
        create_if_not_exist(auth_db_location, pickle.dumps({}), 'wb')

        with open(user_db_location, 'rb') as f:
            self.users = pickle.load(f)
        with open(group_db_location, 'rb') as f:
            self.groups = pickle.load(f)
        with open(messages_db_location, 'rb') as f:
            self.messages = pickle.load(f)
        with open(auth_db_location, 'rb') as f:
            self.auth = pickle.load(f)

        self.user_db_location = user_db_location
        self.group_db_location = group_db_location
        self.messages_db_location = messages_db_location
        self.auth_db_location = auth_db_location
        super().__init__()

    def deinit(self):
        with open(self.user_db_location, 'wb') as f:
            pickle.dump(self.users, f)
        with open(self.group_db_location, 'wb') as f:
            pickle.dump(self.groups, f)
        with open(self.messages_db_location, 'wb') as f:
            pickle.dump(self.messages, f)
        with open(self.auth_db_location, 'wb') as f:
            pickle.dump(self.auth, f)

    def user_public_get(self, user_id: str) -> Optional[PublicUser]:
        return PublicUser.from_user(self.users[user_id])

    def user_exists(self, user_id: str) -> bool:
        return self.users.get(user_id) is not None

    def user_exists_email(self, email: str) -> bool:
        for user in self.users.values():
            if user.email == email:
                return True
        return False

    def user_authenticate(self, email: str, password: str) -> bool:
        actual_hash, salt = self.auth.get(email)
        new_hash = hash(password, salt)
        if new_hash == actual_hash:
            return True
        return False

    def user_create(
            self,
            email: str,
            display_name: str,
            password: str,
            profile_picture: Optional[str] = None
    ) -> Optional[Token]:
        user = User(email, display_name, profile_picture)
        self.users[user.id] = user
        salt = gensalt()
        self.auth[email] = (hash(password, salt), salt.decode())
        return json.dumps(Cookie(user.id, email, display_name).to_dict())

    def encode_cookie(self, cookie: Cookie) -> str:
        return json.dumps(cookie.to_dict())

    def user_verify(self, cookie: Cookie) -> bool:
        user_record = self.users[cookie.id]
        if user_record.is_verified_email:
            return True

        message = MIMEMultipart("alternative")
        message["Subject"] = "ShadowTalk - User Email Verification Code"
        message["From"] = getenv("EMAIL")
        message["To"] = user_record.email
        encoded = encode({'_id': user_record.id}, getenv("EMAIL_TOKEN"), algorithm="HS256")
        url = f"{getenv('DOMAIN')}/verify-email?token={encoded}"
        body = f"""
        <h1 style="text-align: center;">ShadowTalk User Email Verification</h1>
        <br>
        <h3 style="text-align: center;">
            <div style="font-size: 2rem;">
                Hello {user_record.name}!<br>
                Please <a href="{url}" target="_blank">Click this link</a> to verify your account<br>
                <div style="color: 'red';">Do not share this with anyone else</div>
            </div>
        </h3>
        """
        html = MIMEText(body, "html")
        message.attach(html)

        context = create_default_context()
        with SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(getenv("EMAIL"), getenv("EMAIL_PASS"))
            server.sendmail(getenv("EMAIL"), user_record.email, message.as_string())

    def user_login(self, email: str, password: str) -> Optional[Token]:
        if not self.user_authenticate(email, password):
            return None
        user = None
        for iter_user in self.users.values():
            if iter_user.email == email:
                user = iter_user
        return json.dumps(Cookie(user.id, email, user.name).to_dict())

    def user_change_password(self, user_id: str, new_password: str) -> bool:
        if self.users.get(user_id) is None:
            return False

        salt = gensalt()
        self.auth[self.users[user_id].email] = (
            hash(new_password, salt),
            salt.decode()
        )
        return True


    @staticmethod
    def is_valid_email(email: str) -> Optional[str]:
        return re.compile(
            """https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"""
        ).match(email)

    @staticmethod
    def is_valid_display_name(display_name: str) -> Optional[str]:
        return None

    @staticmethod
    def is_valid_password(password: str) -> Optional[str]:
        if len(password) < 8:
            return "Password should atleast be 8 characters long"
        return None

    @staticmethod
    def is_valid_photo_url(photo_url: str) -> Optional[str]:
        if re.compile(
            """https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"""
        ).match(photo_url):
            return None
        return "Invalid url"

    def user_get(self, cookie: Cookie) -> Optional[PrivateUser]:
        return PrivateUser.from_user(self.users[cookie.id])

    def user_change_username(self, cookie: Cookie, new_user_name: str) -> bool:
        if self.users.get(cookie.id) is None:
            return False

        self.users[cookie.id].name = new_user_name
        return True

    def user_change_email(self, cookie: Cookie, new_email: str) -> bool:
        if self.users.get(cookie.id) is None:
            return False

        old_email = self.users[cookie.id].email
        self.auth[new_email] = self.auth[old_email]
        del self.auth[old_email]

        self.users[cookie.id].email = new_email
        self.users[cookie.id].is_verified_email = False
        return True

    def user_change_profile_picture(self, cookie: Cookie, new_profile_picture: str) -> bool:
        if self.users.get(cookie.id) is None:
            return False

        self.users[cookie.id].profile_picture = new_profile_picture

    def user_groups_get(self, cookie: Cookie, search_query: str) -> list[Group]:
        return list(map(
            lambda group_id: self.groups[group_id],
            self.users[cookie.id].group_ids
        ))

    def user_interacted_groups_get(self, cookie: Cookie, search_query: str) -> list[Group]:
        return list(map(
            lambda group_id: self.groups[group_id],
            self.users[cookie.id].interacted_group_ids
        ))

    def user_join_group(self, cookie: Cookie, group_id: str) -> bool:
        if self.users.get(cookie.id) is None:
            return False
        if self.groups.get(group_id) is None:
            return False

        self.users[cookie.id].group_ids.append(group_id)
        self.groups[group_id].member_ids.append(cookie.id)
        return True

    def user_leave_group(self, cookie: Cookie, group_id: str, wipe_messages: bool) -> bool:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return False

        self.users[cookie.id].group_ids.remove(group_id)
        try:
            self.groups[group_id].admin_ids.remove(cookie.id)
        except ValueError:
            self.groups[group_id].member_ids.remove(cookie.id)

        return True

    def user_pin_group(self, cookie: Cookie, group_id: str) -> bool:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return False
        self.users[cookie.id].pinned_group_ids.append(group_id)
        return True

    def user_unpin_group(self, cookie: Cookie, group_id: str) -> bool:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return False

        self.users[cookie.id].pinned_group_ids.remove(group_id)
        return True

    def user_admin_promote_group(self, cookie: Cookie, group_id: str) -> bool:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return False

        self.groups[group_id].admin_ids.append(cookie.id)
        self.groups[group_id].member_ids.remove(cookie.id)

    def user_admin_demote_group(self, cookie: Cookie, group_id: str) -> bool:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return False

        self.groups[group_id].admin_ids.remove(cookie.id)
        self.groups[group_id].member_ids.append(cookie.id)

    def user_wipe_all_messages(self, cookie: Cookie) -> bool:
        if self.users.get(cookie.id) is None:
            return False
        for group_id in self.users[cookie.id].group_ids:
            self.user_wipe_all_group_messages(cookie, group_id)
        return True

    def user_wipe_all_group_messages(self, cookie: Cookie, group_id: str) -> bool:
        if self.messages.get(group_id) is None:
            return False

        self.messages[group_id] = dict(
            (_, message)
            for _, message in self.messages[group_id].items()
            if message.author_id != cookie.id
        )
        return True

    def user_wipe_all_left_group_messages(self, cookie: Cookie) -> bool:
        if self.users.get(cookie.id) is None:
            return False
        user = self.users[cookie.id]
        for interacted_group_id in user.interacted_group_ids:
            if interacted_group_id in user.group_ids:
                continue
            self.user_wipe_all_group_messages(cookie, interacted_group_id)
        return True

    def user_has_group_access(self, uid: str, group_id: str) -> str:
        if self.groups.get(group_id) is None:
            return "none"
        if self.users.get(uid):
            return "none"
        group = self.groups[group_id]

        if uid in group.admin_ids:
            return "admin"
        if uid in group.member_ids:
            return "member"
        return "none"

    def message_send(
            self,
            cookie: Cookie,
            group_id: str,
            content: str,
            is_reply: bool,
            reply_to_user: Optional[str],
            reply_to_content: Optional[str]
    ) -> bool:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return False
        message = Message.generate(
            cookie.id,
            cookie.name,
            content,
            self.user_has_group_access(cookie.id, group_id) == "admin",
            is_reply,
            reply_to_user,
            reply_to_content
        )
        self.messages[group_id][message.id] = message
        self.groups[group_id].last_message_id = message.id
        self.groups[group_id].last_message_content = message.content
        self.groups[group_id].last_message_author_name = cookie.name
        return True

    def message_get(
            self,
            cookie: Cookie,
            group_id: str,
            pagination_last_message_key: Optional[str] = None,
            amount: int = 1
    ) -> list[Message]:
        if self.user_has_group_access(cookie.id, group_id) != "admin":
            return []
        if self.messages.get(group_id) is None:
            return []

        messages = list(self.messages[group_id].values())
        pagination_index = None
        for i, message in enumerate(messages):
            if pagination_last_message_key == message.id:
                pagination_index = i
                break
        if pagination_index is None:
            return []

        return messages[max(0, pagination_index - amount): pagination_index]

    def message_get_with_id(self, cookie: Cookie, group_id: str, message_id: str) -> Optional[Message]:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return None
        if self.messages[group_id].get(message_id) is None:
            return None

        return self.messages[group_id][message_id]

    def message_edit(self, cookie: Cookie, group_id: str, message_id: str, new_content: str) -> bool:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return False
        if self.messages.get(group_id) is None:
            return False
        if self.messages[group_id].get(message_id) is None:
            return False

        message = self.messages[group_id][message_id]
        if message.author_id != cookie.id:
            return False

        self.messages[group_id][message_id].content = new_content
        return True

    def message_delete(self, cookie: Cookie, group_id: str, message_id: str) -> bool:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return False
        if self.messages.get(group_id) is None:
            return False
        if self.messages[group_id].get(message_id) is None:
            return False

        message = self.messages[group_id][message_id]
        if message.author_id != cookie.id and self.user_has_group_access(cookie.id, group_id) != "admin":
            return False

        del self.messages[group_id][message_id]
        return True

    def group_private_create(self, name: str, creator_id: str) -> Optional[Group]:
        if self.users.get(creator_id) is None:
            return None
        group = Group.private(name, [creator_id])
        self.groups[group.id] = group
        self.messages[group.id] = {}

        self.users[creator_id].group_ids.append(group.id)
        self.users[creator_id].interacted_group_ids.append(group.id)
        return group

    def group_contact_create(self, user1_id: str, user1_name: str, user2_id: str, user2_name: str) -> Optional[Group]:
        if self.users.get(user1_id) is None or self.users.get(user2_id) is None:
            return None
        group = Group.private(f"{user1_name} & {user2_name}", [user1_id, user2_id])
        self.groups[group.id] = group
        self.messages[group.id] = {}

        self.users[user1_id].group_ids.append(group.id)
        self.users[user1_id].interacted_group_ids.append(group.id)
        self.users[user2_id].group_ids.append(group.id)
        self.users[user2_id].interacted_group_ids.append(group.id)
        return group

    def group_delete(self, cookie: Cookie, group_id: str) -> bool:
        if self.user_has_group_access(cookie.id, group_id) != "admin":
            return False
        if self.groups.get(group_id) is None or self.messages.get(group_id) is None:
            return False
        del self.messages[group_id]
        group = self.groups[group_id]

        for member_id in group.member_ids:
            self.users[member_id].group_ids.remove(group.id)
            self.users[member_id].interacted_group_ids.remove(group.id)
        for admin_id in group.admin_ids:
            self.users[admin_id].group_ids.remove(group.id)
            self.users[admin_id].interacted_group_ids.remove(group.id)

        del self.groups[group_id]
        return True

    def group_get(self, cookie: Cookie, group_id: str) -> Optional[Group]:
        if self.user_has_group_access(cookie.id, group_id) == "none":
            return None
        if self.groups.get(group_id) is None:
            return None
        return self.groups[group_id]

    def group_search(self, cookie: Cookie, search_query: str) -> list[Group]:
        if self.users.get(cookie.id) is None:
            return []
        groups = list(filter(
            lambda group: search_query in group.name,
            map(
            lambda group_id: self.groups[group_id],
            self.users[cookie.id].group_ids
        )))
        return groups

    def group_rename(self, cookie: Cookie, group_id: str, new_group_name: str) -> bool:
        if self.user_has_group_access(cookie.id, group_id) != "admin":
            return False
        self.groups[group_id].name = new_group_name

    def request_send(self, cookie: Cookie, to_id: str) -> bool:
        if self.users.get(to_id) is None:
            return False
        if self.users.get(cookie.id) is None:
            return False

        self.users[to_id].requests.append(cookie.id)

    def request_get(self, cookie: Cookie) -> list[str]:
        return self.users[cookie.id].requests

    def request_exists(self, cookie: Cookie, to_id: str) -> bool:
        if self.users.get(to_id) is None:
            return False
        if self.users.get(cookie.id) is None:
            return False
        return cookie.id in self.users[to_id].requests

    def request_cancel(self, cookie: Cookie, to_id: str) -> bool:
        if self.users.get(to_id) is None:
            return False
        if self.users.get(cookie.id) is None:
            return False

        self.users[to_id].requests.remove(cookie.id)
