import attr
import pika

from abc import ABC, abstractmethod
from pika import connection

from psycopg2 import connect


@attr.s
class RabbitConnectionParams(object):
    exchange: str = attr.ib(kw_only=True, default=str())
    queue_name: str = attr.ib(kw_only=True)
    host: str = attr.ib(kw_only=True, default='localhost')
    port: int = attr.ib(kw_only=True, default=5672)
    username: str = attr.ib(kw_only=True, default=str())
    password: str = attr.ib(kw_only=True, default=str())


class MessageAdapter(ABC):

    @abstractmethod
    def _connect(self):
        raise NotImplemented()

    @abstractmethod
    def receive_message(self):
        raise NotImplemented()

    @abstractmethod
    def send_message(self, message):
        raise NotImplemented()


class RabbitMessageAdapter(MessageAdapter):

    def __init__(self, connection_params: RabbitConnectionParams):
        self.connection_params = connection_params
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        connection_params = self.connection_params
        credentials = None
        if connection_params.username and connection_params.password:
            credentials = pika.PlainCredentials(connection_params.username,
                                                connection_params.password)

        pika_parameters = pika.ConnectionParameters(
            host=connection_params.host,
            port=connection_params.port,
            credentials=credentials)

        self.connection = pika.BlockingConnection(pika_parameters)
