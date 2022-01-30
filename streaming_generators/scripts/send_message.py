import argparse
import pika


def recv_callback(ch, method, properties, body):
    print(f'Received: {body}')


def main():
    parser = argparse.ArgumentParser()
    # yapf: disable
    parser.add_argument('-q', '--queue-name', help='The name of the message queue')
    parser.add_argument('-m', '--message', help='The message to send to the queue')
    args = parser.parse_args()
    queue_name: str = args.queue_name
    message: str = args.message

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    # yapf: enable
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    print('Published message.')
    channel.close()


if __name__ == '__main__':
    main()
