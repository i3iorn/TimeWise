from .database.engine import Engine as Database
from .database.query_builder import Column, ForeignKey, UniqueConstraint, CheckConstraint
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
            ],
            can_exist=True,
            unique_constraints=[UniqueConstraint(["name"])]
        )
        tag_id = (
            self.database.insert(table_name="groups", name="tag", drop_duplicate=True) or
            self.database.select(table_name="groups", conditions={"name": "tag"}, columns=["id"])[0][0]
        )
        category_id = (
            self.database.insert(table_name="groups", name="category", drop_duplicate=True) or
            self.database.select(table_name="groups", conditions={"name": "category"}, columns=["id"])[0][0]
        )
        settings_id = (
            self.database.insert(table_name="groups", name="setting", drop_duplicate=True) or
            self.database.select(table_name="groups", conditions={"name": "setting"}, columns=["id"])[0][0]
        )
        custom_field_id = (
            self.database.insert(table_name="groups", name="custom_field", drop_duplicate=True) or
            self.database.select(table_name="groups", conditions={"name": "custom_field"}, columns=["id"])[0][0]
        )

        # Create table for generic values
        self.database.create_table(
            table_name="timewise_values",
            columns=[
                Column("id", data_type="INTEGER", primary_key=True, auto_increment=True),
                Column("name"),
                Column("value"),
                Column("group_id", data_type="INTEGER"),
            ],
            unique_constraints=[UniqueConstraint(["name"])],
            foreign_keys=[ForeignKey("group_id", "groups", "id")],
            can_exist=True
        )

        # Set default priority min and max
        self.database.insert(table_name="timewise_values", name="priority_min", value="0", group_id=settings_id, drop_duplicate=True)
        self.database.insert(table_name="timewise_values", name="priority_max", value="5", group_id=settings_id, drop_duplicate=True)

        # Set default categories
        self.database.insert(table_name="timewise_values", name="work", value="Work", group_id=category_id, drop_duplicate=True)
        self.database.insert(table_name="timewise_values", name="personal", value="Personal", group_id=category_id, drop_duplicate=True)

        # Create views for tags, categories, and settings
        self.database.create_view("tags", table_name="timewise_values", conditions={"group_id": tag_id}, can_exist=True)
        self.database.create_view("categories", table_name="timewise_values", conditions={"group_id": category_id}, can_exist=True)
        self.database.create_view("settings", table_name="timewise_values", conditions={"group_id": settings_id}, can_exist=True)
        self.database.create_view("custom_fields", table_name="timewise_values", conditions={"group_id": custom_field_id}, can_exist=True)

        # Create table for tasks
        self.database.create_table(
            table_name="tasks",
            columns=[
                Column("id", data_type="INTEGER", primary_key=True, auto_increment=True),
                Column("title"),
                Column("description", allow_null=True),
                Column("status_id", data_type="INTEGER"),
                Column("category_id", data_type="INTEGER"),
                Column("priority", data_type="INTEGER"),
                Column("estimated_time", data_type="INTEGER", allow_null=True),
                Column("time_spent", data_type="INTEGER", allow_null=True),
                Column("due_date", allow_null=True),
                Column("start_date", allow_null=True),
                Column("completed", data_type="INTEGER"),
            ],
            foreign_keys=[
                ForeignKey("category_id", "categories", "id"),
                ForeignKey("status_id", "statuses", "id")
            ],
            check_constraints=[
                CheckConstraint("priority", ">=", "0"),
            ],
            can_exist=True
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
            unique_constraints=[UniqueConstraint(["task_id", "tag_id"])],
            can_exist=True
        )

        # Create table for task custom fields
        self.database.create_table(
            table_name="task_custom_fields",
            columns=[
                Column("task_id", data_type="INTEGER"),
                Column("custom_field_id", data_type="INTEGER"),
                Column("value"),
            ],
            foreign_keys=[
                ForeignKey("task_id", "tasks", "id"),
                ForeignKey("custom_field_id", "custom_fields", "id")
            ],
            unique_constraints=[UniqueConstraint(["task_id", "custom_field_id"])],
            can_exist=True
        )

        # Create table for intervals
        self.database.create_table(
            table_name="intervals",
            columns=[
                Column("id", data_type="INTEGER", primary_key=True, auto_increment=True),
                Column("name"),
                Column("seconds"),
                Column("description"),
            ],
            unique_constraints=[UniqueConstraint(["name"]), UniqueConstraint(["seconds"])],
            can_exist=True
        )

        self.database.insert(table_name="intervals", name="minute", seconds=60, description="1 minute", drop_duplicate=True)
        self.database.insert(table_name="intervals", name="hour", seconds=3600, description="1 hour", drop_duplicate=True)
        self.database.insert(table_name="intervals", name="day", seconds=86400, description="1 day", drop_duplicate=True)
        self.database.insert(table_name="intervals", name="week", seconds=604800, description="1 week", drop_duplicate=True)
        self.database.insert(table_name="intervals", name="month", seconds=2628000, description="1 month", drop_duplicate=True)
        self.database.insert(table_name="intervals", name="year", seconds=31536000, description="1 year", drop_duplicate=True)

        # Create table for task intervals
        self.database.create_table(
            table_name="task_intervals",
            columns=[
                Column("task_id", data_type="INTEGER"),
                Column("interval_id", data_type="INTEGER"),
                Column("value", data_type="INTEGER"),
            ],
            foreign_keys=[ForeignKey("task_id", "tasks", "id"), ForeignKey("interval_id", "intervals", "id")],
            unique_constraints=[UniqueConstraint(["task_id", "interval_id"])],
            can_exist=True
        )

        # Create table for task status
        self.database.create_table(
            table_name="statuses",
            columns=[
                Column("id", data_type="INTEGER", primary_key=True, auto_increment=True),
                Column("name"),
            ],
            can_exist=True
        )

        self.database.insert(table_name="statuses", name="pending", drop_duplicate=True)
        self.database.insert(table_name="statuses", name="in_progress", drop_duplicate=True)
        self.database.insert(table_name="statuses", name="completed", drop_duplicate=True)
        self.database.insert(table_name="statuses", name="canceled", drop_duplicate=True)

