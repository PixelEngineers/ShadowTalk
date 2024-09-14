from database import DatabaseInterop
from os.path import exists
from typing import Optional, Any, TypeVar, Callable
from bcrypt import hashpw, gensalt
import pickle

from .user import User
from .group import Group
from .message import Message

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

class FileDatabase(DatabaseInterop):
  users: list[User]
  groups: list[Group]
  messages: dict[str, list[Message]]

  user_db_location: str
  group_db_location: str
  messages_db_location: str

  def __init__(self, user_db_location: str, group_db_location: str, messages_db_location: str):
    create_if_not_exist(user_db_location, pickle.dumps([]), 'wb')
    create_if_not_exist(group_db_location, pickle.dumps([]), 'wb')
    create_if_not_exist(messages_db_location, pickle.dumps({}), 'wb')

    with open(user_db_location, 'rb') as f:
      self.users = pickle.load(f)
    with open(group_db_location, 'rb') as f:
      self.groups = pickle.load(f)
    with open(messages_db_location, 'rb') as f:
      self.messages = pickle.load(f)

    self.user_db_location = user_db_location
    self.group_db_location = group_db_location
    self.messages_db_location = messages_db_location
    super().__init__()

  def deinit(self):
    with open(self.user_db_location, 'wb') as f:
      pickle.dump(self.users, f)
    with open(self.group_db_location, 'wb') as f:
      pickle.dump(self.groups, f)
    with open(self.messages_db_location, 'wb') as f:
      pickle.dump(self.messages, f)

  def user_create(self, name: str, password: str) -> str:
    user = User(name, hashpw(password.encode('utf-8'), gensalt()))
    self.users.append(user)
    return user.id

  # https://stackoverflow.com/a/13001189
  def user_change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
    index = find_index(self.users, lambda user: user.id == user_id)
    if index is None:
      return False

    old_hash = self.users[index].password
    if not old_hash == hashpw(new_password.encode('utf-8'), old_hash):
      return False

    self.users[index].password = hashpw(new_password.encode('utf-8'), gensalt())
    return True

  def user_join_group(self, user_id: str, group_id: str) -> bool:
    index = find_index(self.users, lambda user: user.id == user_id)
    if index is None:
      return False

    self.users[index].group_ids.append(group_id)
    self.users[index].interacted_group_ids.append(group_id)

    group_index = find_index(self.groups, lambda group: group.id == group_id)
    if group_index is None:
      return False

    self.groups[group_index].member_ids.append(user_id)
    return True

  def user_leave_group(self, user_id: str, group_id: str, wipe_messages: bool) -> bool:
    index = find_index(self.users, lambda user: user.id == user_id)
    if index is None:
      return False

    self.users[index].group_ids.remove(group_id)
    if wipe_messages:
      self.user_wipe_all_group_messages(user_id, group_id)
      # we can forget about this group :)
      self.users[index].interacted_group_ids.remove(group_id)

    group_index = find_index(self.groups, lambda group: group.id == group_id)
    if group_index is None:
      return False

    group_data = self.groups[group_index]
    if user_id in group_data.admin_ids:
      self.groups[group_index].admin_ids.remove(user_id)
    else:
      self.groups[group_index].member_ids.remove(user_id)

    return True

  def user_admin_promote_group(self, user_id: str, group_id: str) -> bool:
    index = find_index(self.users, lambda user: user.id == user_id)
    group_index = find_index(self.groups, lambda group: group.id == group_id)
    if index is None or group_index is None:
      return False

    self.groups[group_index].member_ids.remove(user_id)
    self.groups[group_index].admin_ids.append(user_id)
    return True

  def user_admin_demote_group(self, user_id: str, group_id: str) -> bool:
    index = find_index(self.users, lambda user: user.id == user_id)
    group_index = find_index(self.groups, lambda group: group.id == group_id)
    if index is None or group_index is None:
      return False

    self.groups[group_index].admin_ids.remove(user_id)
    self.groups[group_index].member_ids.append(user_id)
    return True

  def user_pin_group(self, user_id: str, group_id: str) -> bool:
    index = find_index(self.users, lambda user: user.id == user_id)
    if index is None:
      return False

    self.users[index].pinned_group_ids.append(group_id)
    return True

  def user_unpin_group(self, user_id: str, group_id: str) -> bool:
    index = find_index(self.users, lambda user: user.id == user_id)
    if index is None:
      return False

    self.users[index].pinned_group_ids.remove(group_id)
    return True

  def user_delete(self, user_id: str) -> bool:
    # leave groups
    user_index = find_index(self.users, lambda user: user.id == user_id)
    if user_index is None:
      return False
    user_data = self.users[user_index]

    for interacted_group_id in user_data.interacted_group_ids:
      self.user_wipe_all_group_messages(user_id, interacted_group_id)

    for current_group_id in user_data.group_ids:
      group_index = find_index(self.groups, lambda group: group.id == current_group_id)
      if group_index is None:
        continue
      self.groups[group_index].member_ids.remove(user_id)

    self.users.pop(user_index)
    return True

  """
  Factory reset user
  """
  def user_wipe_all_data(self, user_id: str) -> bool:
    # leave groups
    user_index = find_index(self.users, lambda user: user.id == user_id)
    if user_index is None:
      return False

    for interacted_group_id in self.users[user_index].interacted_group_ids:
      self.user_wipe_all_group_messages(user_id, interacted_group_id)

    self.users[user_index].group_ids = []
    self.users[user_index].interacted_group_ids = []
    self.users[user_index].pinned_group_ids = []
    self.users[user_index].requests = []
    return True

  def user_wipe_all_messages(self, user_id: str) -> bool:
    user_index = find_index(self.users, lambda user: user.id == user_id)
    if user_index is None:
      return False

    for interacted_group_id in self.users[user_index].interacted_group_ids:
      self.user_wipe_all_group_messages(user_id, interacted_group_id)
    return True

  def user_wipe_all_group_messages(self, user_id: str, group_id: str) -> bool:
    if group_id not in self.messages:
      return False
    self.messages[group_id] = list(filter(lambda message: not (message.author_id == user_id), self.messages[group_id]))
    return True

  def user_wipe_all_left_group_messages(self, user_id: str) -> bool:
    user_index = find_index(self.users, lambda user: user.id == user_id)
    if user_index is None:
      return False
    user_data = self.users[user_index]
    for interacted_group_id in user_data.interacted_group_ids:
      if interacted_group_id in user_data.group_ids:
        continue
      self.user_wipe_all_group_messages(user_id, interacted_group_id)

    # now we can forget about those groups :)
    self.users[user_index].interacted_group_ids = user_data.group_ids
    return True

  def message_send(
      self,
      group_id: str,
      content: str,
      author_name: str,
      author_id: str,
      is_author_admin: bool,
      is_reply: bool,
      reply_to_user: Optional[str],
      reply_to_content: Optional[str]
  ) -> bool:
    if group_id not in self.messages:
      self.messages[group_id] = []
      return False

    message = Message(author_id, author_name, content, is_author_admin, is_reply, reply_to_user, reply_to_content)
    self.messages[group_id].append(message)

    group_index = find_index(self.groups, lambda group: group.id == group_id)
    self.groups[group_index].last_message_id = message.id
    self.groups[group_index].last_message_content = content
    self.groups[group_index].last_message_author_name = author_name
    return True

  def message_get(self, group_id: str, pagination: int = 0, amount: int = 1) -> list[Any]:
    if group_id not in self.messages:
      return []
    return self.messages[group_id][pagination:(pagination + amount)]

  def message_delete(self, group_id: str, message_id: str) -> bool:
    if group_id not in self.messages:
      return False

    msg_index = find_index(self.messages[group_id], lambda message: message.id == message_id)
    if msg_index is None:
      return False
    self.messages[group_id].pop(msg_index)
    return True

  def group_private_create(self, name: str, creator_id: str) -> Optional[str]:
    user_index = find_index(self.users, lambda user: user.id == creator_id)
    if user_index is None:
      return None

    group = Group.private(name, [])
    self.groups.append(group)
    self.user_join_group(creator_id, group.id)
    self.user_admin_promote_group(creator_id, group.id)
    return group.id

  def group_contact_create(self, user1_id: str, user1_name: str, user2_id: str, user2_name: str) -> Optional[str]:
    user1_index = find_index(self.users, lambda user: user.id == user1_id)
    user2_index = find_index(self.users, lambda user: user.id == user2_id)
    if user1_index is None or user2_index is None:
      return None

    group = Group.private(f"{user1_name} & {user2_name}", [user1_id, user2_id])
    self.groups.append(group)

    self.users[user1_index].group_ids.append(group.id)
    self.users[user2_index].group_ids.append(group.id)
    return group.id

  # def group_public_create(self, name: str, creator_id: str) -> str:
  #   group = Group.public(name, creator_id)
  #   self.groups.append(group)
  #  return group.id

  def group_delete(self, group_id: str) -> bool:
    group_index = find_index(self.groups, lambda group: group.id == group_id)
    if group_index is None:
      return False

    group_data = self.groups[group_index]

    # note: this doesn't handle public servers
    for member_id in [*group_data.member_ids, *group_data.admin_ids]:
      self.user_leave_group(member_id, group_data.id, False)

    del self.messages[group_data.id]
    del self.groups[group_index]

    return True

  def group_rename(self, group_id: str, new_group_name: str) -> bool:
    group_index = find_index(self.groups, lambda group: group.id == group_id)
    if group_index is None:
      return False

    self.groups[group_index].name = new_group_name
    return True

  def request_send(self, from_id: str, to_id: str) -> bool:
    to_index = find_index(self.users, lambda user: user.id == to_id)
    from_index = find_index(self.users, lambda user: user.id == from_id)
    if to_index is None or from_index is None:
      return False

    self.users[to_index].requests.append(from_id)
    return True

  def request_exists(self, from_id: str, to_id: str) -> bool:
    to_index = find_index(self.users, lambda user: user.id == to_id)
    if to_index is None:
      return False

    return to_id in self.users[to_index].requests

  def request_cancel(self, from_id: str, to_id: str) -> bool:
    to_index = find_index(self.users, lambda user: user.id == to_id)
    from_index = find_index(self.users, lambda user: user.id == from_id)
    if to_index is None or from_index is None:
      return False

    self.users[to_index].requests.remove(from_id)
    return True
