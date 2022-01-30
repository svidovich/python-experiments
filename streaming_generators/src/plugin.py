import attr
import time

from abc import ABC, abstractmethod
from typing import Generator, List, Optional

from utils import prime_generator
from uuid import uuid4


# NOTE: The processing plugin should be decoupled from the message consumer
# and the storage adapter. All of them should essentially be generators that
# pipeline the data through.
class ProcessingPlugin(ABC):

    @abstractmethod
    def process(self, message):
        raise NotImplemented

    def processing_loop(self, target: Generator):
        while True:
            message = (yield)
            output = self.process(message)
            prime_generator(target)
            target.send(output)


# TODO There's a right way to do this, let's google it later
class SimpleMessageSchema(object):

    def __init__(self):
        self.fields = {'message_body'}

    def validate(self, message: dict) -> bool:
        return True if len(self.fields.intersection(set(message.keys()))) == len(self.fields) else False


class SimplePlugin(ProcessingPlugin):

    def __init__(self):
        self.schema = SimpleMessageSchema()

    def process(self, message: dict) -> Optional[dict]:
        if self.schema.validate(message):
            message['processing_id'] = str(uuid4())
            message['timestamp'] = int(time.time())
            return message
        else:
            return None
