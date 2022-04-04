import typing as T
from dataclasses import asdict, dataclass


@dataclass(frozen=True, kw_only=True)
class Response:
    protocol: str = None
    status_code: T.Optional[int] = None
    user_agent: str = None
    response_date: str = None
    header: str = None
    response_content_length: int = 0
    body: str = None

    def asdict(self):
        return asdict(self)


def parse_response_bytes(response_bytes: bytes) -> Response:
    split_bytes = response_bytes.decode('utf-8').split('\r\n')
    response_dictionary = dict()
    if len(split_bytes):

        response_info: str = split_bytes[0]
        response_info_split = response_info.split(' ')

        response_content_length = int(0)
        try:
            response_content_length: int = int(split_bytes[4].split(' ')[1])
        except Exception:
            pass

        return Response(protocol=response_info_split[0] or None,
                        status_code=int(response_info_split[1]),
                        user_agent=split_bytes[1] or None,
                        response_date=split_bytes[2] or None,
                        header=split_bytes[3],
                        response_content_length=response_content_length,
                        body=split_bytes[6])
