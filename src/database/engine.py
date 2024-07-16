import os
import sqlite3

from src.database.query_builder import Select, Insert, Update, Delete, CreateTable


__all__ = ["Engine"]


class Engine:
    def __init__(self):
        self.connection, self.cursor = self.connect()

    # Connection management
    def connect(self):
        conn = sqlite3.connect(os.environ.get("DB_HOST"))
        return conn, conn.cursor()

    def disconnect(self):
        self.connection.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()
        return True

    # Query execution
    def _execute(self, query: str, parameters: dict = None):
        if parameters:
            self.cursor.execute(query, parameters)
        else:
            self.cursor.execute(query)
        self.connection.commit()
        return self.cursor.fetchall()

    # CRUD operations
    def select(self, **kwargs):
        query = Select(**kwargs)
        return self._execute(query.query, query.parameters)

    def insert(self, **kwargs):
        query = Insert(**kwargs)
        return self._execute(query.query, query.parameters)

    def update(self, **kwargs):
        query = Update(**kwargs)
        return self._execute(query.query, query.parameters)

    def delete(self, **kwargs):
        query = Delete(**kwargs)
        return self._execute(query.query, query.parameters)

    # Table management
    def create_table(self, table_name, **kwargs):
        query = CreateTable(table_name=table_name, **kwargs)
        return self._execute(query.query, query.parameters)

    def show_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        return self._execute(query)
