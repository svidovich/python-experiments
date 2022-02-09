import argparse
import pika
from pika.adapters.blocking_connection import BlockingChannel


def recv_callback(ch, method, properties, body):
    print(f'Received: {body}')


def send_message(queue_name: str, message_body: str, channel: BlockingChannel):
    channel.basic_publish(exchange='', routing_key=queue_name, body=message_body)


def main():
    parser = argparse.ArgumentParser()
    # yapf: disable
    parser.add_argument('-q', '--queue-name', required=True, help='The name of the message queue')
    parser.add_argument('-m', '--message', required=True, help='The message to send to the queue')
    parser.add_argument('-d', '--debug', required=False, action='store_true', help='Debug logging switch')
    args = parser.parse_args()
    queue_name: str = args.queue_name
    message: str = args.message

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    # yapf: enable
    channel: BlockingChannel = connection.channel()
    send_message(queue_name=queue_name, message_body=message, channel=channel)
    if args.debug:
        print(f'Published message: {message}')
    connection.close()


if __name__ == '__main__':
    main()
