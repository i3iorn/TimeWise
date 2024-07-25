import re
from dataclasses import dataclass
from typing import overload, List, Type, Union

from src.exceptions import QueryBuilderException


class SQLValidator:
    @staticmethod
    def validate_identifier(identifier):
        """Validate an SQL identifier, such as a table or column name."""
        if not isinstance(identifier, (str, float, int)):
            raise ValueError(f"Invalid identifier: ({identifier}). Identifiers must be strings.")

        if not re.match(r"^[A-Za-z0-9_]+$", str(identifier)):
            raise ValueError(f"Invalid identifier: ({identifier}). Identifiers must be alphanumeric or underscore "
                             f"characters only.")

    @staticmethod
    def validate_data_type(data_type):
        """Validate an SQL data type."""
        data_types = ["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"]
        if data_type.upper() not in data_types:
            raise ValueError(f"Invalid data type: '{data_type}' is not a valid SQL data type.")

    @staticmethod
    def validate_operator(operator):
        """Validate an SQL operator."""
        operators = ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "NOT IN", "IS", "IS NOT", "BETWEEN", "NOT BETWEEN"]
        if operator.upper() not in operators:
            raise ValueError(f"Invalid operator: '{operator}' is not a valid SQL operator.")

    @staticmethod
    def validate_constraint(constraint):
        """Validate an SQL constraint."""
        constraints = ["PRIMARY KEY", "UNIQUE", "CHECK", "FOREIGN KEY", "NOT NULL", "DEFAULT", "AUTOINCREMENT"]
        if constraint.upper() not in constraints:
            raise ValueError(f"Invalid constraint: '{constraint}' is not a valid SQL constraint.")

    @staticmethod
    def validate_order(order):
        """Validate an SQL ORDER BY direction."""
        directions = ["ASC", "DESC", "RANDOM"]
        if order.upper() not in directions:
            raise ValueError(f"Invalid order: '{order}' is not a valid SQL ORDER BY direction.")

    @staticmethod
    def validate_timings(timing):
        """Validate an SQL trigger timing."""
        timings = ["BEFORE", "AFTER", "INSTEAD OF"]
        if timing.upper() not in timings:
            raise ValueError(f"Invalid timing: '{timing}' is not a valid SQL trigger timing.")

    @staticmethod
    def validate_actions(action):
        """Validate an SQL trigger action."""
        actions = ["INSERT", "UPDATE", "DELETE"]
        if action.upper() not in actions:
            raise ValueError(f"Invalid action: '{action}' is not a valid SQL trigger action.")


class Query:
    """
    Base class for SQL queries that can be built and executed.

    :param table_name: The name of the table to query.
    :type: str
    :param query: The SQL query string.
    :type: str
    :param parameters: A dictionary of parameters to be used in the query.
    :type: dict
    """
    def __init__(self, table_name: str = None):
        SQLValidator.validate_identifier(table_name)

        self._table_name = table_name
        self._query = None
        self.parameters = {}

    @property
    def table_name(self):
        return self._table_name

    @table_name.setter
    def table_name(self, table_name: str):
        self._table_name = table_name

    @property
    def query(self):
        return self._query + ";"

    def with_parameters(self) -> str:
        """
        Return the query with the parameters replaced. Specifically for use in creating views. Introduces a security
        risk if used. Take extra care to sanitize inputs.

        :return: The query with parameters replaced.
        :rtype: str
        """
        query = self._query
        for key, val in self.parameters.items():
            SQLValidator.validate_identifier(val)
            query = query.replace(f":{key}", f"'{val}'")

        return query


