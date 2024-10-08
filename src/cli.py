import logging
import click

from datetime import datetime, timedelta

from sqlalchemy import select
from tabulate import tabulate
from typing import Dict, Any, Type, Optional

from src import exceptions
from src.models.category import Category
from src.models.recurrence import Recurrence
from src.models.reminder import Reminder
from src.models.sides import Settings
from src.timewise import TimeWise


# Set up logging
timewise = TimeWise(echo_database_calls=False)
logger = logging.getLogger(__name__)


def get_task_by_id(task_id: int):
    """
    Get a task by its id.

    :param task_id: The id of the task to get.
    :type task_id: int
    :return: The task with the given id.
    :rtype: Task
    """
    return timewise.get_tasks().filter(id=task_id).first()


def parse_datetime(date_str: str) -> datetime:
    """
    Parse a date string into a datetime object.

    :param date_str: The date string to parse.
    :type date_str: str
    :return: The datetime object.
    :rtype: datetime
    """
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")


def parse_tags(tags_str: str) -> list:
    """
    Parse a string of tags into a list of tags.

    :param tags_str: The string of tags to parse.
    :type tags_str: str
    :return: The list of tags.
    :rtype: list
    """
    return [tag.strip() for tag in tags_str.split(",")]


def handle_exceptions(func):
    """
    Handle exceptions in a function.

    :param func: The function to wrap.
    :type func: Callable
    :return: The wrapped function.
    :rtype: Callable
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")
    return wrapper


def print_heading(heading: str) -> None:
    """
    Print a heading with a line of dashes above and below it.

    :param heading: The heading to print.
    :type heading: str

    :return: None
    """
    length = 60
    tab = 4
    print(f"\n{'=' * length}\n={' ' * tab}{str(heading[:length-tab-2]).ljust(length-tab-2)}=\n{'=' * length}")


def interval_to_seconds(interval: str) -> int:
    """
    Convert an interval string to seconds.

    :param interval: The interval string to convert.
    :type interval: str

    :return: The interval in seconds.
    :rtype: int
    """
    seconds = 0
    digits = ""

    for c in interval:
        if c.isdigit():
            digits += c
        else:
            if c == "s":
                seconds += int(digits)
            elif c == "m":
                seconds += int(digits) * 60
            elif c == "h":
                seconds += int(digits) * 60 * 60
            elif c == "d":
                seconds += int(digits) * 60 * 60 * 24
            elif c == "w":
                seconds += int(digits) * 60 * 60 * 24 * 7
            elif c == "M":
                seconds += int(digits) * 60 * 60 * 24 * 30
            elif c == "y":
                seconds += int(digits) * 60 * 60 * 24 * 365
            digits = ""

    return seconds


def seconds_to_interval(seconds: int) -> str:
    """
    Convert seconds to a human-readable interval string.

    :param seconds: The number of seconds to convert.
    :type seconds: int

    :return: The interval string.
    :rtype: str
    """
    units = {
        "y": 60 * 60 * 24 * 365,
        "M": 60 * 60 * 24 * 30,
        "w": 60 * 60 * 24 * 7,
        "d": 60 * 60 * 24,
        "h": 60 * 60,
        "m": 60,
        "s": 1
    }

    interval = ""
    for u, s in units.items():
        if seconds >= s:
            interval += str(seconds // s) + u
            seconds = seconds % s
    return interval



@click.group()
def cli():
    """A simple CLI application."""
    pass


@cli.command(hidden=True)
def drop_database() -> None:
    """
    Drop the database.
    """
    timewise.drop_database()
    print("Database dropped successfully.")


@click.group()
def categories():
    """
    Open the categories interface. This interface allows you to manage categories through a series of subcommands.
    """
    pass


@categories.command()
@click.argument('name')
@click.option('-d', '--description', default="", help='A detailed description of the category.')
def add_category(name, description):
    """
    Add a new category.

    Example:
    $ timewise categories add-category 'Category Name' 'Category Description'

    :param name: The name of the category.
    :type name: str
    :param description: A detailed description of the category.
    :type description: str
    :return: None
    """
    timewise.add_category(name=name, description=description)
    print(f"Category '{name}' added successfully.")


@categories.command()
def list_categories():
    """
    List all categories.
    """
    task_display_format = "{:<5} {:<20} {:<20} {:<11}"
    print(task_display_format.format("ID", "Name", "Description", "Is Active"))
    for category in timewise.get_categories():
        print(task_display_format.format(
            str(category.id),
            str(category.name),
            str(category.description),
            str(category.is_active)
        ))



@click.group()
def tasks() -> None:
    """
    Open the tasks interface. This interface allows you to manage tasks through a series of subcommands.
    """
    pass


@tasks.command()
def sort_methods() -> None:
    """
    List all the methods available as arguments to the --sort-by option in the list command.
    """
    print("The available methods to sort tasks are:")
    for method in timewise.sort_methods:
        print(f"  {method}")


@tasks.command()
@click.option('-s', '--sort-by', default="due_time", help='The method to sort the tasks by.')
@click.option('-c', '--columns', help='The columns to display in the task list.')
@click.option('--include-completed', is_flag=True, help='Include completed tasks in the list.')
def list(**kwargs: Dict[str, Any]) -> None:
    """
    List all tasks. Optionally, sort the tasks by a specific method.

    Example:
    $ timewise tasks list -s 'due_date' -c 'name, description, due_date, completed_at, priority, category'

    :param kwargs: Additional keyword arguments.
    :type kwargs: Dict[str, Any]
    :return: None
    """
    task_display_columns = get_display_columns(kwargs.get("columns", None))

    tasks = timewise.get_tasks(sort_by=kwargs.get("sort_by", "due_time"), include_completed=kwargs.get("include_completed", False))

    task_data = [[getattr(task, column) for column in task_display_columns] for task in tasks.all()]

    print(tabulate(task_data, headers=task_display_columns, tablefmt="grid"))


def get_display_columns(columns: Optional[str] = None) -> list:
    if columns is None:
        columns = timewise.session.query(Settings).filter(Settings.key == "default_display_columns").one().value
    return [column.strip() for column in columns.split(",")]


@tasks.command()
@click.pass_context
@click.argument('name', required=False)
@click.argument('desc', required=False)
@click.option('-n', '--task-name', help='The name of the task.')
@click.option('-e', '--description', default="", help='A detailed description of the task.')
@click.option('-s', '--start-time', default=datetime.now(), help='What time you can begin completing the task at the earliest')
@click.option('-d', '--due-time', default=None, help='The deadline for completing the task.')
@click.option('-c', '--category_id', default=None, help='The category id to which the task belongs.')
@click.option('-C', '--category', default=None, help='The category name to which the task belongs.')
@click.option('-t', '--tags', default=None, help='The tags associated with the task.')
@click.option('-p', '--priority', default=3, help='The priority of the task.')
@click.option('-r', '--recurring-interval', help='Recurring interval, use 1y1M1d1h1m1s format')
@click.option('--literal-title', is_flag=True, help='Whether to use the literal title or standard formatting.')
@click.option('--completed', is_flag=True, help='Whether the task is completed.')
def add(ctx, name: str, desc: str, **kwargs: Dict[str, Any]) -> None:
    """
    Add a new task. The name and description arguments are optional.

    Example:
    $ timewise tasks add 'Task Name' 'Task Description' -s '2021-01-01 12:00:00.000' -d '2021-01-02 12:00:00.000' -c 1 -t 'tag1, tag2' -p 1

    :param name: The name of the task.
    :type name: Optional[str]
    :param desc: A detailed description of the task.
    :type desc: Optional[str]
    :param kwargs: Additional keyword arguments.
    :type kwargs: Dict[str, Any]
    :return: None
    """
    task_name = get_task_name(name, kwargs)
    interval = kwargs.pop("recurring_interval", None)
    description = desc or kwargs.pop("description")
    kwargs = process_options(kwargs)

    try:
        task_id = timewise.add_task(name=task_name, description=description, **kwargs)
    except exceptions.CategoryNotFoundException as e:
        new_category = click.prompt(f"Category '{e.category_name}' not found. Would you like to create it? [y/n]")
        if new_category.lower() in ["yes", "y"]:
            new_cat_desc = click.prompt("Please provide a description for the new category.")
            add_category(e.category_name)
            task_id = timewise.add_task(name=e.category_name, description=new_cat_desc, **kwargs)
        else:
            return

    if interval is not None:
        add_recurrence([str(task_id), interval])
        print(f"Task '{task_name}' added successfully.")


def get_task_name(name: str, kwargs: Dict[str, Any]) -> str:
    task_name = name or kwargs.get("task_name")
    if not task_name:
        task_name = click.prompt("Please provide a name for the task")
    return task_name


def process_options(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    if kwargs["start_time"]:
        try:
            start_seconds = interval_to_seconds(kwargs["start_time"])
            kwargs["start_time"] = datetime.now() + timedelta(seconds=start_seconds)
        except ValueError:
            kwargs["start_time"] = datetime.strptime(kwargs["start_time"], "%Y-%m-%d %H:%M:%S.%f")
    if kwargs["due_time"]:
        try:
            due_seconds = interval_to_seconds(kwargs["due_time"])
            kwargs["due_time"] = datetime.now() + timedelta(seconds=due_seconds)
        except ValueError:
            kwargs["due_time"] = datetime.strptime(kwargs["due_time"], "%Y-%m-%d %H:%M:%S.%f")

    if "tags" in kwargs and isinstance(kwargs["tags"], str):
        kwargs["tags"] = [t.strip() for t in kwargs["tags"].split(",")]

    if kwargs["literal_title"]:
        kwargs["task_name"] = kwargs["task_name"][0].upper() + kwargs["task_name"][1:]
    kwargs.pop("literal_title", None)

    if kwargs["completed"]:
        kwargs["completed_at"] = datetime.now()
    kwargs.pop("completed", None)

    return kwargs


@tasks.command()
@click.argument('task_id', required=True)
@click.pass_context
@click.option('-n', '--name', type=str, help='The name of the task.')
@click.option('-d', '--description', type=str, help='A detailed description of the task.')
@click.option('-s', '--start-time', type=str, help='The start time of the task.')
@click.option('-d', '--due-time', type=str, help='The due time of the task.')
@click.option('-c', '--category-id', type=int, help='The category id of the task.')
@click.option('-C', '--category', type=str, help='The category name of the task.')
@click.option('-t', '--tags', type=str, help='The tags associated with the task.')
@click.option('-p', '--priority', type=int, help='The priority of the task.')
@click.option('--completed', help='Whether the task is completed.')
def update(ctx, task_id, **data):
    """
    Update an existing task. The data argument should be a comma-separated list of key-value pairs.

    Example:
    $ timewise tasks update 1 {'name': 'New Task Name', 'description': 'New Task Description'}

    Args:
        ctx: The click context.
        task_id: The id of the task to update.
        data: The data to update the task with.

    Returns:
        None

    Raises:
        ValueError: If the category id provided is not a valid integer.
    """
    task = get_task_by_id(int(task_id))
    if task is None:
        print(f"Task with id '{task_id}' not found.")
        return

    for key, value in data.items():
        if value is None:
            continue

        try:
            # Convert the value to the correct type
            if key in ["start_time", "due_time", "completed"] and value is not None:
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            elif key == "tags":
                value = [t.strip() for t in value.split(",")]
            elif key == "priority":
                value = int(value)
            elif key == "category_id" or key == "category":
                if isinstance(value, (int, str)) and value.isdigit():
                    value = timewise.session.query(Category).filter(Category.id == int(value)).first()
                elif isinstance(value, str):
                    value = timewise.session.query(Category).filter(Category.name == value).first()
                else:
                    raise TypeError(f"{key} has to be of type (str, int) not {type(value)}")

            if not bool(value):
                print(f"Category '{data[key]}' not found.")
                return

            setattr(task, key, value)
        except TypeError as e:
            expected = str(e).split("must")[-1]
            raise TypeError(f"{key} must{expected}")

    timewise.session.commit()
    print(f"Task '{task.name}' updated successfully.")


def get_category(value: str) -> Type[Category]:
    if value.isdigit():
        return timewise.session.query(Category).filter(Category.id == int(value)).first()
    return timewise.session.query(Category).filter(Category.name == value).first()


@tasks.command()
@click.argument('task_id', required=True)
@click.argument('time', required=True)
def add_reminder(task_id, time):
    """
    Add a reminder to a task. The reminder time is set to the current time.

    Example:
    $ timewise tasks add-reminder 1 '2021-01-01 12:00:00.000'

    :param task_id: The id of the task to add a reminder to.
    :type task_id: str
    :param time: The time to set the reminder for.
    :type time: str
    :return: None
    """
    task = get_task_by_id(int(task_id))
    if task is None:
        print(f"Task with id '{task_id}' not found.")
        return

    reminder = Reminder(reminder_time=parse_datetime(time), task_id=task_id)
    timewise.session.add(reminder)
    timewise.session.commit()
    print(f"Reminder added to task '{task.name}'.")


@tasks.command()
@click.argument('task_id', required=True)
@click.argument('interval', required=True)
@click.option('-s', '--start-time', default=datetime.now(), help='The time to start the recurring task.')
@click.option('-e', '--end-time', default=None, help='The time to end the recurring task.')
def add_recurrence(task_id, interval, **kwargs):
    """
    Add a recurring task to a task. The interval is the number of seconds between each recurring task.

    Example:
    $ timewise tasks add-recurrence 1 '1d' -s '2021-01-01 12:00:00.000' -e '2021-01-02 12:00:00.000'

    :param task_id: The id of the task to add a recurring task to.
    :type task_id: str
    :param interval: The interval between each recurring task.
    :type interval: str
    :param kwargs: Additional keyword arguments.
    :type kwargs: Dict[str, Any]
    :return: None
    """
    task = get_task_by_id(int(task_id))
    if task is None:
        print(f"Task with id '{task_id}' not found.")
        return

    start_time = parse_datetime(kwargs["start_time"])
    end_time = parse_datetime(kwargs["end_time"]) if kwargs["end_time"] else None

    recurring_task = Recurrence(
        start=start_time,
        interval=interval_to_seconds(interval),
        end=end_time,
        task_id=task_id
    )

    timewise.session.add(recurring_task)
    timewise.session.commit()
    print(f"Recurring task added to task '{task.name}'.")


@tasks.command()
@click.argument('recurring_id', required=True)
def delete_recurrence(recurring_id):
    """
    Delete a recurring task from a task. The interval is the number of seconds between each recurring task.

    Example:
    $ timewise tasks delete-recurrence 1

    :param recurring_id: The id of the recurring task to delete.
    :type recurring_id: str
    :return: None
    """
    query = select(Recurrence).filter_by(id=int(recurring_id))
    recurring_task = timewise.session.execute(query).scalars().first()

    if recurring_task is None:
        print(f"Recurring task with id '{recurring_id}' not found.")
        return

    timewise.session.delete(recurring_task)
    timewise.session.commit()
    print(f"Recurring task with id '{recurring_id}' deleted successfully.")


@tasks.command()
@click.argument('cat', required=False)
@click.option('-n', '--task-name', help='The name of the task you want to delete.')
@click.option('-i', '--task-id', help='The id of the task you want to delete.')
def delete(cat, **kwargs):
    """
    Delete a task. The task can be specified by the category, task name, or task id.

    Example:
    $ timewise tasks delete 'Category Name'
    $ timewise tasks delete -n 'Task Name'
    $ timewise tasks delete -i 1

    :param cat: The category of the task to delete.
    :type cat: Optional[str]
    :param kwargs: Additional keyword arguments.
    :type kwargs: Dict[str, Any]
    :return: None
    """
    task = cat or kwargs.get("task_name") or kwargs.get("task_id")

    if task is None:
        task_name = click.prompt("Please provide the name of the task you want to delete.")
        task = timewise.get_tasks().filter(name=task_name).first()
    elif task is not None and (isinstance(task, int) or task.isdigit()):
        task = get_task_by_id(int(task))

    if task:
        timewise.delete_task(task)
        print(f"Task '{task.name}' deleted successfully.")


@tasks.command()
@click.argument('task_id')
def complete(task_id):
    """
    Mark a task as completed.

    Example:
    $ timewise tasks complete 1

    :param task_id: The id of the task to complete.
    :type task_id: str
    :return: None
    """
    task = get_task_by_id(int(task_id))
    if task is None:
        print(f"Task with id '{task_id}' not found.")
        return

    task.completed_at = datetime.now()
    timewise.session.commit()
    print(f"Task '{task.name}' marked as completed.")


@tasks.command()
@click.argument('task_id')
def show_task(task_id):
    """
    Show full details of a task. All fields are displayed in sections.

    Example:
    $ timewise tasks show-task 1

    :param task_id: The id of the task to show.
    :type task_id: str
    :return: None
    """
    task = get_task_by_id(int(task_id))
    if task is None:
        print(f"Task with id '{id}' not found.")
        return

    print_heading(f"TASK: {task.name}")
    if task.description:
        desc = ("Description: " + task.description).split()
        llength = 60
        line = ""
        while len(desc) > 0:
            if len(line + desc[0]) > llength:
                print(line)
                line = ""

            line += " " + desc.pop(0)

        print(line+"\n")

    # Get column names to display
    task_display_columns = ["id", "category", "priority", "count", "parent_task"]
    data = [[getattr(task, column) for column in task_display_columns]]

    print(tabulate(data, headers=task_display_columns, tablefmt="grid"))

    if task.tags:
        # Show all tags
        print_heading("TAGS")
        print(", ".join(task.tags))

    if task.reminders:
        # Show all reminders
        print_heading("Reminders")
        for reminder in task.reminders:
            print(f"{reminder.reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")

    if task.recurrence:
        # Show all recurring tasks
        print_heading("Recurring Tasks")
        print("ID\tInterval\tNext")
        for recurring_task in task.recurrence:
            print(f"{recurring_task.id}\t{seconds_to_interval(recurring_task.interval)}\t\t{next(recurring_task).strftime('%Y-%m-%d %H:%M:%S')}")

    # Show all times in a human-readable format
    print_heading("TIMES")
    if task.start_time:
        print(f"Start Time: {task.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if task.due_time:
        print(f"Due Time: {task.due_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if task.completed_at:
        print(f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")

    print_heading(f"END OF TASK: {task.name}")


cli.add_command(tasks)

cli.add_command(tasks)
cli.add_command(categories)
