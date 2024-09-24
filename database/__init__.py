from FileDatabase import *

"""
TOKEN SYSTEM YOU CUNT
"""

class DatabaseInterop:
  def __init__(self): pass
  def deinit(self): pass

  def user_get(self, name: str): pass

  """dont show group information here, ig"""
  def user_public_get(self, name: str): pass
  def user_exists(self) -> bool: pass
  def user_authenticate(self, name: str, password: str) -> bool: pass
  def user_create(self, name: str, password: str) -> str: pass
  def user_change_password(self, user_id: str, old_password: str, new_password: str) -> bool: pass
  # def user_change_username(self, user_id: str, new_user_name: str) -> bool: pass
  def user_join_group(self, user_id: str, group_id: str) -> bool: pass
  def user_leave_group(self, user_id: str, group_id: str, wipe_messages: bool) -> bool: pass
  def user_admin_promote_group(self, user_id: str, group_id: str) -> bool: pass
  def user_admin_demote_group(self, user_id: str, group_id: str) -> bool: pass
  def user_pin_group(self, user_id: str, group_id: str) -> bool: pass
  def user_unpin_group(self, user_id: str, group_id: str) -> bool: pass
  def user_delete(self, user_id: str) -> bool: pass
  def user_wipe_all_data(self, user_id: str) -> bool: pass
  def user_wipe_all_messages(self, user_id: str) -> bool: pass
  def user_wipe_all_group_messages(self, user_id: str, group_id: str) -> bool: pass
  def user_wipe_all_left_group_messages(self, user_id: str) -> bool: pass
  def user_groups_get(self, search_query: str) -> list: pass
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
  ) -> bool: pass
  def message_get(self, group_id: str, pagination: int = 0, amount: int = 1) -> list[Any]: pass
  def message_edit(self, group_id: str, message_id: str, new_content: str) -> bool: pass
  def message_delete(self, group_id: str, message_id: str) -> bool: pass
  def group_private_create(self, name: str, creator_id: str) -> Optional[str]: pass
  def group_contact_create(self, user1_id: str, user1_name: str, user2_id: str, user2_name: str) -> Optional[str]: pass
  # def group_public_create(self, name: str, creator_id: str) -> str: pass
  def group_delete(self, group_id: str) -> bool: pass
  def group_get(self, group_id: str): pass
  def group_rename(self, group_id: str, new_group_name: str) -> bool: pass
  def request_send(self, from_id: str, to_id: str) -> bool: pass
  def request_exists(self, from_id: str, to_id: str) -> bool: pass
  def request_cancel(self, from_id: str, to_id: str) -> bool: pass