import argparse
import json
import logging
import os
import typing as T
import uuid
from select import select
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from timer import Timer

from utils import Response as CustomResponse
from utils import parse_response_bytes

def args_from_env() -> dict:
    return {
        'API_HOST': os.environ.get("API_HOST"),
        'API_PORT': os.environ.get("API_PORT"),
    }

REQUEST_UA = "~socket experiment machine~"
RECV_SIZE = 1024
MAX_RECV_SIZE = 1024 * 1024 * 8
SOCK_CONNECTION_TIMEOUT = float(1)
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
    with Timer(f'Starting socket connection to {host}:{port}', debug=DEBUG_ENABLED):
        connection_tuple = (host, port)

        logger.debug('Generating socket...')
        inet_socket = generate_socket()
        logger.debug('Getting connection...')
        inet_socket.connect(connection_tuple)
        return inet_socket


def socket_disconnect(inet_socket: socket) -> None:
    with Timer('Shutting down connection...', debug=DEBUG_ENABLED):
        inet_socket.shutdown(SHUT_RDWR)  # send FIN to peer
        inet_socket.close()  # deallocate socket


def socket_rw(inet_socket: socket, request_bytes: bytes) -> bytes:
    response_bytes = bytes()
    _, write_sockets, _ = select(list(), [inet_socket], list(), SOCK_CONNECTION_TIMEOUT)

    if write_sockets:
        with Timer("Sending data", debug=DEBUG_ENABLED):
            inet_socket.send(request_bytes)

        # Now that we've sent data, we want to unblock our socket. That way, when we recv(n),
        # we don't just hang open until we receive something: we will bail off.
        inet_socket.setblocking(False)
        # Wait until our socket has something available to read manually.
        with Timer(f"Detecting response; timeout {SOCK_CONNECTION_TIMEOUT}", debug=DEBUG_ENABLED):
            read_sockets, _, _ = select([inet_socket], list(), list(), SOCK_CONNECTION_TIMEOUT)
        while True:
            if read_sockets:
                with Timer("Receiving bytes from socket", debug=DEBUG_ENABLED):
                    response_bytes += inet_socket.recv(RECV_SIZE)
                logger.debug(f"Response bytes increases size to {len(response_bytes)}")
                logger.debug(f"Response bytes: {response_bytes}")
                # Wait until our socket has something to read manually. If we don't find
                # something to read before SOCK_CONNECTION_TIMEOUT, we'll get an empty list
                # for 'read_sockets', causing us to bail out.
                read_sockets: T.List[T.Optional[socket]]
                with Timer("Checking for additional data from endpoint", debug=DEBUG_ENABLED):
                    read_sockets, _, _ = select([inet_socket], list(), list(), SOCKET_RECHECK_TIMEOUT)
            else:
                break

        return response_bytes


def http_method(inet_socket: socket, path: str, content: bytes, method_name: str, content_type: str = None) -> bytes:
    request_bytes: str = f"{method_name} {path} HTTP/1.1\r\n"
    request_bytes += f"User-Agent: {REQUEST_UA}\r\n"
    if content_type:
        request_bytes += f"Content-Type: {content_type}\r\n"
    request_bytes += f"Content-Length: {len(content) if content else 0}\r\n"
    request_bytes += "\r\n"
    request_bytes: bytes = request_bytes.encode()
    request_bytes += content or bytes()
    response_bytes = socket_rw(inet_socket=inet_socket, request_bytes=request_bytes)
    return response_bytes


def post(inet_socket: socket, path: str, content: bytes, content_type: str = None) -> bytes:
    return http_method(inet_socket=inet_socket, path=path, content=content, method_name='POST', content_type=content_type)


def get(inet_socket: socket, path: str) -> bytes:
    return http_method(inet_socket=inet_socket, path=path, content=None, method_name='GET', content_type=None)


def put(inet_socket: socket, path: str, content: bytes, content_type: str = None) -> bytes:
    return http_method(inet_socket=inet_socket, path=path, content=content, method_name='PUT', content_type=content_type)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--host', required=False, help='Host to hit with socket connection. Alternatively, set the API_HOST environment variable.')
    parser.add_argument('-p', '--port', required=False, type=int, help='Port on host. Alternatively, set the API_PORT environment variable.')
    parser.add_argument('-e', '--endpoint', required=False, default='/', help='The endpoint at the host to hit. Defaults to /.')
    parser.add_argument('-x', '--method', required=False, default='GET', choices=['GET', 'POST', 'PUT'], help='HTTP Method to use')
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
    elif args.method == 'POST':
        sample_post_content = bytes()
        response: bytes = post(inet_socket, api_path, sample_post_content)
    elif args.method == 'PUT':
        sample_put_content = bytes(f'id={uuid.uuid4()}'.encode())
        response: bytes = put(inet_socket, api_path, sample_put_content, content_type='application/x-www-form-urlencoded')
    else:
        raise NotImplemented(f"Method {args.method} is not implemented.")
    socket_disconnect(inet_socket=inet_socket)
    response: CustomResponse = parse_response_bytes(response)
    print(response.asJSON())



if __name__ == '__main__':
    main()
