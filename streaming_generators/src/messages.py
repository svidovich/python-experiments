import attr
import pika
import json
from utils import prime_generator

from abc import ABC, abstractmethod
from time import sleep
from typing import Any, Generator, Tuple, Union

from constants import PIKA_NULL_MESSAGE, POLL_INTERVAL


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
    def _connect(self) -> None:
        """
        Implementation guide:
        Using any necessary business logic, connect to your message source.
        Mutate class as necessary to make connection state available to other
        instance methods.
        """
        raise NotImplemented()

    @abstractmethod
    def receive_message(self) -> Any:
        """
        Implementation guide:
        Using any necessary business logic, retrieve a single message from
        your message source, and return it.
        """
        raise NotImplemented()

    @abstractmethod
    def receive_messages(self) -> Generator:
        """
        Implementation guide:
        Using the receive_message method, poll the message source and yield
        messages as they become available.
        """
        raise NotImplemented()

    def pipeline_messages(self, target: Generator) -> None:
        """
        Implementation guide:
        Using the generator provided by receive_messages, send those messages
        to another generator, given as the 'target' argument to this method.
        """
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

    def _connect(self) -> None:
        """
        Attempts to connect to a RabbitMQ queue. If credentials are provided
        via the RabbitConnectionParams, use those; otherwise, don't use any.
        Mutates adapter state: Sets channel and connection on instance; these
        are used by receive_message and thus other down-streams.
        """
        connection_params = self.connection_params

        # yapf: disable
        pika_parameters = None
        if connection_params.username and connection_params.password:
            credentials = pika.PlainCredentials(
                connection_params.username or str(),
                connection_params.password or str())

            pika_parameters = pika.ConnectionParameters(
                host=connection_params.host,
                port=connection_params.port,
                credentials=credentials)
        else:
            pika_parameters = pika.ConnectionParameters(
                host=connection_params.host,
                port=connection_params.port
            )
        # yapf: enable

        self.connection = pika.BlockingConnection(pika_parameters)
        self.channel = self.connection.channel()

    def basic_json_deserialize(self, message: bytes) -> Union[bytes, dict, list]:
        """
        Takes a message received from RabbitMQ and tries to deserialize it as JSON.
        If it's successful, returns the deserialized JSON; otherwise, returns the message.
        """
        try:
            return json.loads(message)
        except:
            return message

    def send_message(self, message: Any):
        """
        Sends a message to a RabbitMQ Queue.
        """
        self.channel.basic_publish(exchange=self.connection_params.exchange,
                                   routing_key=self.connection_params.queue_name,
                                   body=message)

    def receive_message(self) -> Tuple:
        """
        Retrieves a message from a RabbitMQ queue. Successful or not, returns what comes
        back from the queue. In the case that there's nothing to retrieve, returns a tuple
        like (None, None, None).
        """
        return self.channel.basic_get(queue=self.connection_params.queue_name, auto_ack=True)

    def receive_messages(self, poll_interval: float = POLL_INTERVAL) -> Generator:
        """
        A polling loop that yields messages from a RabbitMQ queue.
        TODOs:
            - Add error handling around status from message; ideally I don't
              think pipeline_messages needs to think about that.
        """
        while True:
            message = self.receive_message()
            if message == PIKA_NULL_MESSAGE:
                sleep(POLL_INTERVAL)
                continue

            yield message

    def pipeline_messages(self, target: Generator) -> None:
        for message in self.receive_messages():
            # TODO / NOTE, FUTURE: We can probably act on the status & properties
            # so that we can refuse to send if the status was bad, etc. We should
            # probably do that lower, in receive_messages or receive_message.
            status, properties, message_content = message
            message_content = self.basic_json_deserialize(message_content)
            prime_generator(target)
            target.send(message_content)