class CanBeOrdered:
    """
    Mixin class for queries that can be ordered.

    :param column: The column to order by.
    :type: str
    :param direction: The direction to order by.
    :type: str

    :raises QueryBuilderException: If an invalid column name or direction is provided.

    :return: The query with the order clause added.
    :rtype: Query
    """
    def order_by(self, column: str = "ID", direction: str = "ASC"):
        SQLValidator.validate_identifier(column)
        SQLValidator.validate_order(direction)
        if direction.upper() in ["ASC", "DESC"]:
            self.parameters["order"] = f"{self._query} ORDER BY {column} {direction}"
        elif direction.upper() == "RANDOM":
            self.parameters["order"] = f"{self._query} ORDER BY RANDOM()"
        else:
            raise QueryBuilderException("Invalid column name or direction provided.")
        self._query += " :order"
        return self


class CanBeLimited:
    """
    Mixin class for queries that can be limited.

    :param limit: The number of rows to limit the query to.
    :type: int
    :param offset: The offset to start the limit from.
    :type: int

    :raises QueryBuilderException: If the limit is less than or equal to 0 or the offset is less than 0.

    :return: The query with the limit clause added.
    :rtype: Query
    """
    @overload
    def limit(self, limit: int):
        """
        Limit the number of rows returned by the query.
        """
        ...

    @overload
    def limit(self, limit: int, offset: int):
        """
        Limit the number of rows returned by the query with an offset.
        """
        ...

    def limit(self, limit: int, offset: int = None):
        """
        Limit the number of rows returned by the query with an optional offset.

        :param limit: The number of rows to limit the query to.
        :type: int
        :param offset: The offset to start the limit from.
        :type: int

        :raises QueryBuilderException: If the limit is less than or equal to 0 or the offset is less than 0.

        :return: The query with the limit clause added.
        :rtype: Query
        """
        if limit > 0:
            self.parameters["limit"] = f"{self._query} LIMIT {limit}"
            if offset and offset > 0:
                self.parameters["limit"] += f"{self._query} OFFSET {offset}"
            elif offset and offset < 0:
                raise QueryBuilderException("Offset must be greater than or equal to 0.")
            self._query += " :limit"
        else:
            raise QueryBuilderException("Limit must be greater than 0.")
        return self


class CanBeFiltered:
    """
    Mixin class for queries that can be filtered.

    :param conditions: A dictionary of conditions to filter the query by.
    :type: dict
    :param column: The column to filter by.
    :type: str
    :param value: The value to filter by.
    :type: str

    :raises QueryBuilderException: If an invalid column name is provided or no conditions are provided.

    :return: The query with the where clause added.
    :rtype: Query
    """
    @overload
    def where(self, conditions: dict):
        """
        Filter the query based on the conditions provided.
        """
        ...

    @overload
    def where(self, column: str, value: int):
        """
        Filter the query based on the column and value provided.
        """
        ...

    def where(self, conditions: dict = None, column: str = None, value: str = None):
        """
        Filter the query based on the conditions provided or the column and value provided.

        :param conditions: A dictionary of conditions to filter the query by.
        :type: dict
        :param column: The column to filter by.
        :type: str
        :param value: The value to filter by.
        :type: str

        :raises QueryBuilderException: If an invalid column name is provided or no conditions are provided.

        :return: The query with the where clause added.
        :rtype: Query
        """
        if conditions:
            [SQLValidator.validate_identifier(key) for key in conditions.keys()]

            if not all([key.replace("_", "").isalnum() for key in conditions.keys()]):
                raise QueryBuilderException("Invalid column name provided.")
            self._query = f"{self._query} WHERE {' AND '.join([f'{key} = :{key}' for key in conditions.keys()])}"
            self.parameters.update(conditions)

        elif column and value:
            SQLValidator.validate_identifier(column)
            self._query = f"{self._query} WHERE {column} = :{column}"
            self.parameters[column] = value

        else:
            raise QueryBuilderException("No conditions provided for where clause.")

        return self


