from email.message import Message
from plugin import TestPlugin
from messages import RabbitMessageAdapter, RabbitConnectionParams


def message_printer(message):
    while True:
        message = (yield)
        print(message)


def main():
    test_plugin = TestPlugin()
    rabbit_connection_params = RabbitConnectionParams(host="0.0.0.0",
                                                      queue_name="messages")

    message_adapter = RabbitMessageAdapter(rabbit_connection_params)

    message_adapter.pipeline_messages(
        test_plugin.processing_loop(target=message_printer))


if __name__ == '__main__':
    main()
