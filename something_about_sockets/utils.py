import json
import typing as T
from dataclasses import asdict, dataclass


@dataclass(kw_only=True)
class Response:
    body: str = None
    connection: str = None
    content_length: int = 0
    content_type: str = None
    date: str = None
    http_version: str = None
    server: str = None
    status_code: T.Optional[int] = None

    def asdict(self) -> dict:
        return asdict(self)
    
    def asJSON(self) -> str:
        return json.dumps(self.asdict())
    
    def __post_init__(self):
        self.status_code = int(self.status_code) if self.status_code else None
        self.content_length = int(self.content_length) if self.content_length else 0


HTTP_PREFIX_MAP = {
    'Connection: ': 'connection',
    'Content-Length: ': 'content_length',
    'Content-Type: ': 'content_type',
    'Date: ': 'date',
    'Server: ': 'server',
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
                response_dictionary['status_code'] = status_information[1]
            
            else:
                for prefix, key in HTTP_PREFIX_MAP.items():
                    if entry.startswith(prefix):
                        response_dictionary[key] = entry.removeprefix(prefix)

        return Response(**response_dictionary)