class CanBeJoined:
    """
    Mixin class for queries that can be joined.

    :param join_type: The type of join to perform.
    :type: str
    :param table: The table to join.
    :type: str
    :param on: The column to join on.
    :type: str

    :raises QueryBuilderException: If an invalid join type is provided.

    :return: The query with the join clause added.
    :rtype: Query
    """
    def join(self, join_type: str, table: str, on: str):
        """
        Join the query with another table based on the join type and column provided.

        :param join_type: The type of join to perform.
        :type: str
        :param table: The table to join.
        :type: str
        :param on: The column to join on.
        :type: str

        :raises QueryBuilderException: If an invalid join type is provided.

        :return: The query with the join clause added.
        :rtype: Query
        """
        SQLValidator.validate_identifier(table)
        join_types = ["INNER", "LEFT OUTER", "RIGHT OUTER", "FULL OUTER"]
        if join_type.upper() not in join_types:
            raise QueryBuilderException(f"Invalid join type: '{join_type}'. Valid options are: {', '.join(join_types)}")

        self._query += f" {join_type.upper()} JOIN {table} ON {on}"
        return self


class Select(CanBeOrdered, CanBeLimited, CanBeFiltered, Query):
    """
    Class for building SELECT queries.

    :param table_name: The name of the table to query.
    :type: str

    :param columns: The columns to select.
    :type: list
    :param conditions: A dictionary of conditions to filter the query by.
    :type: dict
    :param order_by: The column to order by.
    :type: str
    :param limit: The number of rows to limit the query to.
    :type: int
    :param offset: The offset to start the limit from.
    :type: int

    :return: The query string for the SELECT query.
    :rtype: str
    """
    def __init__(
            self,
            table_name: str = None,
            columns: List[str] = None,
            conditions: dict = None,
            order_by: str = None,
            limit: int = None,
            offset: int = None
    ):
        if not table_name:
            raise QueryBuilderException("No table name provided for select query.")

        super().__init__(table_name)
        self._query = f"SELECT * FROM {table_name}"

        if columns:
            self._query = self._query.replace("*", ", ".join(columns))

        if conditions:
            self.where(conditions=conditions)

        if order_by:
            self.order_by(order_by)

        if limit:
            self.limit(limit, offset)


class Insert(Query):
    """
    Class for building INSERT queries.

    :param table_name: The name of the table to insert into.
    :type: str
    :param kwargs: The columns and values to insert.
    :type: dict

    :return: The query string for the INSERT query.
    :rtype: str
    """
    def __init__(self, table_name: str, **kwargs):
        super().__init__(table_name)
        self._query = f"INSERT {'OR IGNORE ' if kwargs.pop("drop_duplicate", False) else ''}INTO {table_name}"

        if not kwargs:
            raise QueryBuilderException("No columns provided for insert query.")

        for key, value in kwargs.items():
            if isinstance(value, dict):
                where = Select(**value).query

        self._query = f"{self._query} ({', '.join(kwargs.keys())}) VALUES ({', '.join([f':{key}' for key in kwargs.keys() if key != 'where'])})"

        self.parameters = kwargs


class Update(CanBeFiltered, Query):
    """
    Class for building UPDATE queries.

    :param table_name: The name of the table to update.
    :type: str
    :param kwargs: The columns and values to update.
    :type: dict
    :param conditions: A dictionary of conditions to filter the query by.
    :type: dict

    :return: The query string for the UPDATE query.
    :rtype: str
    """
    def __init__(self, table_name: str, **kwargs):
        super().__init__(table_name)
        self._query = f"UPDATE {table_name} SET"

        if "conditions" in kwargs:
            self.where(conditions=kwargs.pop("conditions"))

        for key, val in kwargs.items():
            self._query = f"{self._query} {key} = :{key},"
            self.parameters[key] = val
        self._query = self._query[:-1]


class Delete(CanBeFiltered, Query):
    """
    Class for building DELETE queries.

    :param table_name: The name of the table to delete from.
    :type: str
    :param conditions: A dictionary of conditions to filter the query by.
    :type: dict

    :raises QueryBuilderException: If no conditions are provided.

    :return: The query string for the DELETE query.
    :rtype: str
    """
    def __init__(self, table_name: str, conditions: dict = None):
        super().__init__(table_name)
        self._query = f"DELETE FROM {table_name}"

        if conditions:
            self.where(conditions=conditions)
        else:
            raise QueryBuilderException("No conditions provided for delete query.")


