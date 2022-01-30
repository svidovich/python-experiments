from email.generator import Generator
import attr
import pika

from abc import ABC, abstractmethod
from pika import connection
from psycopg2 import connect
from time import sleep
from typing import Any


@attr.s
class RabbitConnectionParams(object):
    exchange: str = attr.ib(kw_only=True, default=str())
    queue_name: str = attr.ib(kw_only=True)
    host: str = attr.ib(kw_only=True, default='localhost')
    port: int = attr.ib(kw_only=True, default=5672)
    username: str = attr.ib(kw_only=True, default=str())
    password: str = attr.ib(kw_only=True, default=str())


class MessageAdapter(ABC):
    # TODO We need some docs here
    @abstractmethod
    def _connect(self):
        raise NotImplemented()

    @abstractmethod
    def receive_message(self):
        raise NotImplemented()

    @abstractmethod
    def receive_messages(self):
        raise NotImplemented()

    def pipeline_messages(self):
        raise NotImplemented()

    @abstractmethod
    def send_message(self, message):
        raise NotImplemented()


POLL_INTERVAL = 1.0


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
        self.channel = self.connection.channel()

    def send_message(self, message: Any):
        self.channel.basic_publish(
            exchange=self.connection_params.exchange,
            routing_key=self.connection_params.queue_name,
            body=message)

    def receive_message(self):
        return self.channel.basic_get(queue=self.connection_params.queue_name,
                                      auto_ack=True)

    def receive_messages(self) -> Generator:
        while True:
            message = self.receive_message()
            if message is None:
                sleep(POLL_INTERVAL)
                continue

            yield message
