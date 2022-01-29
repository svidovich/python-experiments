from abc import ABC, abstractmethod


class ProcessingPlugin(ABC):
    def __init__(self, message_adapter, storage_adapter):
        self.message_adapter = message_adapter
        self.storage_adapter = storage_adapter

    @abstractmethod
    def process(self):
        raise NotImplemented()