@dataclass
class Column:
    """
    Dataclass for creating table columns.

    :param column_name: The name of the column.
    :type: str
    :param data_type: The data type of the column.
    :type: str
    :param primary_key: Whether the column is a primary key.
    :type: bool
    :param auto_increment: Whether the column is auto-incrementing.
    :type: bool
    :param allow_null: Whether the column allows NULL values.
    :type: bool
    :param default: The default value for the column.
    :type: str

    :raises ValueError: If an invalid column name is provided.

    :return: The query string for creating the column.
    :rtype: str
    """
    column_name: str
    data_type: str = "TEXT"
    primary_key: bool = False
    auto_increment: bool = False
    allow_null: bool = True
    default: str = None

    def __post_init__(self):
        """
        Validate the column data.

        :return: None
        """
        SQLValidator.validate_identifier(self.column_name)
        SQLValidator.validate_identifier(self.default) if self.default else None
        SQLValidator.validate_data_type(self.data_type)

        assert not self.auto_increment or self.primary_key, "Auto-increment columns must be primary keys."
        assert not self.default or not self.allow_null, "Columns with default values cannot allow NULL."
        assert not self.default or self.data_type.upper() in ["TEXT", "INTEGER"], "Default values must match the data type."

    def __repr__(self):
        """
        Return the query string for creating the column.
        """
        return (
            f"{self.column_name} "
            f"{self.data_type} "
            f"{'PRIMARY KEY' if self.primary_key else ''} "
            f"{'AUTOINCREMENT' if self.auto_increment else ''} "
            f"{'NOT NULL' if not self.allow_null else ''} "
            f"{'DEFAULT ' + str(self.default).replace('\'', '') if self.default else ''}"
        ).replace("  ", " ").strip()


@dataclass
class ForeignKey:
    """
    Dataclass for creating foreign key constraints.

    :param column: The column in the current table.
    :type: str
    :param references: The table in the foreign key.
    :type: str
    :param ref_column: The column in the foreign key table.
    :type: str

    :raises ValueError: If an invalid column name is provided.

    :return: The query string for creating the foreign key constraint.
    :rtype: str
    """
    column: str             # Column in the current table
    references: str    # Table in the foreign key
    ref_column: str   # Column in the foreign key table

    def __post_init__(self):
        SQLValidator.validate_identifier(self.column)
        SQLValidator.validate_identifier(self.references)
        SQLValidator.validate_identifier(self.ref_column)

    def __repr__(self):
        return f"FOREIGN KEY ({self.column}) REFERENCES {self.references}({self.ref_column})"


@dataclass
class UniqueConstraint:
    """
    Dataclass for creating unique constraints.

    :param columns: The columns to create the unique constraint on.
    :type: list

    :raises ValueError: If an invalid column name is provided.

    :return: The query string for creating the unique constraint.
    :rtype: str
    """
    columns: List[str]

    def __post_init__(self):
        [SQLValidator.validate_identifier(col) for col in self.columns]

    def __repr__(self):
        return f"UNIQUE ({', '.join(self.columns)})"


@dataclass
class CheckConstraint:
    """
    Dataclass for creating check constraints.

    :param constraint: The column to create the check constraint on.
    :type: str
    :param operator: The operator to use in the check constraint.
    :type: str
    :param value: The value to check against.
    :type: str

    :raises ValueError: If an invalid column name is provided.

    :return: The query string for creating the check constraint.
    :rtype: str
    """
    constraint: str
    operator: str
    value: str

    def __post_init__(self):
        SQLValidator.validate_operator(self.operator)
        SQLValidator.validate_identifier(self.constraint)

    def __repr__(self):
        return f"CHECK ({self.constraint} {self.operator} {self.value})"


