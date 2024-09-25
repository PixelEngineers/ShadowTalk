from uuid import uuid4

from typing import Optional

class Group:
  id: str
  name: str

  is_public: bool
  owner_id: Optional[str]

  admin_ids: list[str]
  member_ids: list[str]
  last_message_id: str
  last_message_content: str
  last_message_author_name: str

  def __init__(self): pass

  @staticmethod
  def generate(name):
    self = Group()
    self.id = str(uuid4())
    self.name = name
    self.is_public = False
    self.owner_id = None
    self.admin_ids = []
    self.member_ids = []
    self.last_message_id = "0"
    self.last_message_content = f"\"{name}\" Created"
    self.last_message_author_name = "system"
    pass


  @staticmethod
  def from_attr(
    id: str,
    name: str,
    is_public: bool,
    owner_id: Optional[str],
    admin_ids: list[str],
    member_ids: list[str],
    last_message_id: str,
    last_message_content: str,
    last_message_author_name: str
  ):
    self = Group()
    self.id = id
    self.name = name
    self.is_public = is_public
    self.owner_id = owner_id
    self.admin_ids = admin_ids
    self.member_ids = member_ids
    self.last_message_id = last_message_id
    self.last_message_content = last_message_content
    self.last_message_author_name = last_message_author_name


  def to_obj(self):
    return {
      "id": self.id,
      "name": self.name,
      "is_public": self.is_public,
      "owner_id": self.owner_id,
      "admin_ids": self.admin_ids,
      "member_ids": self.member_ids,
      "last_message_id": self.last_message_id,
      "last_message_content": self.last_message_content,
      "last_message_author_name": self.last_message_author_name
    }

  @staticmethod
  def get_columns():
    return [
      "id",
      "name",
      "is_public",
      "owner_id",
      "admin_ids",
      "member_ids",
      "last_message"
    ]

  @staticmethod
  def private(name: str, creator_ids: list[str]) -> "Group":
    self = Group(name)

    self.is_public = False
    self.owner_id = None

    self.admin_ids = creator_ids
    return self

  # @staticmethod
  # def public(name: str, creator_id: str):
  #   self = Group(name)
  #
  #   self.is_public = True
  #   self.owner_id = creator_id
  #
  #   self.admin_ids = []
  #   return self
