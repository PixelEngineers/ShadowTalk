from uuid import uuid4

class User:
  id: str
  name: str
  password: bytes

  group_ids: list[str]
  interacted_group_ids: list[str]
  pinned_group_ids: list[str]
  requests: list[str]

  def __init__(self, name: str, password: bytes):
    self.id = str(uuid4())
    self.name = name
    self.password = password

    self.group_ids = []
    self.interacted_group_ids = []
    self.pinned_group_ids = []
    self.requests = []

  def to_obj(self):
    return {
      "id": self.id,
      "name": self.name,
      "password": self.password,
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
      "password",
      "group_ids",
      "interacted_group_ids",
      "pinned_group_ids",
      "requests"
    ]