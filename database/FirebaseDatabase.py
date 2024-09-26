import ssl
from os import getenv

from database.FileDatabase import DatabaseInterop
from uuid import uuid4
from typing import Optional, Any, TypeVar
from datetime import timedelta
from firebase_config import config, message_path, USER_COLLECTION, GROUP_COLLECTION

from scrypt import hash as firebase_hash
from firebase_admin import auth, db, initialize_app, App
from firebase_admin._user_mgt import ExportedUserRecord
from firebase_admin.firestore import client
from google.cloud.firestore import ArrayUnion, ArrayRemove, CollectionReference, Client, DocumentSnapshot

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jwt import encode
from ssl import create_default_context
from smtplib import SMTP_SSL

from database.message import Message, MESSAGE_AUTHOR_ID
from database.cookie import Cookie
from database.user import PublicUser, PrivateUser, \
    USER_GROUP_IDS, \
    USER_INTERACTED_GROUP_IDS, \
    USER_PINNED_GROUP_IDS, \
    USER_REQUESTS

from database.group import Group, \
    GROUP_ID, \
    GROUP_NAME, \
    GROUP_ADMIN_IDS, \
    GROUP_MEMBER_IDS, \
    GROUP_LAST_MESSAGE_ID, \
    GROUP_LAST_MESSAGE_CONTENT, \
    GROUP_LAST_MESSAGE_AUTHOR_NAME


