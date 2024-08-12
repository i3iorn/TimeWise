import logging
import os
from typing import Union, List, Optional, Type, overload

from sqlalchemy import create_engine, inspect, exists, Column, text
from sqlalchemy.orm import Session, Query
from typeguard import typechecked

from src import exceptions
from src.config import Config
from src.models.category import Category
from src.models.common import Base
from src.models.task import Task, Tag
from src.models.sides import Settings

logger = logging.getLogger(__name__)


@typechecked
class TaskCollection:
    def __init__(self, tasks: List):
        self.__tasks = tasks

    def filter(self, **kwargs) -> "TaskCollection":
        for key, value in kwargs.items():
            self.__tasks = [task for task in self.__tasks if getattr(task, key) == value]
        return self

    def all(self) -> List["Task"]:
        return self.__tasks

    def first(self) -> Union["Task", None]:
        return self.__tasks[0] if self.__tasks else None

    def count(self) -> int:
        return len(self.__tasks)

    def __iter__(self):
        return iter(self.__tasks)

    def __next__(self):
        return next(self.__tasks)


@typechecked
class TimeWise:
    """
    TimeWise class to manage tasks, categories, and tags in a SQLite database.

    Attributes:
        conf (Config): Configuration object for the application.
    """

    def __init__(
            self,
            database_cursor: Union[str, None] = None,
            echo_database_calls: bool = False,
            log_level: int = logging.WARNING
    ):
        """
        Initializes the TimeWise instance, sets up the database connection, and adds initial records.

        Args:
            database_cursor (Union[str, None]): Path to the SQLite database file. If None, an in-memory database is used.
        """
        logging.basicConfig(level=log_level)
        self.conf = Config()

        database_name = database_cursor or os.environ.get("DB_HOST", ":memory:")
        print(database_name)

        self.__engine = create_engine(
            f"sqlite+pysqlite:///{database_name}",
            echo=echo_database_calls
        )
        self.__session = Session(self.__engine, autoflush=True)

        self.__metadata = Base.metadata

        try:
            inspector = inspect(self.__engine)
            tables = inspector.get_table_names()
            for table in self.__metadata.tables.keys():
                if table not in tables:
                    self.__metadata.tables[table].create(self.__engine)
                else:
                    # Check if all columns are present, otherwise add them
                    columns = inspector.get_columns(table)
                    for column in self.__metadata.tables[table].columns:
                        if column.name not in [c["name"] for c in columns]:
                            with self.__engine.connect() as connection:
                                new_column = Column(column.name, column.type)
                                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {new_column.compile(self.__engine)}"))
        except Exception as e:
            logger.error(f"Error creating and verifying tables: {e}")
            raise e

        self._add_initial_records()

    @property
    def session(self) -> Session:
        return self.__session

    @property
    def sort_methods(self) -> List[str]:
        """
        Get a list of available sort methods.

        :return: A list of available sort methods.
        :rtype: List[str]
        """
        return [method.replace('by_', '') for method in dir(__import__("src.sort", fromlist=["by_priority"])) if method.startswith("by_")]

    def _add_initial_records(self):
        # TODO: Move all initial records to a configuration file.
        initial_data = self.conf.get("initial_values")
        initial_categories = initial_data.get("categories")
        initial_tags = initial_data.get("tags")
        settings = initial_data.get("settings")

        for category in initial_categories:
            exists_query = self.__session.query(exists().where(Category.name == category['name'])).scalar()
            if not exists_query:
                self.__session.add(Category(**category))
                self.__session.flush()

        for tag in initial_tags:
            exists_query = self.__session.query(exists().where(Tag.name == tag['name'])).scalar()
            if not exists_query:
                self.__session.add(Tag(**tag))
                self.__session.flush()

        for setting in settings:
            exists_query = self.__session.query(exists().where(Settings.key == setting['key'])).scalar()
            if not exists_query:
                self.__session.add(Settings(**setting))
                self.__session.flush()

        self.__session.commit()
        logger.debug("Initial records added to the database.")

    def add_task(self, **kwargs) -> int:
        """
        Add a task to the database. Optionally provide a category, tags, and other task attributes.

        Args:
            **kwargs: Task attributes. Optionally provide a category, tags, and other task attributes

        Returns:
            integer ID of the added task

        Raises:
            ValueError: If the category provided is not found in the database.
        """
        logger.debug(f"Adding task to the database with attributes: {kwargs}")

        cat = self.__session.query(Settings).filter(Settings.key == "default_category").one().value
        categories = self.__session.query(Category)
        if "category_id" in kwargs and kwargs["category_id"] is not None:
            logger.debug(f"Category ID provided: {kwargs['category_id']}")
            cat = kwargs.pop("category_id")
            category = categories.filter(Category.id == cat).one_or_none()
        elif "category" in kwargs and kwargs["category"] is not None:
            logger.debug(f"Category name provided: {kwargs['category']}")
            cat = kwargs.pop("category")
            category = categories.filter(Category.name == cat).one_or_none()
        else:
            logger.debug(f"Default category used: {cat}")
            category = categories.filter(Category.name == cat).one_or_none()

        if category is None:
            raise exceptions.CategoryNotFoundException(category=cat)

        tags = kwargs.pop("tags", [])

        arguments = {k: v for k, v in kwargs.items() if k != "category" and v is not None}
        arguments["category"] = category

        task = Task(**arguments)
        self.__session.add(task)
        self.__session.flush()

        if tags:
            task.tags = self.__session.query(Tag).filter(Tag.name.in_(tags)).all()

        self.__session.commit()
        logger.debug(f"Task '{task.name}' with description '{task.description}' added to the database.")
        return task.id

    def drop_database(self):
        self.__metadata.drop_all(self.__engine)
        logger.debug("Database dropped.")

    def get_tasks(
            self,
            category: Optional[str] = None,
            tag: Optional[str] = None
    ) -> TaskCollection:
        """
        Get tasks from the database. Optionally filter by category and tag. Optionally sort by a specific method. A list
        of available sort methods can be found in src.sort.

        :param category: Optionally filter by category.
        :type category: Optional[str]
        :param tag: Optionally filter by tag.
        :type tag: Optional[str]
        :param sort_by: Optionally sort by a specific method, give the method name. A list of available methods can be
        found in src.sort.
        :type sort_by: Optional[str]
        :return:
        :rtype: TaskCollection
        """
        query = self.__session.query(Task)

        if category:
            query = query.join(Category).filter(Category.name == category)

        if tag:
            query = query.join(Task.tags).filter(Tag.name == tag)

        query = query.order_by(Task.start_time)
        tasks = query.all()

        msg_string = f"Found {len(tasks)} task"
        if len(tasks) != 1:
            msg_string += "s"
        msg_string += "."
        if len(tasks) > 0:
            msg_string += f" Task names: {', '.join([task.name for task in tasks][:5])} ..."
        logger.debug(msg_string)

        return TaskCollection(sorted(tasks, key=lambda x: x.start_time))

    def delete_task(
            self,
            task: Optional[Task] = None,
            task_id: Optional[int] = None,
            task_name: Optional[str] = None
    ) -> None:
        """
        Deletes a task from the database. Optionally provide the task object, ID, or name.

        :param task: The task object to delete.
        :type: Task
        :param task_id: The ID of the task to delete.
        :type: int
        :param task_name: The name of the task to delete.
        :type: str
        :return: None
        """
        if task_id is not None:
            task = self.__session.query(Task).filter(Task.id == task_id).one_or_none()
        elif task_name is not None:
            task = self.__session.query(Task).filter(Task.name == task_name).one_or_none()

        if task is None:
            raise ValueError("Task not found.")

        self.__session.delete(task)
        self.__session.commit()
        logger.debug(f"Task '{task.name}' deleted from the database.")

    def add_category(self, name: str, description: str = "") -> None:
        category = Category(name=name, description=description)
        self.__session.add(category)
        self.__session.commit()
        logger.debug(f"Category '{name}' added to the database.")

    def get_categories(self) -> List[Type[Category]]:
        """
        Retrieves all categories from the database.

        Returns:
            List[Category]: A list of all categories.
        """
        return self.__session.query(Category).all()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__session.close()
        self.__engine.dispose()

