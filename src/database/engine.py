import json
import logging
import os
import sqlite3

from threading import Lock
from typing import Union, List, TYPE_CHECKING

from src.database.query_builder import Select, Insert, Update, Delete, CreateTable, Query, CreateTrigger

if TYPE_CHECKING:
    from src.config import Config

__all__ = ["TimeWiseEngine"]


logger = logging.getLogger(__name__)


class DatabaseConnection(sqlite3.Connection):
    def __init__(self, conf: "Config") -> None:
        self.conf = conf["Database"]
        self.db_path = self.conf["db_host"]
        super().__init__(self.db_path)
        self.row_factory = sqlite3.Row

    def __enter__(self):
        return self.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.close()
    

class Engine:
    """
    The Engine class is a singleton class that is responsible for managing the database connection. It is used to execute
    queries and CRUD operations on the database.

    It expects the database host as an environment variable.
    """
    def __init__(self, conf: "Config") -> None:
        self.dbc = DatabaseConnection(conf)
        self.lock = Lock()

        self._config = conf["Database"]
        self._setup_db()

    def _setup_db(self):
        for table in self._config["tables"].values():
            print(type(table), table)
            self.create_table(**table)

        for view in self._config["views"]:
            self.create_view(**view)

        for trigger in self._config["triggers"]:
            self.create_trigger(**trigger)

    # Query execution
    def _execute(
        self,
        query: str,
        parameters: dict = None,
        commit: bool = True,
        fetch_method: str = None
    ):
        with self.lock:
            try:
                if parameters:
                    self.dbc.execute(query, parameters)
                else:
                    self.dbc.execute(query)
            except sqlite3.Error as e:
                print(query)
                print(parameters)
                raise e

            if commit:
                self.dbc.commit()

            if fetch_method:
                fm = getattr(self.dbc.cursor, fetch_method)
                return fm()
            return None

    def execute(self, query: "Query") -> "sqlite3.Cursor":
        return self._execute(query.query, query.parameters)

    def crud(self, fetch_method, **kwargs) -> Union["sqlite3.Row", "sqlite3.Cursor", List["sqlite3.Row"], int]:
        query = Select(**kwargs)
        return self._execute(query.query, query.parameters, fetch_method=fetch_method)

    # CRUD operations
    def select(self, **kwargs) -> List["sqlite3.Row"]:
        return self.crud("fetchall", **kwargs)

    def select_one(self, **kwargs) -> "sqlite3.Row":
        return self.crud("fetchone", **kwargs)

    def insert(self, **kwargs) -> int:
        return self.crud("lastrowid", **kwargs)

    def update(self, **kwargs) -> int:
        return self.crud("rowcount", **kwargs)

    def delete(self, **kwargs) -> int:
        return self.crud("rowcount", **kwargs)

    # Table management
    def create_table(self, **kwargs) -> None:
        query = CreateTable(**kwargs)
        return self._execute(query.query, query.parameters)

    def create_view(self, view_name: str, **kwargs) -> None:
        if not view_name:
            raise ValueError("View name must be provided and cannot be empty.")

        # Assuming 'can_exist' is an optional boolean parameter in kwargs
        can_exist = kwargs.pop('can_exist', False)
        view_existence_clause = "IF NOT EXISTS " if can_exist else ""

        # Construct the SELECT statement part of the view creation
        select_statement = Select(**kwargs).with_parameters()

        # Construct the full CREATE VIEW statement
        create_view_statement = f"CREATE VIEW {view_existence_clause}{view_name} AS {select_statement}"

        try:
            self._execute(create_view_statement)
        except sqlite3.Error as e:
            # Handle specific database errors if needed
            raise RuntimeError(f"Failed to create view '{view_name}': {e}")

    def create_trigger(self, **kwargs) -> None:
        query = CreateTrigger(**kwargs)
        return self._execute(query.query, query.parameters)

    def show_tables(self) -> list:
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        return self._execute(query, fetch_method="fetchall")

    def show_views(self) -> list:
        query = "SELECT name FROM sqlite_master WHERE type='view';"
        return self._execute(query, fetch_method="fetchall")


class TimeWiseEngine(Engine):
    """
    TimeWiseEngine is a subclass of Engine that is responsible for managing the database connection for the TimeWise
    """
    def get_tasks(self):
        return self.select(table="tasks")
