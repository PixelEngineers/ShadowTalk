from database.FileDatabase import FileDatabase

fd = FileDatabase()
# john_id = fd.user_create("john", "doe")
# jerry_id = fd.user_create("jerry", "doe")
# fd.group_contact_create(john_id, "John", jerry_id, "Jerry")
print(fd.groups[0].to_obj())
print(fd.users[0].to_obj())
print(fd.users[1].to_obj())
fd.deinit()