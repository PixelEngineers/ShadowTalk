from typing import Optional
from uuid import uuid4

class User:
    id: str
    email: str
    is_verified_email: bool
    name: str
    profile_picture: Optional[str]

    group_ids: list[str]
    interacted_group_ids: list[str]
    pinned_group_ids: list[str]
    requests: list[str]

    def __init__(self, email: str, name: str, profile_picture: Optional[str] = None):
        self.id = str(uuid4())
        self.name = name
        self.email = email
        self.is_verified_email = False
        self.profile_picture = profile_picture

        self.group_ids = []
        self.interacted_group_ids = []
        self.pinned_group_ids = []
        self.requests = []

    def to_obj(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_verified_email": self.is_verified_email,
            "profile_picture": self.profile_picture,
            "group_ids": self.group_ids,
            "interacted_group_ids": self.interacted_group_ids,
            "pinned_group_ids": self.pinned_group_ids,
            "requests": self.requests
        }

    @staticmethod
    def get_columns():
        return [
            "id",
            "name",
            "email",
            "is_verified_email",
            "profile_picture",
            "group_ids",
            "interacted_group_ids",
            "pinned_group_ids",
            "requests"
        ]

class PublicUser:
    name: str
    profile_picture: Optional[str]

    @staticmethod
    def from_user(self, user: User):
        self.name = user.name
        self.profile_picture = user.profile_picture

    def __init__(self, name: str, profile_picture: Optional[str] = None):
        self.name = name
        self.profile_picture = profile_picture

class PrivateUser:
    name: str
    profile_picture: Optional[str]
    email: str
    is_verified_email: bool

    def __init__(self, name: str, email: str, is_verified_email: bool, profile_picture: Optional[str] = None):
        self.name = name
        self.profile_picture = profile_picture
        self.email = email
        self.is_verified_email = is_verified_email


USER_GROUP_IDS = "group_ids"
USER_INTERACTED_GROUP_IDS = "interacted_group_ids"
USER_PINNED_GROUP_IDS = "pinned_group_ids"
USER_REQUESTS = "requests"

class UserRecord:
    id: str
    group_ids: list[str]
    interacted_group_ids: list[str]
    pinned_group_ids: list[str]
    requests: list[str]

    def __init__(
            self,
            identifier: str,
            group_ids: list[str],
            interacted_group_ids: list[str],
            pinned_group_ids: list[str],
            requests: list[str]
    ):
        self.id = identifier
        self.group_ids = group_ids
        self.interacted_group_ids = interacted_group_ids
        self.pinned_group_ids = pinned_group_ids
        self.requests = requests
