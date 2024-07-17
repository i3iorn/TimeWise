import os
import sqlite3

from multiprocessing import Lock

from src.database.query_builder import Select, Insert, Update, Delete, CreateTable, Query, CreateTrigger

__all__ = ["Engine"]


class Engine:
    def __init__(self):
        self.connection, self.cursor = self.connect()
        self.lock = Lock()

    # Connection management
    def connect(self):
        conn = sqlite3.connect(os.environ.get("DB_HOST"))
        return conn, conn.cursor()

    def disconnect(self):
        self.connection.close()

    def __enter__(self):
        if not self.connection:
            self.connection, self.cursor = self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()
        return True

    # Query execution
    def _execute(
        self,
        query: str,
        parameters: dict = None,
        fetch: bool = False,
        fetchall: bool = False,
        lastrowid: bool = False,
        rowcount: bool = False,
        commit: bool = True
    ):
        with self.lock:
            try:
                if parameters:
                    self.cursor.execute(query, parameters)
                else:
                    self.cursor.execute(query)
            except sqlite3.Error as e:
                print(query)
                print(parameters)
                raise e

            if query.startswith("CREATE TABLE") and "update_at" in query:
                self.cursor.execute(CreateTrigger(
                    table_name=query.split(" ")[2],
                    trigger_name="update_at",
                    action="UPDATE",
                    timing="AFTER",
                    body=Update(
                        table_name=query.split(" ")[2],
                        columns={"updated_at": "CURRENT_TIMESTAMP"},
                        where={"id": "OLD.id"}
                    )).query
                )

            if commit:
                self.connection.commit()
            if fetch:
                return self.cursor.fetchone()
            if fetchall:
                return self.cursor.fetchall()
            if lastrowid:
                return self.cursor.lastrowid
            if rowcount:
                return self.cursor.rowcount

    def execute(self, query: "Query") -> "sqlite3.Cursor":
        return self._execute(query.query, query.parameters)

    # CRUD operations
    def select(self, **kwargs) -> list:
        query = Select(**kwargs)
        return self._execute(query.query, query.parameters, fetchall=True)

    def insert(self, **kwargs) -> int:
        query = Insert(**kwargs)
        return self._execute(query.query, query.parameters, lastrowid=True)

    def update(self, **kwargs) -> int:
        query = Update(**kwargs)
        return self._execute(query.query, query.parameters, rowcount=True)

    def delete(self, **kwargs) -> int:
        query = Delete(**kwargs)
        return self._execute(query.query, query.parameters, rowcount=True)

    # Table management
    def create_table(self, table_name, **kwargs) -> None:
        query = CreateTable(table_name=table_name, **kwargs)
        return self._execute(query.query, query.parameters)

    def create_view(self, view_name, **kwargs) -> None:
        self._execute(f"CREATE VIEW {'IF NOT EXISTS ' if kwargs.pop('can_exist') else ''}{view_name} AS {Select(**kwargs).with_parameters()}")

    def show_tables(self) -> list:
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        return self._execute(query, fetchall=True)
