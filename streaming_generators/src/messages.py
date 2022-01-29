from abc import ABC, abstractmethod


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


class StorageAdapter(ABC):
    @abstractmethod
    def _connect(self):
        raise NotImplemented()

    def store_data(self, data):
        raise NotImplemented()