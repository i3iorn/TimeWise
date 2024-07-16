from .database.engine import Engine as Database
from .database.query_builder import Column, ForeignKey, UniqueConstraint
from .secrets_manager import SecretsManager


class TimeWise:
    """
    TimeWise class is the main class for the TimeWise application. It is a singleton class that is responsible for
    managing the entire application.

    It expects a database instance of type Database and a secrets_manager instance of type SecretsManager. Also the
    environment variable dictionary.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, database: Database, secrets_manager: SecretsManager):
        self.database = database
        self.secrets_manager = secrets_manager

        self._create_tables()

    def _create_tables(self):
        # Create table for allowed value groups and add default values
        self.database.create_table(
            table_name="groups",
            columns=[
                Column("id", data_type="INTEGER", primary_key=True, auto_increment=True),
                Column("name", primary_key=True),
                Column("created_at")
            ]
        )
        self.database.insert(table_name="groups", name="tags")
        self.database.insert(table_name="groups", name="category")

        # Create table for generic values
        self.database.create_table(
            table_name="timewise_values",
            columns=[
                Column("id", data_type="INTEGER", primary_key=True, auto_increment=True),
                Column("name"),
                Column("value"),
                Column("group"),
                Column("created_at"),
                Column("updated_at")
            ],
            unique_constraints=[UniqueConstraint(["name"])],
            foreign_keys=[ForeignKey("group_id", "groups", "id")]
        )

        # Set default priority min and max
        self.database.insert(table_name="timewise_values", name="priority_min", value="0", type="int")
        self.database.insert(table_name="timewise_values", name="priority_max", value="5", type="int")

        # Create table for tasks
        self.database.create_table(
            table_name="tasks",
            columns=[
                Column("id", data_type="INTEGER", primary_key=True, auto_increment=True),
                Column("name"),
                Column("description"),
                Column("category_id", data_type="INTEGER"),
                Column("priority", data_type="INTEGER"),
                Column("due_date", data_type="TEXT"),
                Column("completed", data_type="INTEGER"),
                Column("created_at"),
                Column("updated_at")
            ],
            foreign_keys=[ForeignKey("category_id", "categories", "id")]
        )
