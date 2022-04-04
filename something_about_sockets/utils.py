import typing as T
from dataclasses import asdict, dataclass


@dataclass(frozen=True, kw_only=True)
class Response:
    http_version: str = None
    status_code: T.Optional[int] = None
    server: str = None
    connection: str = None
    content_type: str = None
    date: str = None
    header: str = None
    content_length: int = 0
    body: str = None

    def asdict(self):
        return asdict(self)

HTTP_PREFIX_MAP = {
    'Server: ': 'server',
    'Date: ': 'date',
    'Content-Type: ': 'content_type',
    'Content-Length': 'content_length',
    'Connection: ': 'connection'
}

def parse_response_bytes(response_bytes: bytes) -> Response:
    split_bytes = response_bytes.decode('utf-8').split('\r\n')
    response_dictionary = dict()
    response_dictionary['body'] = split_bytes.pop()
    if len(split_bytes):
        for entry in split_bytes:
            if entry.startswith('HTTP/'):
                status_information = entry.split(' ')
                response_dictionary['http_version'] = status_information[0]
                response_dictionary['status_code'] = int(status_information[1])
            
            else:
                for prefix, key in HTTP_PREFIX_MAP.items():
                    if entry.startswith(prefix):
                        response_dictionary[key] = entry.removeprefix(prefix)

        return Response(**response_dictionary)
