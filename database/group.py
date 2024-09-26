from uuid import uuid4

GROUP_ID = "id"
GROUP_NAME = "name"
GROUP_ADMIN_IDS = "admin_ids"
GROUP_MEMBER_IDS = "member_ids"
GROUP_LAST_MESSAGE_ID = "last_message_id"
GROUP_LAST_MESSAGE_CONTENT = "last_message_content"
GROUP_LAST_MESSAGE_AUTHOR_NAME = "last_message_author_name"

class Group:
    id: str
    name: str

    admin_ids: list[str]
    member_ids: list[str]
    last_message_id: str
    last_message_content: str
    last_message_author_name: str

    def __init__(
            self,
            identifier: str,
            name: str,
            admin_ids: list[str],
            member_ids: list[str],
            last_message_id: str,
            last_message_content: str,
            last_message_author_name: str
    ):
        self.id = identifier
        self.name = name
        self.admin_ids = admin_ids
        self.member_ids = member_ids
        self.last_message_id = last_message_id
        self.last_message_content = last_message_content
        self.last_message_author_name = last_message_author_name

    @staticmethod
    def generate(name) -> "Group":
        return Group(
            str(uuid4()),
            name,
            [],
            [],
            "0",
            f"\"{name}\" Created",
            "system"
        )

    def to_obj(self):
        return {
            GROUP_ID: self.id,
            GROUP_NAME: self.name,
            GROUP_ADMIN_IDS: self.admin_ids,
            GROUP_MEMBER_IDS: self.member_ids,
            GROUP_LAST_MESSAGE_ID: self.last_message_id,
            GROUP_LAST_MESSAGE_CONTENT: self.last_message_content,
            GROUP_LAST_MESSAGE_AUTHOR_NAME: self.last_message_author_name,
        }

    @staticmethod
    def private(name: str, creator_ids: list[str]) -> "Group":
        self = Group.generate(name)

        self.admin_ids = creator_ids
        return self
