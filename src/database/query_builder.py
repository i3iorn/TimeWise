from dataclasses import dataclass
from enum import Enum
from typing import overload, List

from src.exceptions import QueryBuilderException


class Query:
    def __call__(self):
        return self.build()

    @property
    def table_name(self):
        return self._table_name

    @table_name.setter
    def table_name(self, table_name: str):
        if not table_name:
            raise QueryBuilderException("Table name cannot be empty.")
        if not all(c.isalnum or c == "_" for c in table_name):
            raise QueryBuilderException("Table name can only contain alphanumeric characters.")

        self._table_name = table_name

    def with_parameters(self):
        query = self.query
        for key, val in self.parameters.items():
            query = query.replace(f":{key}", f"'{val}'")

        return query


class Order(Enum):
    ASC = "ASC"
    DESC = "DESC"
    RANDOM = "RANDOM"


class CanBeOrdered:
    def order_by(self, column: str = "ID", direction: str = "ASC"):
        if self.query:
            if column.isalnum() and direction.upper() in ["ASC", "DESC"]:
                self.parameters["order"] = f"{self.query} ORDER BY {column} {direction}"
            elif column.isalnum() and direction.upper() == "RANDOM":
                self.parameters["order"] = f"{self.query} ORDER BY RANDOM()"
            else:
                raise QueryBuilderException("Invalid column name or direction provided.")
            self.query += " :order"
        else:
            raise QueryBuilderException("No active query.")


class CanBeLimited:
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
        if self.query:
            if limit > 0:
                self.parameters["limit"] = f"{self.query} LIMIT {limit}"
                if offset and offset > 0:
                    self.parameters["limit"] += f"{self.query} OFFSET {offset}"
                elif offset and offset < 0:
                    raise QueryBuilderException("Offset must be greater than or equal to 0.")
                self.query += " :limit"
            else:
                raise QueryBuilderException("Limit must be greater than 0.")
        else:
            raise QueryBuilderException("No active query.")


class CanBeFiltered:
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
        if self.query:
            if conditions:
                if not all([key.replace("_", "").isalnum() for key in conditions.keys()]):
                    raise QueryBuilderException("Invalid column name provided.")
                self.query = f"{self.query} WHERE {' AND '.join([f'{key} = :{key}' for key in conditions.keys()])}"
                self.parameters.update(conditions)
            elif column and value:
                if column.isalnum():
                    self.query = f"{self.query} WHERE {column} = :{column}"
                    self.parameters[column] = value
                else:
                    raise QueryBuilderException("Invalid column name provided.")
        else:
            raise QueryBuilderException("No active query.")


class Select(CanBeOrdered, CanBeLimited, CanBeFiltered, Query):
    def __init__(
            self,
            table_name: str,
            columns: list = None,
            conditions: dict = None,
            order_by: str = None,
            limit: int = None,
            offset: int = None
    ):
        self.table_name = table_name
        self.query = f"SELECT * FROM {table_name}"
        self.parameters = {}

        if columns:
            self.query = self.query.replace("*", ", ".join(columns))

        if conditions:
            self.where(conditions=conditions)

        if order_by:
            self.order_by(order_by)

        if limit:
            self.limit(limit, offset)


class Insert(Query):
    def __init__(self, table_name: str, **kwargs):
        self.table_name = table_name
        self.query = f"INSERT INTO {table_name}"
        self.parameters = {}

        self.query = f"{self.query} ({', '.join(kwargs.keys())}) VALUES ({', '.join([f':{key}' for key in kwargs.keys()])})"
        self.parameters = kwargs


class Update(CanBeFiltered, Query):
    def __init__(self, table_name: str, **kwargs):
        self.table_name = table_name
        self.query = f"UPDATE {table_name} SET"
        self.parameters = {}

        if "conditions" in kwargs:
            self.where(conditions=kwargs.pop("conditions"))

        for key, val in kwargs.items():
            self.query = f"{self.query} {key} = :{key},"
            self.parameters[key] = val
        self.query = self.query[:-1]