ID = TypeVar("ID")
Token = TypeVar("Token")
class FirebaseDatabase(DatabaseInterop):
    firebase: App
    firestore: Client
    user_collection: CollectionReference
    group_collection: CollectionReference

    def __init__(self):
        self.firebase = initialize_app(config)
        self.firestore = client()
        self.user_collection = self.firestore.collection(USER_COLLECTION)
        self.group_collection = self.firestore.collection(GROUP_COLLECTION)
        super().__init__()

    # Done
    def user_public_get(self, user_id: str) -> Optional[PublicUser]:
        try:
            user_data = auth.get_user(user_id)
        except:
            return None
        return PublicUser(user_data.display_name, user_data.photo_url)

    # Done
    def user_exists(self, user_id: str) -> bool:
        try:
            _ = auth.get_user(user_id)
            return True
        except:
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
                if not firebase_hash(password, user.password_salt) == user.password_hash:
                    return None, False
                return user, True
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
    ) -> Optional[Token]:
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
    # NOTE: THIS FUNCTION TAKES ~4 SECONDS TO RUN
    def user_verify(self, user_id: str) -> bool:
        user_record = auth.get_user(user_id)
        if user_record.email_verified:
            return True

        message = MIMEMultipart("alternative")
        message["Subject"] = "ShadowTalk - User Email Verification Code"
        message["From"] = getenv("EMAIL")
        message["To"] = user_record.email
        encoded = encode({'_id': user_record.uid}, getenv("EMAIL_TOKEN"), algorithm="HS256")
        url = f"{getenv('DOMAIN')}/verify-email?token={encoded}"
        body = f"""
        <h1 style="text-align: center;">ShadowTalk User Email Verification</h1>
        <br>
        <h3 style="text-align: center;">
            <div style="font-size: 2rem;">
                Hello {user_record.display_name}!<br>
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


    # Done
    def user_login(self, email: str, password: str) -> Optional[Token]:
        user, correct_login = self.user_authenticate(email, password)
        if not correct_login:
            return None
        try:
            return auth.create_session_cookie(user.uid, timedelta(days=30))
        except:
            return None

    # def user_logout(self, cookie: Cookie):
    #     pass

    # Done
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

    @staticmethod
    def __group_get(group: DocumentSnapshot) -> Group:
        return Group(
            group.get(GROUP_ID),
            group.get(GROUP_NAME),
            group.get(GROUP_ADMIN_IDS),
            group.get(GROUP_MEMBER_IDS),
            group.get(GROUP_LAST_MESSAGE_ID),
            group.get(GROUP_LAST_MESSAGE_CONTENT),
            group.get(GROUP_LAST_MESSAGE_AUTHOR_NAME),
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
            output_groups.append(self.__group_get(group))
        return output_groups

    # Done
    def user_interacted_groups_get(self, cookie: Cookie, search_query: str) -> list[Group]:
        user_data = self.user_collection.document(cookie.uid).get()
        interacted_group_ids = user_data.get(USER_INTERACTED_GROUP_IDS)
        groups = self.group_collection \
            .where(GROUP_ID, 'in', interacted_group_ids) \
            .stream()
        output_groups = []
        for group in groups:
            output_groups.append(self.__group_get(group))
        return output_groups

    # Done
    def user_join_group(self, cookie: Cookie, group_id: str) -> bool:
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access != "none":
            return False
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
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return False

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
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return False

        try:
            self.user_collection.document(cookie.uid).update({
                USER_PINNED_GROUP_IDS: ArrayUnion([group_id])
            })
            return True
        except:
            return False

    # Done
    def user_unpin_group(self, cookie: Cookie, group_id: str) -> bool:
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return False

        try:
            self.user_collection.document(cookie.uid).update({
                USER_PINNED_GROUP_IDS: ArrayRemove([group_id])
            })
            return True
        except:
            return False

    # Done
    def user_admin_promote_group(self, cookie: Cookie, group_id: str) -> bool:
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return False

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
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return False

        try:
            self.group_collection.document(cookie.uid).update({
                GROUP_ADMIN_IDS: ArrayRemove([cookie.uid]),
                GROUP_MEMBER_IDS: ArrayUnion([cookie.uid])
            })
            return True
        except:
            return False

    @staticmethod
    def __delete_all_group_messages_for_user(user_id: str, group_id) -> bool:
        try:
            messages_snapshot = db.reference(message_path(group_id)).get()
            for message_id, message_data in messages_snapshot.items():
                if message_data.get(MESSAGE_AUTHOR_ID) == user_id:
                    db.reference(message_path(group_id) + f"/{message_id}").delete()
            return True
        except:
            return False

    # Done
    def user_wipe_all_messages(self, cookie: Cookie) -> bool:
        try:
            user_data = self.user_collection.document(cookie.uid).get()
            interacted_group_ids = user_data.get(USER_INTERACTED_GROUP_IDS)
            group_ids = user_data.get(USER_GROUP_IDS)
        except:
            return False
        for interacted_group_id in interacted_group_ids:
            self.__delete_all_group_messages_for_user(cookie.uid, interacted_group_id)
        try:
            self.user_collection.document(cookie.uid).update({
                USER_INTERACTED_GROUP_IDS: group_ids
            })
        except:
            return False
        return True

    # Done
    def user_wipe_all_group_messages(self, cookie: Cookie, group_id: str) -> bool:
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return False

        if not self.__delete_all_group_messages_for_user(cookie.uid, group_id):
            return False

        user_data = self.user_collection.document(cookie.uid).get()
        if group_id in user_data.get(USER_GROUP_IDS):
            return True

        # The group from which messages were removed from has been left by the user
        try:
            self.user_collection.document(cookie.uid).update({
                USER_INTERACTED_GROUP_IDS: ArrayRemove([group_id])
            })
            return True
        except:
            return False

    # Done
    def user_wipe_all_left_group_messages(self, cookie: Cookie) -> bool:
        try:
            user_data = self.user_collection.document(cookie.uid).get()
        except:
            return False
        interacted_group_ids = user_data.get(USER_INTERACTED_GROUP_IDS)
        group_ids = user_data.get(USER_GROUP_IDS)
        for interacted_group_id in interacted_group_ids:
            if interacted_group_id in group_ids:
                continue
            self.__delete_all_group_messages_for_user(cookie.uid, interacted_group_id)
        return True

    # Done
    def message_send(
            self,
            cookie: Cookie,
            group_id: str,
            content: str,
            is_reply: bool,
            reply_to_user: Optional[str],
            reply_to_content: Optional[str]
    ) -> bool:
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return False
        message = Message.generate(
            cookie.uid,
            cookie.name,
            content,
            access == "admin",
            is_reply,
            reply_to_user,
            reply_to_content
        )
        try:
            db.reference(message_path(group_id) + f"/{message.id}").set(message.to_obj())
            return True
        except:
            return False

    # Done
    def message_get(self, cookie: Cookie, group_id: str, pagination_last_message_key: Optional[str] = None, amount: int = 1) -> list[Any]:
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return []
        ref = db.reference(message_path(group_id))
        query = ref.order_by_child('index').limit_to_first(amount)
        query.start_at(pagination_last_message_key)
        try:
            snapshot = query.get()
        except:
            return []
        if snapshot is None:
            return []

        output_messages = []
        for message_id, message_body in snapshot.items():
            message = Message.from_snapshot(message_id, message_body)
            if message is None:
                continue
            output_messages.append(message)
        return output_messages

    # Done
    def message_edit(self, cookie: Cookie, group_id: str, message_id: str, new_content: str) -> bool:
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return False

        try:
            old_message_data = db.reference(message_path(group_id) + f"/{message_id}").get()
        except:
            return False

        if old_message_data is None:
            return False
        message = Message.from_snapshot(message_id, old_message_data)

        if message.author_id != cookie.uid:
            return False

        message.content = new_content

        try:
            db.reference(message_path(group_id) + f"/{message_id}").set(message.to_obj())
        except:
            return False
        return True

    # Done
    def message_delete(self, cookie: Cookie, group_id: str, message_id: str) -> bool:
        access = self.__user_has_group_access(cookie.uid, group_id)
        if access == "none":
            return False
        message_ref = db.reference(message_path(group_id) + f"/{message_id}")
        try:
            message_data = message_ref.get()
        except:
            return False

        message = Message.from_snapshot(message_id, message_data)
        if message is None:
            return False

        created_message = message.author_id == cookie.uid
        is_admin = access == "admin"
        if not created_message and not is_admin:
            return False
        try:
            message_ref.delete()
        except:
            return False
        return True


    def __group_create(self, group: Group) -> Optional[Group]:
        try:
            self.group_collection.document(group.id).set(group.to_obj())
            return group
        except:
            return None

    def __user_has_group_access(self, uid: str, group_id: str) -> str:
        group_reference = self.group_collection.document(group_id)
        try:
            members_list = group_reference.get(GROUP_MEMBER_IDS)
        except:
            return "none"
        if uid in members_list:
            return "member"
        try:
            admin_list = group_reference.get(GROUP_ADMIN_IDS)
        except:
            return "none"
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
        except:
            return False
        return True

    # Done
    def group_get(self, cookie: Cookie, group_id: str) -> Optional[Group]:
        if self.__user_has_group_access(cookie.uid, group_id) == "none":
            return None
        group_record = self.group_collection.document(group_id).get()
        return self.__group_get(group_record)

    # Done
    def group_rename(self, cookie: Cookie, group_id: str, new_group_name: str) -> bool:
        if self.__user_has_group_access(cookie.uid, group_id) != "admin":
            return False
        try:
            self.group_collection.document(group_id).update({
                GROUP_NAME: new_group_name,
            })
        except:
            return False
        return True

    # Done
    def request_send(self, cookie: Cookie, to_id: str) -> bool:
        try:
            self.user_collection.document(to_id).update({
                USER_REQUESTS: ArrayUnion([cookie.uid])
            })
        except:
            return False
        return True


    # Done
    def request_exists(self, cookie: Cookie, to_id: str) -> bool:
        try:
            self.user_collection.document(to_id).update({
                USER_REQUESTS: ArrayUnion([cookie.uid])
            })
        except:
            return False
        return True

    # Done
    def request_cancel(self, cookie: Cookie, to_id: str) -> bool:
        try:
            self.user_collection.document(to_id).update({
                USER_REQUESTS: ArrayRemove([cookie.uid])
            })
        except:
            return False
        return True
