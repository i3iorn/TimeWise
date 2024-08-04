from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Boolean, Table, ForeignKey, and_, event, UniqueConstraint
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typeguard import typechecked


@typechecked
class TimeStampedMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


@typechecked
class Base(DeclarativeBase):
    __abstract__ = True
    __table_args__ = {'keep_existing': True}


class CustomValues(TimeStampedMixin, Base):
    __tablename__ = 'custom_values'
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    value: Mapped[str] = mapped_column(String(4000), nullable=True)


class Settings(Base):
    __tablename__ = 'settings'
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    value: Mapped[str] = mapped_column(String(4000), nullable=True)


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=lambda: uuid4().hex)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(4000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="category")


task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task", ForeignKey("tasks.id")),
    Column("tag", ForeignKey("tags.id")),
)


class Tag(Base):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=lambda: uuid4().hex)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(4000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tasks: Mapped[List["Task"]] = relationship("Task", secondary=task_tags, back_populates="tags")


class Reminder(Base):
    __tablename__ = 'reminders'
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=lambda: uuid4().hex)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    task: Mapped["Task"] = relationship("Task", back_populates="reminders")
    reminder_time: Mapped[datetime] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)


class Task(TimeStampedMixin, Base):
    """
    Represents a task in the database.

    Attributes:
        id (int): The primary key of the task.
        name (str): The name of the task.
        description (str): A detailed description of the task.
        start_time (datetime): The start time of the task.
        due_time (datetime): The due time of the task.
        completed_at (datetime): The time when the task was completed.
        category_id (int): The foreign key referencing the category of the task.
        category (Category): The category to which the task belongs.
        tags (List[Tag]): The tags associated with the task.
    """
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=lambda: uuid4().hex)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(4000), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now)
    due_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    reminders: Mapped[List["Reminder"]] = relationship(
        "Reminder",
        primaryjoin=id == Reminder.task_id,
        back_populates="task",
        cascade="all, delete-orphan",
    )

    parent_task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    parent_task: Mapped["Task"] = relationship(
        "Task",
        primaryjoin=parent_task_id == id,
        remote_side=[id],
        back_populates="sub_tasks",
    )

    sub_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        primaryjoin=id == parent_task_id,
        back_populates="parent_task",
    )

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(
        "Category",
        primaryjoin=and_(category_id == Category.id, Category.is_active == True),
        back_populates="tasks",
    )

    tags: Mapped[List["Task"]] = relationship(
        "Tag",
        secondary=task_tags,
        primaryjoin=task_tags.c.task == id,
        secondaryjoin=and_(task_tags.c.tag == Tag.id, Tag.is_active == True),
        back_populates="tasks",
    )

    __table_args__ = (
        UniqueConstraint('name', 'description', name='uix_name_description'),
    )

    __sort_by__ = "start_time"

    def mark_as_completed(self):
        """
        Marks the task as completed by setting the completed_at attribute to the current datetime.
        """
        self.completed_at = datetime.now()

    def mark_as_incomplete(self):
        """
        Marks the task as incomplete by setting the completed_at attribute to None.
        """
        self.completed_at = None

    def set_category(self, category: Category):
        """
        Sets the category of the task.

        Args:
            category (Category): The category to set for the task.
        """
        self.category = category

    def add_tag(self, tag: Tag):
        """
        Adds a tag to the task.

        Args:
            tag (Tag): The tag to add to the task.
        """
        self.tags.append(tag)

    def remove_tag(self, tag: Tag):
        """
        Removes a tag from the task.

        Args:
            tag (Tag): The tag to remove from the task.
        """
        self.tags.remove(tag)

    def update_start_time(self, start_time: datetime):
        """
        Updates the start time of the task.

        Args:
            start_time (datetime): The new start time for the task.
        """
        self.start_time = start_time


@event.listens_for(Task, "before_insert")
def default_reminder_before_insert(mapper, connection, target):
    reminder_time = target.due_time - timedelta(minutes=30) if target.due_time else datetime.now() + timedelta(hours=12)
    default_reminder = Reminder(
        task=target,
        reminder_time=reminder_time,  # Set the default reminder time
        is_active=True,
        is_sent=False
    )
    target._default_reminder = default_reminder  # Temporarily store the reminder on the target


@event.listens_for(Task, "after_insert")
def default_reminder_after_insert(mapper, connection, target):
    default_reminder = target._default_reminder
    target.reminders.append(default_reminder)
    del target._default_reminder


@event.listens_for(Session, "after_flush")
def default_reminder_after_flush(session, flush_context):
    for target in session.new:
        if isinstance(target, Task) and hasattr(target, '_default_reminder'):
            default_reminder = target._default_reminder
            session.add(default_reminder)
            target.reminders.append(default_reminder)
            del target._default_reminder
