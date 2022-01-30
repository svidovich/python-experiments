import os

from plugin import TestPlugin
from messages import RabbitMessageAdapter, RabbitConnectionParams

RABBITMQ_HOST = os.environ['RABBITMQ_HOST']
MESSAGES_QUEUE = os.environ['MESSAGES_QUEUE']


def message_printer(message):
    while True:
        message = (yield)
        print(message)


def main():
    test_plugin = TestPlugin()
    rabbit_connection_params = RabbitConnectionParams(
        host=RABBITMQ_HOST, queue_name=MESSAGES_QUEUE)

    message_adapter = RabbitMessageAdapter(rabbit_connection_params)

    message_adapter.pipeline_messages(
        test_plugin.processing_loop(target=message_printer))


if __name__ == '__main__':
    main()
