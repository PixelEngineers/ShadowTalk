import socket
from threading import Thread
from typing import Callable, Tuple, Optional

class Server:
  server_socket: socket.socket

  def __init__(self, port, host=socket.gethostname()):
    self.server_socket = socket.socket()
    self.server_socket.bind((host, port))

  def set_connection_limit(self, connection_limit):
    self.server_socket.listen(connection_limit)

  def listen(
      self,
      on_connect: Callable[[str, str], None],
      on_disconnect: Callable[[str, str], None],
      on_data: Callable[[str, str], Tuple[str, Optional[str]]],
      data_limit=1024
  ):
    def handle_new_client(
        identifier: str,
        client_address: str,
        client_connection: socket.socket
    ):
      on_connect(identifier, client_address)
      while True:
        data = client_connection.recv(data_limit).decode()
        if not data:
          break
        [response, error] = on_data(identifier, str(data))
        if error is not None:
          client_connection.send(f"Error: {error}".encode())
          break
        client_connection.send(response.encode())
      on_disconnect(identifier, client_address)
      client_connection.close()

    i = 0
    while True:
      connection, address = self.server_socket.accept()
      i += 1
      Thread(target=handle_new_client, args=(str(i), address, connection)).start()


if __name__ == '__main__':
  server = Server(6969)
  server.set_connection_limit(2)

  def send_res(identifier: str, data: str) -> Tuple[str, Optional[str]]:
    print(f"{identifier}: {data}")
    return f"You said {data}", None

  server.listen(
    lambda identifier, address: print(f"{address} [{identifier}] has joined the connection"),
    lambda identifier, address: print(f"{address} [{identifier}] has left the connection"),
    send_res
  )