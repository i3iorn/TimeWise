import html
import threading
from collections import defaultdict
from difflib import SequenceMatcher
from enum import Enum
from typing import List, Any, Dict, Type, Tuple
from abc import ABC, abstractmethod
import json
from jsonschema import validate, ValidationError

"""
This sorting factory takes a dictionary or json string matching the sort.schema_v1.json schema and returns a
function that sorts a TaskCollection object according to the specified sorting method.

Example:
{
  "name": "DueTimeSort",
  "attributes": [
    {
      "name": "due_time",
      "input_type": "datetime",
      "value": "2024-08-08 20:05:06.456123",
      "default": "2099-08-07 10:37:06.456123",
      "weight": "0.9"
    }
  ]
}
"""


class SortingFactory:
    """
    A factory class that creates and configures sorting classes.
    """

    def __init__(self):
        # Dictionary to store available sorting algorithms
        self.sorting_algorithms = {}

    def register_sorting_algorithm(self, name, sorting_class):
        """
        Register a new sorting algorithm with the factory.

        Args:
            name (str): The name of the sorting algorithm.
            sorting_class (type): The class that implements the sorting algorithm.
        """
        self.sorting_algorithms[name] = sorting_class

    def create_sorting_instance(self, name, **kwargs):
        """
        Create an instance of a sorting class.

        Args:
            name (str): The name of the sorting algorithm to use.
            **kwargs: Additional arguments to pass to the sorting class constructor.

        Returns:
            A sorting class instance.
        """
        if name not in self.sorting_algorithms:
            raise ValueError(f"Sorting algorithm '{name}' is not registered.")

        sorting_class = self.sorting_algorithms[name]
        return sorting_class(**kwargs)


class SortingAlgorithmMeta(type):
    """
    Metaclass for sorting algorithm classes.
    """

    def __new__(cls, name, bases, attrs):
        for method_name in ('sort', 'reverse_sort', 'time_complexity', 'space_complexity'):
            if method_name not in attrs or not callable(attrs[method_name]):
                raise TypeError(f"Sorting algorithm class '{name}' must implement the '{method_name}' method")

        return super(SortingAlgorithmMeta, cls).__new__(cls, name, bases, attrs)


class SortingAlgorithmInterface(metaclass=SortingAlgorithmMeta):
    """
    Abstract base class for sorting algorithms.
    """

    @abstractmethod
    def sort(self, data: list) -> list:
        """
        Sort the given data in ascending order.

        Args:
            data (list): The list of elements to be sorted.

        Returns:
            list: The sorted list.
        """
        pass

    @abstractmethod
    def reverse_sort(self, data: list) -> list:
        """
        Sort the given data in descending order.

        Args:
            data (list): The list of elements to be sorted.

        Returns:
            list: The sorted list in descending order.
        """
        pass

    @abstractmethod
    def time_complexity(self) -> str:
        """
        Get the time complexity of the sorting algorithm.

        Returns:
            str: The time complexity of the sorting algorithm.
        """
        pass

    @abstractmethod
    def space_complexity(self) -> str:
        """
        Get the space complexity of the sorting algorithm.

        Returns:
            str: The space complexity of the sorting algorithm.
        """
        pass


class ComparisonType(Enum):
    """
    An enumeration of comparison types for sorting algorithms.
    """
    BOOLEAN = 0
    DISTANCE = 1


class BooleanComparisonType(Enum):
    EQUAL = 0
    LESS_THAN = 1
    LESS_THAN_OR_EQUAL = 2
    GREATER_THAN = 3
    GREATER_THAN_OR_EQUAL = 4
    NOT_EQUAL = 5

    __aliases__ = {
        "eq": EQUAL,
        "ne": NOT_EQUAL,
        "lt": LESS_THAN,
        "le": LESS_THAN_OR_EQUAL,
        "gt": GREATER_THAN,
        "ge": GREATER_THAN_OR_EQUAL,
        "equal": EQUAL,
        "less_than": LESS_THAN,
        "less_than_or_equal": LESS_THAN_OR_EQUAL,
        "greater_than": GREATER_THAN,
        "greater_than_or_equal": GREATER_THAN_OR_EQUAL,
        "not_equal": NOT_EQUAL,
        "=": EQUAL,
        "!=": NOT_EQUAL,
        "<": LESS_THAN,
        "<=": LESS_THAN_OR_EQUAL,
        ">": GREATER_THAN,
        ">=": GREATER_THAN_OR_EQUAL
    }

    @classmethod
    def from_alias(cls, alias):
        return cls.__aliases__.get(alias)


class DistanceComparisonType(Enum):
    LEVENSHTEIN = 0
    JACCARD = 1
    ALPHABETICAL = 2
    NUMERIC = 3
    SORENSEN_DICE = 4


