class Response:

    def __init__(*args, **kwargs):
        pass


def parse_response_bytes(response_bytes: bytes) -> dict:
    split_bytes = response_bytes.decode('utf-8').split('\r\n')
    response_dictionary = dict()
    if len(split_bytes):

        response_info: str = split_bytes[0]
        response_info_split = response_info.split(' ')
        response_dictionary['protocol'] = response_info_split[0] or None
        response_dictionary['status_code'] = int(response_info_split[1])

        response_dictionary['user_agent'] = split_bytes[1] or None
        response_dictionary['response_date'] = split_bytes[2] or None
        response_dictionary['header'] = split_bytes[3]

        response_content_length = int(0)
        try:
            response_content_length: int = int(split_bytes[4].split(' ')[1])
        except Exception:
            pass
        response_dictionary['content_length'] = response_content_length
        unknown = split_bytes[5]  # Not sure what this is yet
        response_dictionary['response_body'] = split_bytes[6]

        print(response_dictionary)
