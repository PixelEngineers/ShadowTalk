from uuid import uuid4
from typing import Optional

class Message:
  id: str
  content: str

  author_name: str
  author_id: str
  is_author_admin: bool

  is_reply: bool
  reply_to_user: Optional[str]
  reply_to_content: Optional[str]

  def __init__(
      self,
      author_id,
      author_name,
      content,
      is_author_admin,
      is_reply,
      reply_to_user = None,
      reply_to_content = None
  ):
    self.id = str(uuid4())
    self.author_id = author_id
    self.author_name = author_name
    self.content = content
    self.is_author_admin = is_author_admin
    self.is_reply = is_reply
    self.reply_to_user = reply_to_user
    self.reply_to_content = reply_to_content

  def to_obj(self):
    return {
      "id": self.id,
      "author_id": self.author_id,
      "author_name": self.author_name,
      "content": self.content,
      "is_author_admin": self.is_author_admin,
      "is_reply": self.is_reply,
      "reply_to_user": self.reply_to_user,
      "reply_to_content": self.reply_to_content
    }

  @staticmethod
  def get_columns():
    return [
      "id"
      "author_id",
      "author_name",
      "content",
      "is_author_admin",
      "is_reply",
      "reply_to_user",
      "reply_to_content",
    ]
