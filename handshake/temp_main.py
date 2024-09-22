from handshake.agent import Agent
from handshake.keyservice import FileKeyService

key_service = FileKeyService()

bob = Agent.file_else_default("bob", key_service, 10)
alice = Agent.file_else_default("alice", key_service, 10)

imb = alice.connect("bob")
bob.initial_message("alice", imb)

alice_hello = alice.send("bob", b"Hello Bob!")
print(f"Bob received: {bob.receive('alice', alice_hello)}")

bob.to_file()
alice.to_file()
key_service.deinit()