import attr
import logging
import psycopg2

from abc import ABC, abstractmethod

from sqlalchemy import create_engine, MetaData, Table

from plugin import PluginOutput

logger = logging.getLogger(__name__)


@attr.s
class PGConnectionParams(object):
    host: str = attr.ib(kw_only=True, default='localhost')
    dbname: str = attr.ib(kw_only=True, default='postgres')
    username: str = attr.ib(kw_only=True)
    password: str = attr.ib(kw_only=True)
    port: int = attr.ib(kw_only=True, default=5432)


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