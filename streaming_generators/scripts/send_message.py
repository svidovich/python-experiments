import argparse
import pika


def recv_callback(ch, method, properties, body):
    print(f'Received: {body}')


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
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    if args.debug:
        print(f'Published message: {message}')
    connection.close()


if __name__ == '__main__':
    main()
