import os
import socket
from socket import socket, AF_INET

API_HOST = os.environ["API_HOST"]
API_PORT = int(os.environ["API_PORT"])


def main():
    inet_socket = socket(AF_INET)
    socket_connection_tuple = (API_HOST, API_PORT)
    inet_socket.connect(socket_connection_tuple)


if __name__ == '__main__':
    main()