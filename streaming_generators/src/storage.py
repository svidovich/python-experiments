import attr
import logging
import psycopg2

from abc import ABC, abstractmethod

from sqlalchemy import create_engine, MetaData, Table

from plugin import PluginOutput

logger = logging.getLogger(__name__)


@attr.s(kw_only=True, auto_attribs=True)
class ESConnectionParams(object):
    host: str = attr.ib()
    username: str = attr.ib(default='elastic')
    password: str = attr.ib()
    port: int = attr.ib(default=9200)


@attr.s(kw_only=True, auto_attribs=True)
class PGConnectionParams(object):
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


class ElasticSearchStorageAdapter(StorageAdapterBase):

    def __init__(self, connection_params: ESConnectionParams):
        self._connect(connection_params)

    def _connect(self, connection_params: ESConnectionParams) -> bool:
        return connection_params

    def store_data(self, plugin_output: PluginOutput):
        index_name: str = plugin_output.output_location
        print(plugin_output.output)