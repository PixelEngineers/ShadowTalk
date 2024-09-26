from uuid import uuid4
from typing import Optional

MESSAGE_AUTHOR_ID = "author_id"
MESSAGE_INDEX = "index"
MESSAGE_AUTHOR_NAME = "author_name"
MESSAGE_CONTENT = "content"
MESSAGE_IS_AUTHOR_ADMIN = "is_author_admin"
MESSAGE_IS_REPLY = "is_reply"
MESSAGE_REPLY_TO_USER = "reply_to_user"
MESSAGE_REPLY_TO_CONTENT = "reply_to_content"


class Message:
    id: str
    index: int # used for pagination
    content: str

    author_name: str
    author_id: str
    is_author_admin: bool

    is_reply: bool
    reply_to_user: Optional[str]
    reply_to_content: Optional[str]

    def __init__(
            self,
            identifier: str,
            index: int,
            author_id: str,
            author_name: str,
            content: str,
            is_author_admin: bool,
            is_reply: bool,
            reply_to_user: Optional[str],
            reply_to_content: Optional[str]
    ):
        self.id = identifier
        self.index = index
        self.author_id = author_id
        self.author_name = author_name
        self.content = content
        self.is_author_admin = is_author_admin
        self.is_reply = is_reply
        self.reply_to_user = reply_to_user
        self.reply_to_content = reply_to_content

    @staticmethod
    def generate(
            author_id: str,
            author_name: str,
            content: str,
            is_author_admin: bool,
            is_reply: bool,
            reply_to_user: Optional[str] = None,
            reply_to_content: Optional[str] = None
    ) -> "Message":
        return Message(
            str(uuid4()),
            0,
            author_id,
            author_name,
            content,
            is_author_admin,
            is_reply,
            reply_to_user,
            reply_to_content
        )

    def to_obj(self):
        return {
            MESSAGE_AUTHOR_ID: self.author_id,
            MESSAGE_INDEX: self.index,
            MESSAGE_AUTHOR_NAME: self.author_name,
            MESSAGE_CONTENT: self.content,
            MESSAGE_IS_AUTHOR_ADMIN: self.is_author_admin,
            MESSAGE_IS_REPLY: self.is_reply,
            MESSAGE_REPLY_TO_USER: self.reply_to_user,
            MESSAGE_REPLY_TO_CONTENT: self.reply_to_content
        }

    @staticmethod
    def from_snapshot(message_id: str, message_data: dict) -> Optional["Message"]:
        try:
            return Message(
                message_id,
                message_data[MESSAGE_AUTHOR_ID],
                message_data[MESSAGE_INDEX],
                message_data[MESSAGE_AUTHOR_NAME],
                message_data[MESSAGE_CONTENT],
                message_data[MESSAGE_IS_AUTHOR_ADMIN],
                message_data[MESSAGE_IS_REPLY],
                message_data[MESSAGE_REPLY_TO_USER],
                message_data[MESSAGE_REPLY_TO_CONTENT]
            )
        except KeyError:
            return None
