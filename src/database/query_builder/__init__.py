from typing import overload

from src.database.query_builder.exceptions import QueryBuilderException


class QueryBuilder:
    def __init__(self, table_name: str = None):
        self._table_name = table_name or ""
        self.query = ""
        self.parameters = {}

    @property
    def table_name(self):
        return self._table_name

    @table_name.setter
    def table_name(self, table_name: str):
        self._table_name = table_name

    def build(self):
        if not self.table_name:
            raise QueryBuilderException("No table name provided.")

        self.query = self.query.replace(":table_name", self.table_name)
        return self.query, self.parameters


class CanBeOrdered:
    def order_by(self, column: str = "ID", direction: str = "ASC"):
        if self.query:
            if column.isalnum() and direction.upper() in ["ASC", "DESC"]:
                self.query = f"{self.query} ORDER BY {column} {direction}"
                return self
            else:
                raise QueryBuilderException("Invalid column name or direction provided.")
        else:
            raise QueryBuilderException("No active query.")


class CanHaveConditions:
    def where(self, query: dict):
        if self.query:
            conditions = " AND ".join([f"{key} = '{value}'" for key, value in query.items()])
            self.query = f"{self.query} WHERE {conditions}"
            return self
        else:
            raise QueryBuilderException("No active query.")


class Select(CanBeOrdered, CanHaveConditions, QueryBuilder):
    @overload
    def main(self):
        ...

    @overload
    def main(self, columns: list):
        ...

    @overload
    def main(self, columns: list, alias: list):
        ...

    @overload
    def main(self, column_aliases: dict):
        ...

    def main(self, columns: list = None, alias: list = None, column_aliases: dict = None):
        if self.query:
            raise QueryBuilderException("Query already exists.")

        # Create a list of all provided values
        provided_values = columns + alias + list(column_aliases.keys()) + list(column_aliases.values())

        # Check if any value contain an invalid characters
        if any([value for value in provided_values if not value.isalnum()]):
            raise QueryBuilderException("Invalid column name or alias provided.")

        if column_aliases:
            columns = ", ".join([f"{key} AS {value}" for key, value in column_aliases.items()])
        elif alias and columns:
            columns = ", ".join([f"{column} AS {alias}" for column, alias in zip(columns, alias)])
        elif columns:
            columns = ", ".join(columns)
        else:
            columns = "*"

        self.query = f"SELECT {columns} FROM :table_name"
        return self

    def as_view(self, view_name: str):
        if self.query:
            self.query = f"CREATE VIEW {view_name} AS {self.query}"
            return self
        else:
            raise QueryBuilderException("No active query.")


class Insert(CanHaveConditions, QueryBuilder):
    def main(self, data: dict):
        if self.query:
            raise QueryBuilderException("Query already exists.")

        columns = ", ".join(data.keys())
        values = ", ".join([f"'{value}'" for value in data.values()])

        self.query = f"INSERT INTO :table_name ({columns}) VALUES ({values})"
        return self


class Update(CanHaveConditions, QueryBuilder):
    def main(self, data: dict):
        if self.query:
            raise QueryBuilderException("Query already exists.")

        columns = ", ".join([f"{key} = '{value}'" for key, value in data.items()])

        self.query = f"UPDATE :table_name SET {columns}"
        return self


class Delete(CanHaveConditions, QueryBuilder):
    def main(self):
        if self.query:
            raise QueryBuilderException("Query already exists.")

        self.query = f"DELETE FROM :table_name"
        return self

    def build(self):
        if len(self.parameters) == 0 and not hasattr(self, "force_delete"):
            raise QueryBuilderException("No conditions provided. Either provide conditions or use force_delete.")

        return super().build()


class CreateTable(QueryBuilder):
    def main(
            self,
            columns: dict,
            primary_key: str = "ID",
            auto_increment: bool = True,
            foreign_keys: dict = None,
            unique_keys: list = None,
            check_constraints: list = None,
            indexes: list = None,
            table_constraints: list = None,
            without_rowid: bool = False,
            temporary: bool = False,
            if_not_exists: bool = False
    ):
        if self.query:
            raise QueryBuilderException("Query already exists.")

        if not columns:
            raise QueryBuilderException("No columns provided.")

        columns = ", ".join([f"{key} {value}" for key, value in columns.items()])

        if foreign_keys:
            foreign_keys = ", ".join([f"FOREIGN KEY ({key}) REFERENCES {value}" for key, value in foreign_keys.items()])

        if unique_keys:
            unique_keys = ", ".join([f"UNIQUE ({key})" for key in unique_keys])

        if check_constraints:
            check_constraints = ", ".join(check_constraints)

        if indexes:
            indexes = ", ".join(indexes)

        if table_constraints:
            table_constraints = ", ".join(table_constraints)

        self.query = f"CREATE {'TEMPORARY' if temporary else ''} TABLE {'IF NOT EXISTS' if if_not_exists else ''} {self.table_name} ({columns}"
        self.query = f"{self.query}, PRIMARY KEY ({primary_key})" if primary_key else self.query
        self.query = f"{self.query}, FOREIGN KEY ({foreign_keys})" if foreign_keys else self.query
        self.query = f"{self.query}, UNIQUE ({unique_keys})" if unique_keys else self.query
        self.query = f"{self.query}, CHECK ({check_constraints})" if check_constraints else self.query
        self.query = f"{self.query}, {indexes}" if indexes else self.query
        self.query = f"{self.query}, {table_constraints}" if table_constraints else self.query
        self.query = f"{self.query}) {'WITHOUT ROWID' if without_rowid else ''}"
        return self


class DropTable(QueryBuilder):
    def main(self, if_exists: bool = False):
        if self.query:
            raise QueryBuilderException("Query already exists.")

        self.query = f"DROP TABLE {'IF EXISTS' if if_exists else ''} :table_name"
        return self


class CreateIndex(QueryBuilder):
    def main(self, name: str, columns: list, unique: bool = False):
        if self.query:
            raise QueryBuilderException("Query already exists.")

        columns = ", ".join(columns)

        self.query = f"CREATE {'UNIQUE' if unique else ''} INDEX {name} ON :table_name ({columns})"
        return self


class DropIndex(QueryBuilder):
    def main(self, name: str):
        if self.query:
            raise QueryBuilderException("Query already exists.")

        self.query = f"DROP INDEX {name}"
        return self
