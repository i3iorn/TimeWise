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
                Column("name"),
                Column("created_at")
            ]
        )
        tag_id = self.database.insert(table_name="groups", name="tag")
        category_id = self.database.insert(table_name="groups", name="category")
        settings_id = self.database.insert(table_name="groups", name="setting")
        custom_field_id = self.database.insert(table_name="groups", name="custom_field")

        # Create table for generic values
        self.database.create_table(
            table_name="timewise_values",
            columns=[
                Column("id", data_type="INTEGER", primary_key=True, auto_increment=True),
                Column("name"),
                Column("value"),
                Column("group_id", data_type="INTEGER"),
                Column("created_at"),
                Column("updated_at")
            ],
            unique_constraints=[UniqueConstraint(["name"])],
            foreign_keys=[ForeignKey("group_id", "groups", "id")]
        )

        # Set default priority min and max
        self.database.insert(table_name="timewise_values", name="priority_min", value="0", group_id=settings_id)
        self.database.insert(table_name="timewise_values", name="priority_max", value="5", group_id=settings_id)

        # Create views for tags, categories, and settings
        self.database.create_view("tags", table_name="timewise_values", conditions={"group_id": tag_id})
        self.database.create_view("categories", table_name="timewise_values", conditions={"group_id": category_id})
        self.database.create_view("settings", table_name="timewise_values", conditions={"group_id": settings_id})
        self.database.create_view("custom_fields", table_name="timewise_values", conditions={"group_id": custom_field_id})

        # Create table for tasks
        self.database.create_table(
            table_name="tasks",
            columns=[
                Column("id", data_type="INTEGER", primary_key=True, auto_increment=True),
                Column("name"),
                Column("description"),
                Column("category_id", data_type="INTEGER"),
                Column("priority", data_type="INTEGER"),
                Column("due_date"),
                Column("completed", data_type="INTEGER"),
                Column("created_at"),
                Column("updated_at")
            ],
            foreign_keys=[ForeignKey("category_id", "categories", "id")]
        )

        # Create table for task tags
        self.database.create_table(
            table_name="task_tags",
            columns=[
                Column("task_id", data_type="INTEGER"),
                Column("tag_id", data_type="INTEGER")
            ],
            foreign_keys=[
                ForeignKey("task_id", "tasks", "id"),
                ForeignKey("tag_id", "tags", "id")
            ],
            unique_constraints=[UniqueConstraint(["task_id", "tag_id"])]
        )

        # Create table for task custom fields
        self.database.create_table(
            table_name="task_custom_fields",
            columns=[
                Column("task_id", data_type="INTEGER"),
                Column("custom_field_id", data_type="INTEGER"),
                Column("value")
            ],
            foreign_keys=[
                ForeignKey("task_id", "tasks", "id"),
                ForeignKey("custom_field_id", "custom_fields", "id")
            ],
            unique_constraints=[UniqueConstraint(["task_id", "custom_field_id"])]
        )
