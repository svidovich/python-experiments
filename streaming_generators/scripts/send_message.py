import argparse
import pika


def recv_callback(ch, method, properties, body):
    print(f'Received: {body}')


def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-u', '--queue-url', help="Where to send your message")
    # parser.add_agument('-m', '--message', help="The message to send")
    args = parser.parse_args()
    # yapf: disable
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    # yapf: enable
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key='messages', body='Yeehaw')
    print('Published message.')

    channel.basic_consume(queue='messages',
                          auto_ack=True,
                          on_message_callback=recv_callback)

    print('Consuming...')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.close()
        exit(0)


if __name__ == '__main__':
    main()
