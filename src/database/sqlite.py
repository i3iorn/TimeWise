import sqlite3

from .base import Database
from .query_builder import QueryBuilder


class SQLite(Database):
    def __init__(self, db_name: str):
        super().__init__(db_name)
        self._qb = QueryBuilder()
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        return True

    def disconnect(self):
        self.connection.commit()
        self.connection.close()
        return True
