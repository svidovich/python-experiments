import os
import time

from plugin import SimplePlugin
from messages import RabbitMessageAdapter, RabbitConnectionParams
from storage import ESConnectionParams, ElasticSearchStorageAdapter, PostgresStorageAdapter, PGConnectionParams
from utils import broadcast

DATABASE = os.environ["POSTGRES_DB"]
# TODO: Things that aren't secure for 1000, Alex.
DATABASE_USER = os.environ['PIPELINE_POSTGRES_USER']
DATABASE_PASSWORD = os.environ['PIPELINE_POSTGRES_PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']
# ---
MESSAGES_QUEUE = os.environ['MESSAGES_QUEUE']
RABBITMQ_HOST = os.environ['RABBITMQ_HOST']
# ---
ELASTIC_HOSTNAME = os.environ['ELASTIC_HOSTNAME']
ELASTIC_PASSWORD = os.environ['ELASTIC_PASSWORD']
ELASTIC_USERNAME = os.environ['ELASTIC_USERNAME']


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
    mq_connected = False
    while not mq_connected:
        try:
            message_adapter = RabbitMessageAdapter(rabbit_connection_params)
            mq_connected = True
        except:
            time.sleep(1)
            continue

    postgres_connection_params = PGConnectionParams(host=DATABASE_HOST,
                                                    dbname=DATABASE,
                                                    username=DATABASE_USER,
                                                    password=DATABASE_PASSWORD)
    pg_storage_adapter = PostgresStorageAdapter(postgres_connection_params)

    elasticsearch_connection_params = ESConnectionParams(host=ELASTIC_HOSTNAME,
                                                         username=ELASTIC_USERNAME,
                                                         password=ELASTIC_PASSWORD)
    es_storage_adapter = ElasticSearchStorageAdapter(elasticsearch_connection_params)

    # This explicitly pulls the generators so that we can cleanly broadcast to them below
    storage_adapter_streaming_loops = [
        message_printer(),
        pg_storage_adapter.stream_data_to_store(),
        es_storage_adapter.stream_data_to_store(),
    ]

    message_adapter.pipeline_messages(test_plugin.processing_loop(target=broadcast(storage_adapter_streaming_loops)))


if __name__ == '__main__':
    main()
