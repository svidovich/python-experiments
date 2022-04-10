import argparse
import logging
import os
import typing as T
from select import select
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from timer import Timer
from urllib import response

def args_from_env() -> dict:
    return {
        'API_HOST': os.environ.get("API_HOST"),
        'API_PORT': os.environ.get("API_PORT"),
    }

REQUEST_UA = "~socket experiment machine~"
RECV_SIZE = 1024
MAX_RECV_SIZE = 1024 * 1024 * 8
SOCK_CONNECTION_TIMEOUT = float(10)
# After we read from the socket for the first time, we should go back to the socket
# and check to see if there's any additional data. This variable controls how long
# we wait for that data to show up before we straight up bail out.
SOCKET_RECHECK_TIMEOUT = float(0.0)
DEBUG_ENABLED = os.environ.get("DEBUG", False)
logging.basicConfig(level=logging.DEBUG if DEBUG_ENABLED else logging.INFO)
logger = logging.getLogger(__name__)


def generate_socket() -> socket:
    return socket(AF_INET, SOCK_STREAM)


def socket_connect(inet_socket: socket, host: str, port: int) -> socket:
    with Timer(f'Starting socket connection to {host}:{port}'):
        connection_tuple = (host, port)

        logger.debug('Generating socket...')
        inet_socket = generate_socket()
        logger.debug('Getting connection...')
        inet_socket.connect(connection_tuple)
        return inet_socket

def socket_disconnect(inet_socket: socket) -> None:
    with Timer('Shutting down connection...'):
        inet_socket.shutdown(SHUT_RDWR)  # send FIN to peer
        inet_socket.close()  # deallocate socket


def get(inet_socket: socket, path: str) -> bytes:
    request_bytes: bytes = f"GET {path} HTTP/1.1\r\n\r\n".encode()
    response_bytes = bytes()

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
                with Timer("Receiving bytes from socket"):
                    response_bytes += inet_socket.recv(RECV_SIZE)
                logger.debug(f"Response bytes increases size to {len(response_bytes)}")
                logger.debug(f"Response bytes: {response_bytes}")
                # Wait until our socket has something to read manually. If we don't find
                # something to read before SOCK_CONNECTION_TIMEOUT, we'll get an empty list
                # for 'read_sockets', causing us to bail out.
                read_sockets: T.List[T.Optional[socket]]
                with Timer("Checking for additional data from endpoint"):
                    read_sockets, _, _ = select([inet_socket], list(), list(), SOCKET_RECHECK_TIMEOUT)
            else:
                break

        return response_bytes

def post(inet_socket: socket, path: str, content: bytes, content_type: str = None) -> bytes:
    request_bytes: str = f"POST {path} HTTP/1.1\r\n"
    request_bytes += f"User-Agent: {REQUEST_UA}\r\n"
    request_bytes += f"Content-Length: {len(content)}\r\n"
    if content_type:
        request_bytes += f"Content-Type: {content_type}\r\n"
    request_bytes: bytes = request_bytes.encode()
    request_bytes += content
    response_bytes = bytes()

    _, write_sockets, _ = select(list(), [inet_socket], list(), SOCK_CONNECTION_TIMEOUT)

    if write_sockets:
        logger.debug('Making request...')
        inet_socket.send(request_bytes)

        inet_socket.setblocking(False)
        read_sockets, _, _ = select([inet_socket], list(), list(), SOCK_CONNECTION_TIMEOUT)
        while True:
            if read_sockets:
                with Timer("Receiving bytes from socket"):
                    response_bytes += inet_socket.recv(RECV_SIZE)
                logger.debug(f"Response bytes increases size to {len(response_bytes)}")
                logger.debug(f"Response bytes: {response_bytes}")
                read_sockets: T.List[T.Optional[socket]]
                with Timer("Checking for additional data from endpoint"):
                    read_sockets, _, _ = select([inet_socket], list(), list(), SOCKET_RECHECK_TIMEOUT)
            else:
                break

        return response_bytes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--host', required=False, help='Host to hit with socket connection. Alternatively, set the API_HOST environment variable.')
    parser.add_argument('-p', '--port', required=False, type=int, help='Port on host. Alternatively, set the API_PORT environment variable.')
    parser.add_argument('-e', '--endpoint', required=False, default='/', help='The endpoint at the host to hit. Defaults to /.')
    parser.add_argument('-x', '--method', required=False, default='GET', choices=['GET', 'POST'], help='HTTP Method to use')
    args = parser.parse_args()

    api_host = args.host
    api_port = args.port
    if not any({api_host, api_port}):
        env_args: dict = args_from_env()
        if not all(value for value in env_args.values()):
            raise RuntimeError("You need to provide host and port, either through environment or as arguments to the script.")
        
        api_host = env_args['API_HOST']
        api_port = env_args['API_PORT']

    api_port = int(api_port)

    api_path = args.endpoint
    inet_socket: socket = socket_connect(generate_socket(), api_host, api_port)
    if args.method == 'GET':
        response: bytes = get(inet_socket, api_path)
    if args.method == 'POST':
        sample_post_content = bytes()
        response: bytes = post(inet_socket, api_path, sample_post_content)
    socket_disconnect(inet_socket=inet_socket)
    logger.debug(response)



if __name__ == '__main__':
    main()
