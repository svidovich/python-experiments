import attr
import time

from abc import ABC, abstractmethod
from typing import Any, Generator, List, Optional

from utils import prime_generator
from uuid import uuid4


@attr.s(kw_only=True, auto_attribs=True)
class PluginOutput(object):
    output_location: str = attr.ib(required=True)
    output: Any = attr.ib()


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
            output: PluginOutput = self.process(message)
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

    def process(self, message: dict) -> Optional[PluginOutput]:
        if self.schema.validate(message):
            message['message_id'] = str(uuid4())
            message['message_timestamp'] = int(time.time())
            # NOTE: In a more official environment, this would probably
            # be something on the class. At the very least, the storage
            # adapter downstream needs some way to know where we're meant
            # to put stuff.
            message['output_location'] = 'message_table'
            return PluginOutput(output_location='message_table', output=message)
        else:
            return None
