from typing import List, Tuple


class Condition:
    def __init__(self, column: str, operator: str, value):
        self.column = column
        self.operator = operator
        self.value = value

    def __str__(self):
        return f"{self.column} {self.operator} {self.value}"


class Database:
    def create_table(
            self,
            table_name: str,
            columns: list,
            primary_key=None,
            foreign_key=None,
            foreign_table=None,
            foreign_column=None,
            unique=None,
            not_null=None,
            check=None,
            default=None,
            can_exist=False
    ):
        """Create a table in the database"""
        # Consolidate conditions into the columns list
        conditions = [
            f"PRIMARY KEY ({primary_key})" if primary_key else "",
            f"FOREIGN KEY ({foreign_key}) REFERENCES {foreign_table}({foreign_column})" if foreign_key and foreign_table and foreign_column else "",
            f"UNIQUE ({unique})" if unique else "",
            f"NOT NULL ({not_null})" if not_null else "",
            f"CHECK ({check})" if check else "",
            f"DEFAULT ({default})" if default else ""
        ]
        # Filter out empty strings and join all conditions
        conditions_str = ", ".join(filter(None, conditions))
        # Combine columns and conditions
        all_columns_str = ", ".join(columns + [conditions_str]) if conditions_str else ", ".join(columns)
        # Form the query with or without IF NOT EXISTS
        query = f"CREATE TABLE {'IF NOT EXISTS ' if can_exist else ''}{table_name} ({all_columns_str})"
        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info(f"Table '{table_name}' created")

    def drop_table(self, table_name: str):
        """Drop a table from the database"""
        query = f"DROP TABLE {table_name}"
        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info(f"Table '{table_name}' dropped")

    def insert(self, table_name: str, values: dict):
        """Insert values into a table"""
        columns = ", ".join(values.keys())
        placeholders = ", ".join("?" * len(values))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, tuple(values.values()))
        self.connection.commit()
        self.logger.info(f"Values inserted into table '{table_name}'")

    def select(
            self,
            table_name: str,
            columns: List[str],
            conditions: List[Tuple],
            limit: int = None
    ):
        """Select values from a table"""
        columns_str = ", ".join(columns)
        if len(conditions) == 4:
            query = f"SELECT {columns_str} FROM {table_name} WHERE {conditions[1]} {conditions[2]} ? {conditions[0]} {conditions[3]}"
            self.cursor.execute(query, (conditions[3],))