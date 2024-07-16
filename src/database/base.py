class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name

    # Connect
    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    # CRUD
    def select(self, columns: list = None, alias: list = None, column_aliases: dict = None):
        raise NotImplementedError

    def insert(self, data: dict):
        raise NotImplementedError

    def update(self, query: dict, data: dict):
        raise NotImplementedError

    def delete(self, query: dict):
        raise NotImplementedError

    # Other
    def drop(self):
        raise NotImplementedError

    def find(self, query: dict):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def count(self):
        raise NotImplementedError

    # Dunder
    def __str__(self):
        return self.db_name

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()
        return True

    def __del__(self):
        self.disconnect()
        return True


