from typing import List, Tuple, Union

from src.components.task import Task

OPERATORS = ["==", "!=", ">", "<", ">=", "<=", "+", "-", "*", "/", "**", "%", "//", "in", "not in", "is", "is not"]


class Condition:
    """
    A condition to be used in a sorting algorithm. The condition is defined by a value, an operator, and an attribute
    name. The value is compared to the attribute of a task using the operator. The result of this comparison is returned
    as a float.

    Attributes:
    value: The value to compare to.
    operator: The operator to use in the comparison.
    attribute_name: The name of the attribute to compare to.

    Methods:
    __call__: Compare the value to the attribute of a task and return the result as a float.


    ### WARNING: This class uses the eval function. If the value is untrusted input, this can lead to code execution.
    """
    def __init__(self, value: Union[str, int, float], operator: OPERATORS, attribute_name: str):
        if not isinstance(value, (int, float)):
            if not isinstance(value, str) or not value.isalpha():
                raise ValueError("Value must be an integer or float, alternatively a string of only letters")

        if operator not in OPERATORS:
            raise ValueError(f"Operator must be one of: {OPERATORS}")

        if not isinstance(attribute_name, str) or not attribute_name.replace("_", "").isalpha():
            raise ValueError("Attribute name must be a string of only letters and underscores")

        self.value = value
        self.operator = operator
        self.attribute_name = attribute_name

    def __call__(self, task: "Task") -> float:
        if not hasattr(task, self.attribute_name):
            raise ValueError(f"Task does not have attribute {self.attribute_name}")

        attribute = getattr(task, self.attribute_name)

        ### WARNING: This is a security consideration. Do not use eval with untrusted input.
        # TODO: Replace eval with a safer alternative
        return float(eval(f"{self.value} {self.operator} {attribute}"))


class TaskSortingAlgorithm:
    """
    Base class for all sorting algorithms. These algorithms are used to sort the tasks in the task list when standard
    sorting is not enough. All attributes in a class can be used. You define a series of comparisons that evaluate to
    1 or 0 and each comparison is multiplied by a weight. The sum of all these comparisons is the final score for the
    task. The tasks are then sorted based on this score.

    The sorting algorithm is defined in the calculate_score method. The score is calculated by summing the results of
    each comparison. The tasks are sorted based on this score.

    Attributes:
    tasks: List of tasks to be sorted.
    comparisons: List of comparisons to be made.

    Methods:
    sort: Sort the tasks based on the sorting algorithm.
    calculate_score: Calculate the score for a task based on the sorting algorithm.
    """
    def __init__(self, tasks, conditions: List[Tuple[str | int | float, str, str]]):
        self.tasks = tasks
        self.conditions = [Condition(*condition) for condition in conditions]

    def sort(self):
        """
        Sort the tasks based on the sorting algorithm.
        """
        scores = []
        for task in self.tasks:
            score = self.calculate_score(task)
            scores.append(score)

        self.tasks = [task for _, task in sorted(zip(scores, self.tasks), key=lambda x: x[0], reverse=True)]

    def calculate_score(self, task):
        """
        Calculate the score for a task based on the sorting algorithm.
        """
        score = 0
        for comparison in self.conditions:
            score += comparison(task)

        return score
