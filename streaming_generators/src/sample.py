import os
import time

from plugin import SimplePlugin
from messages import RabbitMessageAdapter, RabbitConnectionParams

RABBITMQ_HOST = os.environ['RABBITMQ_HOST']
MESSAGES_QUEUE = os.environ['MESSAGES_QUEUE']


def message_printer():
    while True:
        message = (yield)
        if message is not None:
            print(message)
        else:
            print('Message is None.')


def main():
    test_plugin = SimplePlugin()
    rabbit_connection_params = RabbitConnectionParams(host=RABBITMQ_HOST, queue_name=MESSAGES_QUEUE)

    # TODO: This is a hack to essentially let me await rabbit being up.
    # There's a cool way to do this with docker-compose itself, but we
    # can think about that later.
    connected = False
    while not connected:
        try:
            message_adapter = RabbitMessageAdapter(rabbit_connection_params)
            connected = True
        except:
            time.sleep(1)
            continue

    message_adapter.pipeline_messages(test_plugin.processing_loop(target=message_printer()))


if __name__ == '__main__':
    main()
