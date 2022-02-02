import attr
import psycopg2

from abc import ABC, abstractmethod
from plugin import PluginOutput
import logging

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
            self.connection = psycopg2.connect(dbname=connection_params.dbname,
                                               host=connection_params.host,
                                               user=connection_params.username,
                                               password=connection_params.password,
                                               port=connection_params.port)
            return True
        except Exception as e:
            print(f'An error occurred during connection to database: {e}')
            return False

    def store_data(self, data: PluginOutput):
        table = data.output_location
        data = data.output  # TODO: Stupid
        if table is not None:
            # TODO: Hackly. Be careful. Psycopg... really sucks, generally, lol.
            # This type of thing is why people use ORMs.
            columns = list(data.keys())
            values = ",".join([f"'{data[column]}'" for column in columns])

            sql_statement = f"insert into {table}({','.join(columns)}) values ({values})"
            with self.connection.cursor() as cursor:
                # TODO / NOTE: Generally, this isn't the pattern. We probably want
                # a queue / consumer kind of thing so we can insert lots at once.
                # For now, let's just get writing to a database.
                try:
                    cursor.execute(sql_statement)
                    self.connection.commit()
                except Exception as e:
                    logger.exception(e)
                    self.connection.rollback()