class CreateTable(Query):
    """
    Class for building CREATE TABLE queries.

    :param table_name: The name of the table to create.
    :type: str
    :param columns: The columns to create in the table.
    :type: list
    :param foreign_keys: The foreign key constraints to add to the table.
    :type: list
    :param unique_constraints: The unique constraints to add to the table.
    :type: list
    :param check_constraints: The check constraints to add to the table.
    :type: list
    :param can_exist: Whether the table can exist before creating it.
    :type: bool

    :raises ValueError: If an invalid column name is provided.

    :return: The query string for creating the table.
    :rtype: str
    """
    def __init__(
            self,
            table_name: str,
            columns: List[Union[Column | dict]],
            foreign_keys: List[Union[ForeignKey | dict]] = None,
            unique_constraints: List[Union[UniqueConstraint | list]] = None,
            check_constraints: List[Union[CheckConstraint | dict]] = None,
            can_exist: bool = False
    ):
        columns = [col if isinstance(col, Column) else Column(**col) for col in columns]
        columns.extend([
            Column("created_at", default="CURRENT_TIMESTAMP", allow_null=False),
            Column("updated_at")
        ])
        super().__init__(table_name)
        self._query = f"CREATE TABLE {'IF NOT EXISTS ' if can_exist else ''}{table_name}"

        self._query = f"{self._query} ({', '.join([str(col) for col in columns])}"

        if foreign_keys:
            foreign_keys = [fk if isinstance(fk, ForeignKey) else ForeignKey(**fk) for fk in foreign_keys]
            self._query = f"{self._query}, {', '.join([str(fk) for fk in foreign_keys])}"

        if unique_constraints:
            unique_constraints = [uc if isinstance(uc, UniqueConstraint) else UniqueConstraint(uc) for uc in unique_constraints]
            self._query = f"{self._query}, {', '.join([str(uc) for uc in unique_constraints])}"

        if check_constraints:
            check_constraints = [cc if isinstance(cc, CheckConstraint) else CheckConstraint(**cc) for cc in check_constraints]
            self._query = f"{self._query}, {', '.join([str(cc) for cc in check_constraints])}"

        self._query = f"{self._query})"


class CreateIndex(Query):
    """
    Class for building CREATE INDEX queries.

    :param table_name: The name of the table to create the index on.
    :type: str
    :param column: The column to create the index on.
    :type: str
    :param unique: Whether the index should be unique.
    :type: bool

    :raises ValueError: If an invalid column name is provided.

    :return: The query string for creating the index.
    :rtype: str
    """
    def __init__(self, table_name: str, column: str, unique: bool = False):
        super().__init__(table_name)
        SQLValidator.validate_identifier(column)

        index_name = f"idx_{self.table_name}_{column}"
        self._query = f"CREATE {'UNIQUE' if unique else ''} INDEX {index_name} ON {table_name} ({column})"
        self.parameters = {}


class CreateTrigger:
    """
    Class for building CREATE TRIGGER queries.

    :param trigger_name: The name of the trigger.
    :type: str
    :param table_name: The name of the table to create the trigger on.
    :type: str
    :param action: The action to trigger the trigger.
    :type: str
    :param timing: The timing of the trigger.
    :type: str
    :param body: The body of the trigger.
    :type: str

    :raises ValueError: If an invalid table name is provided.

    :return: The query string for creating the trigger.
    :rtype: str
    """
    def __init__(
            self,
            trigger_name: str,
            table_name: str,
            action: str,
            timing: str,
            body: "Query",
            can_exist=True
    ):
        SQLValidator.validate_identifier(table_name)
        SQLValidator.validate_identifier(trigger_name)
        SQLValidator.validate_actions(action)
        SQLValidator.validate_timings(timing)

        self.query = f"CREATE TRIGGER {'IF NOT EXISTS ' if can_exist else ''}{trigger_name} {timing.upper()} {action.upper()} ON {table_name} BEGIN {body.with_parameters()} END"