class Delete(CanBeFiltered, Query):
    def __init__(self, table_name: str, conditions: dict = None):
        self.table_name = table_name
        self.query = f"DELETE FROM {table_name}"
        self.parameters = {}

        if conditions:
            self.where(conditions=conditions)
        else:
            raise QueryBuilderException("No conditions provided for delete query.")


@dataclass
class Column:
    name: str
    data_type: str = "TEXT"
    primary_key: bool = False
    auto_increment: bool = False
    allow_null: bool = True
    default: str = None

    def __post_init__(self):
        if not all(c.isalnum() or c == "_" for c in self.name):
            raise QueryBuilderException("Invalid column name provided.")
        if self.data_type.upper() not in ["TEXT", "INTEGER", "REAL", "BLOB"]:
            raise QueryBuilderException("Invalid data type provided.")
        if self.default and self.data_type.upper() == "INTEGER":
            try:
                int(self.default)
            except ValueError:
                raise QueryBuilderException("Default value must be an integer.")
        if self.default and self.data_type.upper() == "REAL":
            try:
                float(self.default)
            except ValueError:
                raise QueryBuilderException("Default value must be a float.")
        if self.default and self.data_type.upper() == "TEXT":
            self.default = f"'{self.default}'"

        if self.name.endswith("_at"):
            self.default = "CURRENT_TIMESTAMP"

    def __repr__(self):
        """
        Return the query string for creating the column.
        """
        return (
            f"{self.name} "
            f"{self.data_type} "
            f"{'PRIMARY KEY' if self.primary_key else ''} "
            f"{'AUTOINCREMENT' if self.auto_increment else ''} "
            f"{'NOT NULL' if not self.allow_null else ''} "
            f"{'DEFAULT ' + str(self.default).replace('\'', '') if self.default else ''}"
        ).replace("  ", " ").strip()


@dataclass
class ForeignKey:
    column: str             # Column in the current table
    reference_table: str    # Table in the foreign key
    reference_column: str   # Column in the foreign key table


@dataclass
class UniqueConstraint:
    columns: List[str]


@dataclass
class CheckConstraint:
    column: str
    operator: str
    value: str


class CreateTable(Query):
    def __init__(
            self,
            table_name: str,
            columns: List[Column],
            foreign_keys: List[ForeignKey] = None,
            unique_constraints: List[UniqueConstraint] = None,
            check_constraints: List[CheckConstraint] = None,
            can_exist: bool = False
    ):
        self.table_name = table_name
        self.query = f"CREATE TABLE {table_name}"
        self.parameters = {}

        if can_exist:
            self.query = f"{self.query} IF NOT EXISTS"

        self.query = f"{self.query} ({', '.join([str(col) for col in columns])}"
        if foreign_keys:
            for fk in foreign_keys:
                self.query = f"{self.query}, FOREIGN KEY ({fk.column}) REFERENCES {fk.reference_table}({fk.reference_column})"
        if unique_constraints:
            for uc in unique_constraints:
                self.query = f"{self.query}, UNIQUE ({', '.join(uc.columns)})"
        if check_constraints:
            for cc in check_constraints:
                self.query = f"{self.query}, CHECK ({cc.column} {cc.operator} {cc.value})"

        self.query = f"{self.query})"
        self.query = self.query.replace("  ", " ")
        self.query = self.query.replace(", )", ")")
        self.query = self.query.replace(" ,", ",")


class CreateView(Query):
    def __init__(self, view_name: str, query: str):
        self.view_name = view_name
        self.query = f"CREATE VIEW {view_name} AS {query}"
        self.parameters = {}


class CreateIndex(Query):
    def __init__(self, table_name: str, column: str, unique: bool = False):
        self.table_name = table_name
        if not column.isalnum():
            raise QueryBuilderException("Invalid column name provided.")

        index_name = f"idx_{self.table_name}_{column}"
        self.query = f"CREATE {'UNIQUE' if unique else ''} INDEX {index_name} ON {table_name} ({column})"
        self.parameters = {}
