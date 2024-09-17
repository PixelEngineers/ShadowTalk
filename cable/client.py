import socket

class Client:
  client_socket: socket.socket

  def __init__(self, port, host=socket.gethostname()):
    self.client_socket = socket.socket()
    self.client_socket.connect((host, port))

  def send(self, data: str, receive_data_limit=1024) -> str:
    self.client_socket.send(data.encode())
    return self.client_socket.recv(receive_data_limit).decode()

if __name__ == '__main__':
  client = Client(6969)
  message = input("> ")
  while message != "quit":
    print(client.send(message))
    message = input("> ")
