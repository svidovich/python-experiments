from utils import parse_response_bytes, Response
import unittest


class HTTPTestCase(unittest.TestCase):

    def test_parse_response_bytes(self):
        sample_response_bytes = b'HTTP/1.1 200 OK\r\nServer: Werkzeug/2.1.1 Python/3.10.4\r\nDate: Mon, 04 Apr 2022 03:00:02 GMT\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: 17\r\n\r\n{"sample":"data"}'
        output_response: Response = parse_response_bytes(sample_response_bytes)
        output_dictionary = output_response.asdict()
        expected_output = {
            'body': '{"sample":"data"}',
            'connection': None,
            'content_length': 17,
            'content_type': 'text/html; charset=utf-8',
            'date': 'Mon, 04 Apr 2022 03:00:02 GMT',
            'http_version': 'HTTP/1.1',
            'server': 'Werkzeug/2.1.1 Python/3.10.4',
            'status_code': 200
        }
        for key, value in expected_output.items():
            self.assertEqual(
                output_dictionary[key],
                value
            )



if __name__ == '__main__':
    unittest.main(verbosity=3)
