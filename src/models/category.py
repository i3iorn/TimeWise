from typing import List, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.common import Base

if TYPE_CHECKING:
    from src.models.task import Task


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=lambda: uuid4().hex)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(4000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    color: Mapped[str] = mapped_column(String(16), nullable=True)

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="category")

    def __str__(self):
        return self.name
