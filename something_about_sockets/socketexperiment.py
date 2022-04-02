from ast import Bytes
from io import BytesIO
import logging
import os
from socket import socket, AF_INET, SOCK_STREAM
import sys

API_HOST = os.environ["API_HOST"]
API_PORT = int(os.environ["API_PORT"])

RECV_SIZE = 1024
MAX_RECV_SIZE = 1024 * 1024 * 8

logger = logging.getLogger(__name__)


def generate_socket() -> socket:
    return socket(AF_INET, SOCK_STREAM)


def get(host: str, port: int, path: str) -> bytearray:
    request_bytes: bytes = f"GET {path} HTTP/1.1\r\n\r\n".encode()
    response_bytes = bytearray(MAX_RECV_SIZE)  # TODO: This sucks, make a dynamic bytearray type or something
    connection_tuple = (host, port)

    print('Generating socket...')
    inet_socket = generate_socket()
    print('Getting connection...')
    inet_socket.connect(connection_tuple)
    print('Making request...')
    inet_socket.send(request_bytes)

    print('Getting first results...')
    result_byte_count: int = inet_socket.recv_into(response_bytes, nbytes=RECV_SIZE)
    count = 0
    while result_byte_count > 0:
        result_byte_count = inet_socket.recv_into(response_bytes, nbytes=RECV_SIZE)
        print(f'Getting result set {count} of length {result_byte_count}')

    print('Shutting down connection...')
    inet_socket.shutdown()  # send FIN to peer
    inet_socket.close()  # deallocate socket

    return response_bytes


def main():
    print('pre-request')
    api_path = '/'
    response: bytearray = get(API_HOST, API_PORT, api_path)
    print(response)
    print('post-request')


if __name__ == '__main__':
    main()
