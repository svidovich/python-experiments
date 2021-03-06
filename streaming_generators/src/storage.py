import attr
import logging
import time

from abc import ABC, abstractmethod

from elasticsearch import Elasticsearch
from sqlalchemy import create_engine, MetaData, Table

from plugin import PluginOutput
from utils import coroutine

logger = logging.getLogger(__name__)


@attr.s
class StorageConnectionParams(object):

    @property
    def asdict(self):
        return attr.asdict(self)


@attr.s(kw_only=True, auto_attribs=True)
class ESConnectionParams(StorageConnectionParams):
    host: str = attr.ib()
    username: str = attr.ib(default='elastic')
    password: str = attr.ib()
    port: int = attr.ib(default=9200)


@attr.s(kw_only=True, auto_attribs=True)
class PGConnectionParams(StorageConnectionParams):
    host: str = attr.ib(default='localhost')
    dbname: str = attr.ib(default='postgres')
    username: str = attr.ib()
    password: str = attr.ib()
    port: int = attr.ib(default=5432)


class StorageAdapterBase(ABC):

    @abstractmethod
    def _connect(self):
        raise NotImplemented()

    @abstractmethod
    def store_data(self, data):
        raise NotImplemented()

    @coroutine
    def stream_data_to_store(self) -> bool:
        while True:
            try:
                data = (yield)
                self.store_data(data)
            except Exception as e:
                logger.exception(e)


class PostgresStorageAdapter(StorageAdapterBase):

    def __init__(self, connection_params: PGConnectionParams):
        self._connect(connection_params)

    def _connect(self, connection_params: PGConnectionParams) -> bool:
        try:
            postgres_connection_string = f'postgresql+psycopg2://{connection_params.username}:{connection_params.password}@{connection_params.host}:{connection_params.port}/{connection_params.dbname}'
            self.engine = create_engine(postgres_connection_string, echo=True)
            self.connection = self.engine.connect()
            return True
        except Exception as e:
            print(f'An error occurred during connection to database: {e}')
            return False

    def store_data(self, plugin_output: PluginOutput):
        table_name = plugin_output.output_location
        if table_name in self.engine.table_names():
            metadata = MetaData(bind=None)
            table = Table(table_name, metadata, autoload=True, autoload_with=self.engine)
            statement = table.insert().values(**plugin_output.output)
            self.connection.execute(statement)
        else:
            raise Exception(f"{table_name} is not a relation on database {self.engine.url.database}")


ES_CONNECTION_POLL_TIME = 2
ES_MAX_CONNECTION_ATTEMPTS = 20


class ElasticSearchStorageAdapter(StorageAdapterBase):

    def __init__(self, connection_params: ESConnectionParams):
        self._connect(connection_params)

    def _connect(self, connection_params: ESConnectionParams) -> bool:
        print('-' * 50)
        print(f'Attempting connection to ES with the following parameters:')
        print(connection_params.asdict)
        print('-' * 50)

        connection_attempts = 0
        while connection_attempts < ES_MAX_CONNECTION_ATTEMPTS:
            try:
                self.connection = Elasticsearch(
                    [connection_params.host],  # NOTE: Only one host: in cluster mode there can be more
                    port=connection_params.port,
                    scheme='http',
                    http_auth=(connection_params.username, connection_params.password))
                output = self.connection.cluster.health()
                print(f'Connection successful! ES Cluster Health: {output}')  # TODO: Loggerfy
                break
            except:
                connection_attempts += 1
                print(f'Failed connecting to ElasticSearch. Trying again in {ES_CONNECTION_POLL_TIME} second(s).')
                time.sleep(ES_CONNECTION_POLL_TIME)
                continue
        if not self.connection:
            raise Exception(f'{type(self).__name__}: Failed to connect to destination storage')

    def store_data(self, plugin_output: PluginOutput):
        index_name: str = plugin_output.output_location
        if not self.connection.indices.exists(index=index_name):
            print(f'{type(self).__name__}:')
            print(f'No such index {index_name}: creating a new one...')
            self.connection.indices.create(index=index_name, ignore=400)
        self.connection.index(index=index_name, body=plugin_output.output)