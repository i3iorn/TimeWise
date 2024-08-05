from datetime import datetime

from sqlalchemy.exc import IntegrityError

from src.models import Settings
from src.timewise import TimeWise
import click
from tabulate import tabulate


timewise = TimeWise()


@click.group()
def cli():
    """A simple CLI application."""
    pass


@click.group()
def tasks():
    """
    Open the tasks interface. This interface allows you to manage tasks through a series of subcommands.
    """
    pass


@tasks.command()
def sort_methods():
    """
    List all the methods available as arguments to the --sort-by option in the list command.
    """
    print("The available methods to sort tasks are:")
    for method in timewise.sort_methods:
        print(f"  {method}")


@tasks.command()
@click.option('-s', '--sort-by', help='The method to sort the tasks by.')
@click.option('-c', '--columns', help='The columns to display in the task list.')
def list(**kwargs):
    """
    List all tasks. Optionally, sort the tasks by a specific method.

    :param sort_by: The method to sort the tasks by.
    :type sort_by: Optional[str]

    :return: None
    """
    sort_name = kwargs.get("sort_by", "due_date")
    if sort_name == "date":
        sort_name = "due_date"
    sort_name = sort_name.replace("-", "_").replace(" ", "_")
    if sort_name not in timewise.sort_methods:
        print(f"Invalid sort method '{sort_name}'. Please use the 'sort_methods' command to see available options.")
        return

    tasks = timewise.get_tasks(sort_by=f'by_{sort_name}')

    # Get column names to display
    task_display_columns = timewise.session.query(Settings).filter(
        Settings.key == "default_display_columns").one().value.split(",") if kwargs.get(
        "columns") is None else kwargs.get("columns").split(",")
    task_display_columns = [column.strip() for column in task_display_columns]

    # Convert tasks to a list of lists for tabulate
    task_data = [[getattr(task, column) for column in task_display_columns] for task in tasks.all()]

    # Display the tasks using tabulate
    print(tabulate(task_data, headers=task_display_columns, tablefmt="grid"))


@tasks.command()
@click.argument('name', required=False)
@click.argument('desc', required=False)
@click.option('-n', '--task-name', help='The name of the task.')
@click.option('-e', '--description', default="", help='A detailed description of the task.')
@click.option('-s', '--start-time', default=datetime.now(), help='What time you can begin completing the task at the earliest')
@click.option('-d', '--due-time', default=None, help='The deadline for completing the task.')
@click.option('-c', '--category_id', default=None, help='The category id to which the task belongs.')
@click.option('-t', '--tags', default=None, help='The tags associated with the task.')
@click.option('-p', '--priority', default=3, help='The priority of the task.')
def add(name, desc, **kwargs):
    """
    Add a new task.
    """
    task_name = name or kwargs.get("task_name")
    if not task_name:
        task_name = click.prompt("Please provide a name for the task")

    description = desc or kwargs.get("description")
    del kwargs["task_name"]
    del kwargs["description"]

    kwargs["start_time"] = datetime.strptime(kwargs["start_time"], "%Y-%m-%d %H:%M:%S.%f")
    if kwargs["due_time"]:
        kwargs["due_time"] = datetime.strptime(kwargs["due_time"], "%Y-%m-%d %H:%M:%S.%f")

    if "tags" in kwargs:
        kwargs["tags"] = [t.strip() for t in kwargs["tags"].split(",")]

    try:
        timewise.add_task(name=task_name, description=description, **kwargs)
    except IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"Task '{task_name}' already exists with the same description.")
        else:
            print(f"Error adding task: {e}")
    else:
        print(f"Task '{task_name}' added successfully.")


@tasks.command()
def update():
    """
    Update an existing task.
    """
    pass


@tasks.command()
@click.argument('cat', required=False)
@click.option('-n', '--task-name', help='The name of the task you want to delete.')
@click.option('-i', '--task-id', help='The id of the task you want to delete.')
def delete(cat, **kwargs):
    """
    Delete a task.
    """
    task = cat or kwargs.get("task_name") or kwargs.get("task_id")

    if task is None:
        task_name = click.prompt("Please provide the name of the task you want to delete.")
        task = timewise.get_tasks().filter(name=task_name).first()
    elif task is not None and (isinstance(task, int) or task.isdigit()):
        task = timewise.get_tasks().filter(id=int(task)).first()

    if task:
        timewise.delete_task(task)
        print(f"Task '{task.name}' deleted successfully.")


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
    """
    try:
        timewise.add_category(name=name, description=description)
    except IntegrityError as e:
        print(f"Error adding category: {e}")
    else:
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


cli.add_command(tasks)
cli.add_command(categories)
