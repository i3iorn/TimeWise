from src.timewise import TaskCollection


def by_priority(collection: "TaskCollection"):
    """
    Sort the collection of tasks by priority.

    Args:
        collection (TaskCollection): The collection of tasks to sort.

    Returns:
        TaskCollection: The sorted collection of tasks.
    """
    return TaskCollection(sorted(collection.all(), key=lambda x: x.priority))


def by_due_date(collection: "TaskCollection"):
    """
    Sort the collection of tasks by due date.

    Args:
        collection (TaskCollection): The collection of tasks to sort.

    Returns:
        TaskCollection: The sorted collection of tasks.
    """
    try:
        return TaskCollection(sorted(collection.all(), key=lambda x: x.due_time))
    except TypeError:
        import warnings
        warnings.warn("Some tasks have no due date and will be sorted to the end.")
        return collection


def by_category(collection: "TaskCollection"):
    """
    Sort the collection of tasks by category.

    Args:
        collection (TaskCollection): The collection of tasks to sort.

    Returns:
        TaskCollection: The sorted collection of tasks.
    """
    return TaskCollection(sorted(collection.all(), key=lambda x: x.category.name))


def by_name(collection: "TaskCollection"):
    """
    Sort the collection of tasks by name.

    Args:
        collection (TaskCollection): The collection of tasks to sort.

    Returns:
        TaskCollection: The sorted collection of tasks.
    """
    return TaskCollection(sorted(collection.all(), key=lambda x: x.name))


def by_start_time(collection: "TaskCollection"):
    """
    Sort the collection of tasks by start time.

    Args:
        collection (TaskCollection): The collection of tasks to sort.

    Returns:
        TaskCollection: The sorted collection of tasks.
    """
    return TaskCollection(sorted(collection.all(), key=lambda x: x.start_time))


def by_priority_and_due_date(collection: "TaskCollection"):
    """
    Sort the collection of tasks by priority and due date.

    Args:
        collection (TaskCollection): The collection of tasks to sort.

    Returns:
        TaskCollection: The sorted collection of tasks.
    """
    return TaskCollection(sorted(collection.all(), key=lambda x: (x.priority, x.due_time)))
