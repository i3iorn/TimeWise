import datetime
import logging

from typeguard import typechecked

from src.datatypes.base import TimeWiseDatatype


@typechecked
class TaskTitle(TimeWiseDatatype):
    """
    A class to represent a title in the TimeWise application
    """
    MAX_LENGTH = 100
    MIN_LENGTH = 1


@typechecked
class Description(TimeWiseDatatype):
    """
    A class to represent a description in the TimeWise application.
    """
    ALLOW_EMPTY = True
    ALLOW_NONE = True
    MAX_LENGTH = 1000


@typechecked
class Notes(TimeWiseDatatype):
    """
    A class to represent notes in the TimeWise application.
    """
    ALLOW_EMPTY = True
    ALLOW_NONE = True
    MAX_LENGTH = 10000


@typechecked
class Tag(TimeWiseDatatype):
    """
    A class to represent a tag in the TimeWise application.
    """
    ALLOW_EMPTY = True
    ALLOW_NONE = True
    MAX_LENGTH = 40
    MIN_LENGTH = 3


@typechecked
class Location(TimeWiseDatatype):
    """
    A class to represent a location in the TimeWise application.
    """
    ALLOW_EMPTY = True
    ALLOW_NONE = True
    MAX_LENGTH = 2
    MIN_LENGTH = 2
    PRIMITIVE_TYPE = tuple


@typechecked
class Reminder(TimeWiseDatatype):
    """
    A class to represent a reminder in the TimeWise application.
    """
    ALLOW_NONE = True
    PRIMITIVE_TYPE = datetime.datetime


@typechecked
class Project(TimeWiseDatatype):
    """
    A class to represent a project in the TimeWise application.
    """
    ALLOW_NONE = True


@typechecked
class Category(TimeWiseDatatype):
    """
    A class to represent a category in the TimeWise application.
    """
    pass


@typechecked
class Participant:
    """
    A class to represent a participant in the TimeWise application.
    """
    ALLOW_NONE = True


@typechecked
class Attachment:
    """
    A class to represent an attachment in the TimeWise application.
    """
    ALLOW_NONE = True
