from abc import ABC, abstractmethod


# NOTE: The processing plugin should be decoupled from the message consumer
# and the storage adapter. All of them should essentially be generators that
# pipeline the data through.
class ProcessingPlugin(ABC):

    @abstractmethod
    def process(self):
        raise NotImplemented()
