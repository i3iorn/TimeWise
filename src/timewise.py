import logging
from typing import Union, List, Optional, Type, overload

from sqlalchemy import create_engine, inspect, exists
from sqlalchemy.orm import Session
from typeguard import typechecked

from src.config import Config
from src.models import Base, Category, Tag, Task, Settings

logger = logging.getLogger(__name__)


@typechecked
class TaskCollection:
    def __init__(self, tasks: List[Task]):
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
        database_name = database_cursor or self.conf.get('database', {}).get('host', ':memory:')

        self.__engine = create_engine(
            f"sqlite+pysqlite:///{database_name}",
            echo=echo_database_calls
        )
        self.__session = Session(self.__engine, autoflush=True)

        self.__metadata = Base.metadata

        inspector = inspect(self.__engine)
        tables = inspector.get_table_names()
        for table in self.__metadata.tables.keys():
            if table not in tables:
                self.__metadata.tables[table].create(self.__engine)

        self._add_initial_records()

    def _add_initial_records(self):

        initial_categories = [
            {"name": "Work", "description": "Work related tasks", "is_active": True},
            {"name": "Personal", "description": "Personal tasks", "is_active": True},
        ]

        initial_tags = [
            {"name": "Urgent", "description": "Urgent tasks", "is_active": True},
            {"name": "Optional", "description": "Optional tasks", "is_active": True},
        ]

        settings = [
            {"key": "default_category", "value": "1"},
        ]

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

    def add_task(self, **kwargs) -> None:
        default_category = self.__session.query(Settings).filter(Settings.key == "default_category").one()
        category = kwargs.pop("category", None) or kwargs.pop("category_id", None) or default_category.value
        if isinstance(category, str) and category.isdigit():
            category = int(category)
        elif isinstance(category, str) and not category.isdigit() or not isinstance(category, int):
            raise ValueError("Category ID must be an integer or a string representing an integer.")

        tags = kwargs.pop("tags", [])

        arguments = {k: v for k, v in kwargs.items() if k != "category" and v is not None}

        category_obj = None
        if isinstance(category, int):
            category_exists = self.__session.query(exists().where(Category.id == category)).scalar()
            if category_exists:
                category_obj = self.__session.query(Category).filter(Category.id == category).one()
        elif category:
            category_exists = self.__session.query(exists().where(Category.name == category)).scalar()
            if category_exists:
                category_obj = self.__session.query(Category).filter(Category.name == category).one()

        if category_obj:
            arguments["category"] = category_obj

        task = Task(**arguments)
        self.__session.add(task)
        self.__session.flush()

        if tags:
            task.tags = self.__session.query(Tag).filter(Tag.name.in_(tags)).all()

        self.__session.commit()
        logger.debug(f"Task '{task.name}' with description '{task.description}' added to the database.")

    def get_tasks(self, category: Optional[str] = None, tag: Optional[str] = None):

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

        return TaskCollection(tasks)

    @overload
    def detele_task(self, task_id: int) -> None:
        """
        Deletes a task from the database by its ID.

        :param task_id:
        :return:
        """
        ...

    @overload
    def delete_task(self, task_name: str) -> None:
        """
        Deletes a task from the database by its name.

        :param task_name:
        :return:
        """
        ...

    def delete_task(
            self,
            task: Optional[Task] = None,
            task_id: Optional[int] = None,
            task_name: Optional[str] = None
    ) -> None:
        """
        Deletes a task from the database.

        :param task:
        :param task_id:
        :param task_name:
        :return:
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

    def get_categories(self):
        return self.__session.query(Category).all()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__session.close()
        self.__engine.dispose()

