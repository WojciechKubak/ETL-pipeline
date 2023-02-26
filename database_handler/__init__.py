from typing import Any, Self

from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from dotenv import load_dotenv
import os


class SingletonMeta(type):
    _instances = {}

    def __call__(cls: Self, *args: Any, **kwargs: Any) -> Self:
        if cls not in cls._instances:
            instance = cls.super().__init__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    

class EnvironmentVariableReader:
    def __init__(self, variable_name: str) -> None:
        self.variable_name = variable_name

    def read(self) -> str:
        load_dotenv()
        return os.getenv(self.variable_name, '')
    

class DatabaseManager(metaclass=SingletonMeta):
    def __init__(self, connection_url: str = None) -> None:
        self.connection_url = connection_url
        self._engine: Engine = None
        self._engine_initialized = False
        if not self.connection_url:
            raise ValueError('Connection string cannot be empty.')

    @property
    def engine(self) -> Engine:
        if not self._engine_initialized:
            self.build_engine()
        return self._engine

    def build_engine(self) -> None:
        if not self.connection_url:
            raise ValueError('Connection string cannot be empty.')
        try:
            self._engine = create_engine(self.connection_url, echo=False)
            self._engine_initialized = True
        except SQLAlchemyError as err:
            raise ValueError(f'Error occurred while building engine: {err}.')

    def test_connection(self) -> None:
        if not self._engine_initialized:
            self.build_engine()

        conn = None
        try:
            with self._engine.connect() as conn:
                conn.execute('SELECT 1')
        except SQLAlchemyError as err:
            raise ValueError(f'Error occurred: {err}.')
        finally:
            if conn:
                conn.close()

    @classmethod
    def from_connection_url(cls: Self, connection_url: str) -> Self:
        dbm = cls(connection_url)
        dbm.build_engine()
        dbm.test_connection()
        return dbm
    
    @classmethod
    def from_environment_variable(cls: Self, env_reader: EnvironmentVariableReader) -> Self:
        connection_url = env_reader.read()
        dbm = cls(connection_url)
        dbm.build_engine()
        dbm.test_connection()
        return dbm