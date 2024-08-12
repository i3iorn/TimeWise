from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import String, ForeignKey, Integer, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.common import Base

if TYPE_CHECKING:
    from src.models.task import Task


class Recurrence(Base):
    __tablename__ = 'recurrences'
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=lambda: uuid4().hex)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    task: Mapped["Task"] = relationship("Task", back_populates="recurrence")
    interval: Mapped[int] = mapped_column(Integer)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    start: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('task_id', 'interval', 'start', name='uix_task_interval_start'),
    )

    def __next__(self):
        while self.start < datetime.now():
            self.start += timedelta(seconds=self.interval)

        return self.start
