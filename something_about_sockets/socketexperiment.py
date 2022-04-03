import logging
import os
from select import select
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from urllib import response

API_HOST = os.environ["API_HOST"]
API_PORT = int(os.environ["API_PORT"])

RECV_SIZE = 1024
MAX_RECV_SIZE = 1024 * 1024 * 8
SOCK_CONNECTION_TIMEOUT = float(10)
DEBUG_ENABLED = os.environ.get("DEBUG", False)
logging.basicConfig(level=logging.DEBUG if DEBUG_ENABLED else logging.INFO)
logger = logging.getLogger(__name__)


def generate_socket() -> socket:
    return socket(AF_INET, SOCK_STREAM)


def get(host: str, port: int, path: str) -> bytes:
    request_bytes: bytes = f"GET {path} HTTP/1.1\r\n\r\n".encode()
    response_bytes = bytes()
    connection_tuple = (host, port)

    logger.debug('Generating socket...')
    inet_socket = generate_socket()
    logger.debug('Getting connection...')
    inet_socket.connect(connection_tuple)
    _, write_sockets, _ = select(list(), [inet_socket], list(), SOCK_CONNECTION_TIMEOUT)

    if write_sockets:
        logger.debug('Making request...')
        inet_socket.send(request_bytes)

        # Now that we've sent data, we want to unblock our socket. That way, when we recv(n),
        # we don't just hang open until we receive something: we will bail off.
        inet_socket.setblocking(False)
        # Wait until our socket has something available to read manually.
        read_sockets, _, _ = select([inet_socket], list(), list(), SOCK_CONNECTION_TIMEOUT)
        while True:
            if read_sockets:
                response_bytes += inet_socket.recv(RECV_SIZE)
                logger.debug(f"Response bytes increases size to {len(response_bytes)}")
                logger.debug(f"Response bytes: {response_bytes}")
                # Wait until our socket has something to read manually. If we don't find
                # something to read before SOCK_CONNECTION_TIMEOUT, we'll get an empty list
                # for 'read_sockets', causing us to bail out.
                read_sockets, _, _ = select([inet_socket], list(), list(), SOCK_CONNECTION_TIMEOUT)
            else:
                break

        logger.debug('Shutting down connection...')
        inet_socket.shutdown(SHUT_RDWR)  # send FIN to peer
        inet_socket.close()  # deallocate socket

        return response_bytes


def main():
    logger.debug('pre-request')
    api_path = '/'
    response: bytes = get(API_HOST, API_PORT, api_path)
    logger.debug(response)
    logger.debug('post-request')


if __name__ == '__main__':
    main()
