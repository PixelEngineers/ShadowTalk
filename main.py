# from database.FileDatabase import FileDatabase

# fd = FileDatabase(
#   'file_db/users.dat',
#   'file_db/groups.dat',
#   'file_db/messages.dat',
# )
#
# # if db is empty
# if len(fd.users) == 0:
#   john_id = fd.user_create("john", "doe")
#   jerry_id = fd.user_create("jerry", "doe")
#   fd.group_contact_create(john_id, "John", jerry_id, "Jerry")
#
# print(fd.groups[0].to_obj())
# print(fd.users[0].to_obj())
# print(fd.users[1].to_obj())
# fd.deinit()

# from database.FirebaseDatabase import FirebaseDatabase
# fb = FirebaseDatabase()
# fb.user_create("ojesh", "sri")

from google.cloud import firestore