# DEFAULTS
WEIGHT = 1.0
REVERSE = False
NUMERIC_COMPARISON_TYPE = ComparisonType.DISTANCE
COMPARISON_SUBTYPE = DistanceComparisonType.NUMERIC
BOOLEAN_COMPARISON_TYPE = ComparisonType.BOOLEAN
BOOLEAN_COMPARISON_SUBTYPE = BooleanComparisonType.EQUAL
STRING_COMPARISON_TYPE = ComparisonType.DISTANCE
STRING_COMPARISON_SUBTYPE = DistanceComparisonType.ALPHABETICAL
DATETIME_COMPARISON_TYPE = ComparisonType.DISTANCE
DATETIME_COMPARISON_SUBTYPE = DistanceComparisonType.NUMERIC


class Comparator:
    """
    A class that provides comparison functions for sorting algorithms. The comparison functions can be configured to
    compare different types of data using different comparison methods.

    # Example use:
    # c = Comparator()
    # c.set_weight(0.5)
    # c.set_comparison_type(ComparisonType.DISTANCE)
    # c.set_comparison_subtype(DistanceComparisonType.LEVENSHTEIN)
    # print(c.compare("FooBar", "Foo Bar"))
    # prints: 0.01020408163265306
    """

    def __init__(
            self,
            key: str = None,
            comparison_type: ComparisonType = None,
            comparison_subtype: Type[Enum] = None,
            reverse: bool = REVERSE,
            weight: float = WEIGHT
    ):
        """
        Initialize the Comparator object. If no arguments are provided we try to guess as much as possible.
        """
        self.__reverse = None
        self.__weight = None

        if key is None or key == "":
            self.__key = None
        elif not isinstance(key, str):
            raise TypeError(f"Expected str, got {type(key)}")
        else:
            self.__key = key

        if comparison_type is None:
            self.__comparison_type, self.__comparison_subtype = self.__guess_comparison_type(key)

        if comparison_subtype is None:
            self.__comparison_subtype = self.__guess_comparison_subtype(self.__comparison_type)

        self.set_reverse(reverse)
        self.set_weight(weight)

    @property
    def comparison_type(self) -> ComparisonType:
        return self.__comparison_type

    @property
    def comparison_subtype(self) -> Enum:
        return self.__comparison_subtype

    @staticmethod
    def __guess_comparison_type(key: str) -> (ComparisonType, Type[Enum]):
        if key is None or key == "":
            return None, None
        if "time" in key.lower() or  "date" in key.lower():
            return DATETIME_COMPARISON_TYPE, DATETIME_COMPARISON_SUBTYPE
        return STRING_COMPARISON_TYPE, STRING_COMPARISON_SUBTYPE

    @staticmethod
    def __guess_comparison_subtype(main_type: ComparisonType) -> Enum:
        if main_type == ComparisonType.BOOLEAN:
            return BOOLEAN_COMPARISON_SUBTYPE
        elif main_type == ComparisonType.DISTANCE:
            return DistanceComparisonType.NUMERIC

    def _normalize_return(self, value: float, min: int = None, max: int = None) -> float:
        """
        Normalize the comparison result based on the weight and reverse flag. The result is normalized to a value
        between 0.0 and 1.0. A lower value means that

        Args:
            value (float): The comparison result to normalize.
            min (int): The minimum value of the comparison result.
            max (int): The maximum value of the comparison result.

        Returns:
            float: The normalized comparison result.
        """
        if min is None:
            min = 0
        if max is None:
            max = 1

        if self.__reverse:
            value = max - value

        if (max - min) == 0:
            return 0.0

        return (value - min) / (max - min) * self.__weight

    def set_key(self, key: str):
        if not isinstance(key, str):
            raise TypeError(f"Expected str, got {type(key)}")
        self.__key = key

    def set_comparison_type(self, comparison_type: ComparisonType):
        if not isinstance(comparison_type, ComparisonType):
            raise TypeError(f"Expected ComparisonType, got {type(comparison_type)}")
        self.__comparison_type = comparison_type

    def set_comparison_subtype(self, comparison_subtype: Enum):
        if not isinstance(comparison_subtype, Enum):
            raise TypeError(f"Expected Enum, got {type(comparison_subtype)}")

        self.__comparison_subtype = comparison_subtype

    def set_reverse(self, reverse: bool):
        if not isinstance(reverse, bool):
            raise TypeError(f"Expected bool, got {type(reverse)}")
        self.__reverse = reverse

    def set_weight(self, weight: float):
        if not isinstance(weight, float):
            raise TypeError(f"Expected float, got {type(weight)}")
        self.__weight = weight

    def compare(self, value1: Any, value2: Any) -> float:
        """
        Compare two values based on the comparison type and subtype. If there is a key set the values are assumed to be
        dictionaries and the key is used to access the value to compare.

        Args:
            value1 (Any): The first value to compare.
            value2 (Any): The second value to compare.

        Returns:
            float: The comparison result as a float between 0.0 and 1.0.

        Raises:
            TypeError: If the comparison type is not supported
        """
        if isinstance(value1, str):
            value1 = html.escape(value1)
        if isinstance(value2, str):
            value2 = html.escape(value2)

        if not isinstance(value1, (str, int, float, bool, dict)):
            raise TypeError(f"Unsupported type: {type(value1)}")
        if not isinstance(value2, (str, int, float, bool, dict)):
            raise TypeError(f"Unsupported type: {type(value2)}")

        if self.__key is not None:
            value1 = value1[self.__key]
            value2 = value2[self.__key]

        if not isinstance(value1, (str, int, float, bool)):
            raise TypeError(f"Unsupported type: {type(value1)}")
        if not isinstance(value2, (str, int, float, bool)):
            raise TypeError(f"Unsupported type: {type(value2)}")

        if self.__comparison_type is None:
            self.set_comparison_type(ComparisonType.BOOLEAN)
            self.set_comparison_subtype(BooleanComparisonType.EQUAL)

        res = None
        if self.__comparison_type == ComparisonType.BOOLEAN:
            res = self.__compare_boolean(value1, value2)
        if self.__comparison_type == ComparisonType.DISTANCE:
            res = self.__compare_distance(value1, value2)

        if res is not None:
            return self._normalize_return(res[0], res[1], res[2])

        raise TypeError(f"Unsupported comparison type: {self.__comparison_type}")

    def __compare_boolean(self, value1: Any, value2: Any) -> Tuple[float, int, int]:
        """
        Compare two boolean values.

        Args:
            value1 (Any): The first value to compare.
            value2 (Any): The second value to compare.

        Returns:
            float: The comparison result as a float between 0.0 and 1.0.
        """
        res = None
        if self.__comparison_subtype == BooleanComparisonType.EQUAL:
            res = 1.0 if value1 == value2 else 0.0
        if self.__comparison_subtype == BooleanComparisonType.NOT_EQUAL:
            res = 0.0 if value1 == value2 else 1.0
        if self.__comparison_subtype == BooleanComparisonType.LESS_THAN:
            res = 1.0 if value1 < value2 else 0.0
        if self.__comparison_subtype == BooleanComparisonType.LESS_THAN_OR_EQUAL:
            res = 1.0 if value1 <= value2 else 0.0
        if self.__comparison_subtype == BooleanComparisonType.GREATER_THAN:
            res = 1.0 if value1 > value2 else 0.0
        if self.__comparison_subtype == BooleanComparisonType.GREATER_THAN_OR_EQUAL:
            res = 1.0 if value1 >= value2 else 0.0

        if res is not None:
            return res, 0, 1

        raise TypeError(f"Unsupported boolean comparison subtype: {self.__comparison_subtype}")

    def __compare_distance(self, value1: Any, value2: Any) ->  Tuple[float, int, int]:
        """
        Compare two values based on a distance metric. Alla distance metrics are normalized to a value between 0.0 and
        1.0. Where 1.0 means the values are completely different and 0.0 means the values are identical.

        Args:
            value1 (Any): The first value to compare.
            value2 (Any): The second value to compare.

        Returns:
            float: The comparison result as a float between 0.0 and 1.0.
        """

        def distance_calculation_with_timeout(func, *args, timeout=5) -> Tuple[float, int, int]:
            result = [None]
            error = [None]

            def wrapper():
                try:
                    result[0] = func(*args)
                except Exception as e:
                    error[0] = e

            thread = threading.Thread(target=wrapper)
            thread.start()
            thread.join(timeout)
            if thread.is_alive():
                raise TimeoutError(f"Distance calculation timed out after {timeout} seconds.")
            if error[0]:
                raise error[0]
            return result[0] if result[0] is not None else (1.0, 0, 1)

        func_ = None
        if self.__comparison_subtype == DistanceComparisonType.LEVENSHTEIN:
            func_ = self.__damerau_levenshtein_distance
        if self.__comparison_subtype == DistanceComparisonType.JACCARD:
            func_ = self.__jaccard_distance
        if self.__comparison_subtype == DistanceComparisonType.SORENSEN_DICE:
            func_ = self.__sorensen_dice_coefficient
        if self.__comparison_subtype == DistanceComparisonType.ALPHABETICAL:
            func_ = self.__alphabetical_distance
        if self.__comparison_subtype == DistanceComparisonType.NUMERIC:
            func_ = lambda x, y: abs(x - y), 0, 1

        if func_ is None:
            raise TypeError(f"Unsupported distance comparison subtype: {self.__comparison_subtype}")

        return distance_calculation_with_timeout(func_, value1, value2)

    def __damerau_levenshtein_distance(self, value1: str, value2: str) -> Tuple[float, int, int]:
        """
        Calculate the Damerau-Levenshtein distance between two strings.
        """
        if not isinstance(value1, str) or not isinstance(value2, str):
            raise TypeError("Damerau-Levenshtein distance requires string input")
        max_len = max(len(value1), len(value2))
        distance = self.__damerau_levenshtein(value1, value2, max_len)
        print(f"\nDistance: {distance}, Max len: {max_len}")
        return distance, 0, max_len

    def __sorensen_dice_coefficient(self, value1: str, value2: str) -> Tuple[float, int, int]:
        """
        Calculate the Sørensen–Dice coefficient between two strings.
        """
        if not isinstance(value1, str) or not isinstance(value2, str):
            raise TypeError("Sørensen–Dice coefficient requires string input")
        if len(value1) == 0 or len(value2) == 0:
            return 1.0, 0, 1
        similarity = SequenceMatcher(None, value1, value2).ratio()
        return 1 - similarity, 0, 1

    def __damerau_levenshtein(self, value1: str, value2: str, max_len: int) -> int:
        """
        Calculate the Damerau-Levenshtein distance between two strings.
        """
        if not isinstance(value1, str) or not isinstance(value2, str):
            raise TypeError("Damerau-Levenshtein distance requires string input")

        if len(value1) == 0 or len(value2) == 0:
            return max_len

        # Create a matrix
        matrix = [[0] * (len(value2) + 1) for _ in range(len(value1) + 1)]

        # Initialize the matrix
        for i in range(len(value1) + 1):
            matrix[i][0] = i
        for j in range(len(value2) + 1):
            matrix[0][j] = j

        # Fill in the matrix
        for i in range(1, len(value1) + 1):
            for j in range(1, len(value2) + 1):
                cost = 0 if value1[i - 1] == value2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,  # Deletion
                    matrix[i][j - 1] + 1,  # Insertion
                    matrix[i - 1][j - 1] + cost  # Substitution
                )
                if i > 1 and j > 1 and value1[i - 1] == value2[j - 2] and value1[i - 2] == value2[j - 1]:
                    matrix[i][j] = min(
                        matrix[i][j],
                        matrix[i - 2][j - 2] + cost  # Transposition
                    )

        return matrix[len(value1)][len(value2)]

    @staticmethod
    def __jaccard_distance(value1: str, value2: str) -> Tuple[float, int, int]:
        """
        Calculate the Jaccard distance between two strings. A distance of 0.0 means the strings are identical and a
        distance of 1.0 means the strings are completely different.

        Args:
            value1 (str): The first string.
            value2 (str): The second string.

        Returns:
            float: The Jaccard distance as a float between 0.0 and 1.0.
        """
        if not isinstance(value1, str) or not isinstance(value2, str):
            raise TypeError("Jaccard distance requires string input")

        if len(value1) == 0 and len(value2) == 0:
            return 1.0, 0, 1

        intersection = len(set(value1).intersection(set(value2)))
        union = len(set(value1).union(set(value2)))
        return 1 - (intersection / union), 0, 1

    @staticmethod
    def __alphabetical_distance(value1: str, value2: str) -> Tuple[float, int, int]:
        """
        Calculate the alphabetical distance between two strings. A distance of 0.0 means the strings are identical and a
        distance of 1.0 means the strings are completely different.

        # Example use:
        # self.__alphabetical_distance("a", "b") == 1
        # self.__alphabetical_distance("b", "a") == 1
        # self.__alphabetical_distance("a", "a") == 0
        # self.__alphabetical_distance("a", "A") == 0
        # self.__alphabetical_distance("a", "bb") == 2
        # self.__alphabetical_distance("a", "aa") == 1
        # self.__alphabetical_distance("a", "c") == 2

        Args:
            value1 (str): The first string.
            value2 (str): The second string.

        Returns:
            float: The alphabetical distance as an integer.
        """
        if not isinstance(value1, str) or not isinstance(value2, str):
            raise TypeError("Alphabetical distance requires string input")

        if len(value1) == 0 and len(value2) == 0:
            return 1.0, 0, max(len(value1), len(value2))

        distance = 0
        for i in range(min(len(value1), len(value2))):
            if value1[i] != value2[i]:
                distance += 1
        distance += abs(len(value1) - len(value2))
        return distance, 0, max(len(value1), len(value2))

