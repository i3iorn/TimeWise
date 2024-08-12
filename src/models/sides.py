from typing import List, TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.common import TimeStampedMixin, Base

if TYPE_CHECKING:
    from src.models.task import Task


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


class Unit(Base):
    __tablename__ = 'units'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(4000), nullable=True)
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="unit")

    def __str__(self):
        return self.name
