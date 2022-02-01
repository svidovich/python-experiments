import attr
import psycopg2

from abc import ABC, abstractmethod


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
                return True
            except Exception:
                return False


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

    def store_data(self, data: dict):
        # TODO: This would be prettier if we were passing a data class around
        table: str = data.pop('output_location', None)
        if table is not None:
            columns = list(table.keys())
            values = [data[column] for column in columns]

            sql_statement = f"insert into {table}({','.join(columns)} values ({','.join(values)}))"
            with self.connection.cursor() as cursor:
                cursor.execute(sql_statement)
