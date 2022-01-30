from abc import ABC, abstractmethod
from typing import Generator

from utils import prime_generator


# NOTE: The processing plugin should be decoupled from the message consumer
# and the storage adapter. All of them should essentially be generators that
# pipeline the data through.
class ProcessingPlugin(ABC):

    @abstractmethod
    def process(self, message):
        raise NotImplemented

    def processing_loop(self, target: Generator = None):
        while True:
            message = (yield)
            output = self.process(message)
            prime_generator(target)
            target.send(output)
