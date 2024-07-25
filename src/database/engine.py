import logging
import sqlite3
from sqlite3 import Row, Cursor

from threading import Lock
from typing import Union, List, TYPE_CHECKING

from src.components.base import Dict
from src.config import ConfigFlag
from src.database.query_builder import Select, Insert, Update, Delete, CreateTable, Query, CreateTrigger

if TYPE_CHECKING:
    from src.config import Config

__all__ = ["TimeWiseEngine"]


logger = logging.getLogger(__name__)


class DatabaseConnection(sqlite3.Connection):
    """
    DatabaseConnection is a subclass of sqlite3.Connection that is responsible for managing the database connection.
    It is used to execute queries and CRUD operations on the database.

    It expects the database host as an environment variable.
    """
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
        self.cursor = self.dbc.cursor()
        self.lock = Lock()

        self._config = conf["Database"]
        self._setup_db()

    def _setup_db(self):
        for table in self._config["tables"].values():
            self.create_table(**table)

        for view in self._config["views"]:
            self.create_view(**view)

        if "triggers" in self._config:
            for trigger in self._config["triggers"]:
                self.create_trigger(**trigger)

        if "initial_values" in self._config:
            for table, values in self._config["initial_values"].items():
                for value in values:
                    self.insert(table_name=table, **value)

        print(self.select(table_name="groups"))
        print(self.select(table_name="timewise_values"))

    def execute(self, query: "Query") -> Cursor:
        """
        Execute a query on the database using the Query object

        :param query: The Query object to execute
        :type query: Query

        :return: The result of the query
        :rtype: sqlite3.Cursor
        """
        print(query.with_parameters())
        return self.cursor.execute(query.query, query.parameters)

    def crud(self, crud_type, **kwargs) -> Union[sqlite3.Row, sqlite3.Cursor, List[sqlite3.Row], int]:
        """
        Execute a CRUD operation on the database using the provided keyword arguments

        :param crud_type: The CRUD operation to execute
        :type crud_type: class
        :param kwargs: The keyword arguments to pass to the CRUD operation
        :type kwargs: dict

        :return: The result of the CRUD operation
        :rtype: Union[sqlite3.Row, sqlite3.Cursor, List[sqlite3.Row], int]
        """
        query = crud_type(**kwargs)
        return self.execute(query)

    # CRUD operations
    def select(self, **kwargs) -> List[Dict]:
        """
        Select rows from the database

        :param kwargs: The keyword arguments to pass to the select operation
        :type kwargs: dict

        :return: The selected rows
        :rtype: List[Dict]
        """
        table = kwargs.get("table_name")
        column_names = {
            i: row[1] for i, row in enumerate(self.cursor.execute(f"PRAGMA table_info({table});").fetchall())
        }
        if not column_names:
            column_names = {
                i: row[1] for i, row in enumerate(self.cursor.execute(f"PRAGMA pragma_view_info({table});").fetchall())
            }

        results = self.crud(Select, **kwargs).fetchall()
        return [Dict({column_names[i]: val for i, val in enumerate(row)}) for row in results]

    def select_one(self, **kwargs) -> Dict:
        """
        Select one row from the database

        :param kwargs: The keyword arguments to pass to the select operation
        :type kwargs: dict
        :return: The selected row
        :rtype: Dict
        """
        return self.select(**kwargs)[0]

    def insert(self, **kwargs) -> int:
        """
        Insert a row into the database

        :param kwargs: The keyword arguments to pass to the insert operation
        :type kwargs: dict
        :return: The last row id
        :rtype: int
        """
        return self.crud(Insert, **kwargs).lastrowid

    def update(self, **kwargs) -> int:
        """
        Update a row in the database

        :param kwargs: The keyword arguments to pass to the update operation
        :type kwargs: dict
        :return: The number of rows updated
        :rtype: int
        """
        return self.crud(Update, **kwargs).rowcount

    def delete(self, **kwargs) -> int:
        """
        Delete a row from the database

        :param kwargs: The keyword arguments to pass to the delete operation
        :type kwargs: dict
        :return: The number of rows deleted
        :rtype: int
        """
        return self.crud(Delete, **kwargs).rowcount

    # Table management
    def create_table(self, **kwargs) -> None:
        """
        Create a table in the database using the provided keyword arguments

        :param kwargs: The keyword arguments to pass to the create table operation
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        query = CreateTable(**kwargs)
        self.execute(query)

    def create_view(self, view_name: str, **kwargs) -> None:
        """
        Create a view in the database using the provided keyword arguments

        :param table: The name of the view
        :type view_name: str
        :param kwargs: The keyword arguments to pass to the create view operation
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        if not view_name:
            raise ValueError("View name must be provided and cannot be empty.")

        # Assuming 'can_exist' is an optional boolean parameter in kwargs
        can_exist = kwargs.pop('can_exist', False)
        view_existence_clause = "IF NOT EXISTS " if can_exist else ""
        filter = kwargs.pop("filter", None)

        # Construct the SELECT statement part of the view creation
        select_statement = Select(table_name=kwargs.pop("source"), **kwargs).with_parameters()

        # Construct the full CREATE VIEW statement
        create_view_statement = f"CREATE VIEW {view_existence_clause}{view_name} AS {select_statement}"
        if filter:
            create_view_statement += f" WHERE {filter}"
        create_view_statement += ";"

        try:
            self.dbc.execute(create_view_statement)
        except sqlite3.Error as e:
            # Handle specific database errors if needed
            raise RuntimeError(f"Failed to create view '{view_name}': {e}")

    def create_trigger(self, **kwargs) -> None:
        """
        Create a trigger in the database using the provided keyword arguments

        :param kwargs: The keyword arguments to pass to the create trigger operation
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        query = CreateTrigger(**kwargs)
        self.dbc.execute(query.query)

    def show_tables(self) -> list:
        """
        Show all tables in the database

        :return: A list of all tables in the database
        :rtype: list
        """
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        return self.dbc.execute(query).fetchall()

    def show_views(self) -> list:
        """
        Show all views in the database

        :return: A list of all views in the database
        :rtype: list
        """
        query = "SELECT name FROM sqlite_master WHERE type='view';"
        return self.dbc.execute(query).fetchall()

    def __getattr__(self, item):
        if item.startswith("get_"):
            attribute = item[4:]
            items = self.select(table_name=attribute)
            print(items)
            return items
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")


class TimeWiseEngine(Engine):
    """
    TimeWiseEngine is a subclass of Engine that is responsible for managing the database connection for the TimeWise
    """
    pass
