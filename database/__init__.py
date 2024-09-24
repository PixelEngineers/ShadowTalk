import database.FileDatabase

useDatabase = FileDatabase.FileDatabase(
  "file_db/users.dat",
  "file_db/groups.dat",
  "file_db/messages.dat"
)