import logging
import sqlite3
from sqlite3 import Row, Cursor

from threading import Lock
from typing import Union, List, TYPE_CHECKING, _SpecialForm

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

    # Query execution
    def _execute(
        self,
        query: str,
        parameters: dict = None,
        commit: bool = True,
        fetch_method: str = None
    ) -> Union[Row, Cursor, List[Row], int, None]:
        """
        Execute a query on the database

        :param query: The query to execute
        :type query: str
        :param parameters: The parameters to pass to the query
        :type parameters: dict
        :param commit: Whether to commit the transaction
        :type commit: bool
        :param fetch_method: The fetch method to use
        :type fetch_method: str

        :raise sqlite3.Error: If the query execution fails

        :return: The result of the query
        :rtype: Union[sqlite3.Row, sqlite3.Cursor, List[sqlite3.Row], int, None]
        """
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

    def execute(self, query: "Query") -> Union[sqlite3.Row, sqlite3.Cursor, List[sqlite3.Row], int]:
        """
        Execute a query on the database using the Query object

        :param query: The Query object to execute
        :type query: Query

        :return: The result of the query
        :rtype: sqlite3.Cursor
        """
        return self._execute(query.query, query.parameters)

    def crud(self, fetch_method, **kwargs) -> Union[sqlite3.Row, sqlite3.Cursor, List[sqlite3.Row], int]:
        """
        Execute a CRUD operation on the database using the provided keyword arguments

        :param fetch_method: The fetch method to use
        :type fetch_method: str
        :param kwargs: The keyword arguments to pass to the CRUD operation
        :type kwargs: dict

        :return: The result of the CRUD operation
        :rtype: Union[sqlite3.Row, sqlite3.Cursor, List[sqlite3.Row], int]
        """
        query = Select(**kwargs)
        return self._execute(query.query, query.parameters, fetch_method=fetch_method)

    # CRUD operations
    def select(self, **kwargs) -> List["sqlite3.Row"]:
        """
        Select rows from the database

        :param kwargs: The keyword arguments to pass to the select operation
        :type kwargs: dict

        :return: The selected rows
        :rtype: List[sqlite3.Row]
        """
        return self.crud("fetchall", **kwargs)

    def select_one(self, **kwargs) -> "sqlite3.Row":
        """
        Select one row from the database

        :param kwargs: The keyword arguments to pass to the select operation
        :type kwargs: dict
        :return: The selected row
        :rtype: sqlite3.Row
        """
        return self.crud("fetchone", **kwargs)

    def insert(self, **kwargs) -> int:
        """
        Insert a row into the database

        :param kwargs: The keyword arguments to pass to the insert operation
        :type kwargs: dict
        :return: The last row id
        :rtype: int
        """
        return self.crud("lastrowid", **kwargs)

    def update(self, **kwargs) -> int:
        """
        Update a row in the database

        :param kwargs: The keyword arguments to pass to the update operation
        :type kwargs: dict
        :return: The number of rows updated
        :rtype: int
        """
        return self.crud("rowcount", **kwargs)

    def delete(self, **kwargs) -> int:
        """
        Delete a row from the database

        :param kwargs: The keyword arguments to pass to the delete operation
        :type kwargs: dict
        :return: The number of rows deleted
        :rtype: int
        """
        return self.crud("rowcount", **kwargs)

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
        return self._execute(query.query, query.parameters)

    def create_view(self, name: str, **kwargs) -> None:
        """
        Create a view in the database using the provided keyword arguments

        :param name: The name of the view
        :type name: str
        :param kwargs: The keyword arguments to pass to the create view operation
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        if not name:
            raise ValueError("View name must be provided and cannot be empty.")

        # Assuming 'can_exist' is an optional boolean parameter in kwargs
        can_exist = kwargs.pop('can_exist', False)
        view_existence_clause = "IF NOT EXISTS " if can_exist else ""
        filter = kwargs.pop("filter", None)

        # Construct the SELECT statement part of the view creation
        select_statement = Select(name=kwargs.pop("source"), **kwargs).with_parameters()

        # Construct the full CREATE VIEW statement
        create_view_statement = f"CREATE VIEW {view_existence_clause}{name} AS {select_statement}"
        if filter:
            create_view_statement += f" WHERE {filter}"

        try:
            self._execute(create_view_statement)
        except sqlite3.Error as e:
            # Handle specific database errors if needed
            raise RuntimeError(f"Failed to create view '{name}': {e}")

    def create_trigger(self, **kwargs) -> None:
        """
        Create a trigger in the database using the provided keyword arguments

        :param kwargs: The keyword arguments to pass to the create trigger operation
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        query = CreateTrigger(**kwargs)
        return self._execute(query.query, {})

    def show_tables(self) -> list:
        """
        Show all tables in the database

        :return: A list of all tables in the database
        :rtype: list
        """
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        return self._execute(query, fetch_method="fetchall")

    def show_views(self) -> list:
        """
        Show all views in the database

        :return: A list of all views in the database
        :rtype: list
        """
        query = "SELECT name FROM sqlite_master WHERE type='view';"
        return self._execute(query, fetch_method="fetchall")


class TimeWiseEngine(Engine):
    """
    TimeWiseEngine is a subclass of Engine that is responsible for managing the database connection for the TimeWise
    """
    def get_tasks(self):
        return self.select("tasks")
