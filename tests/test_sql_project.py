import contextlib
import sqlite3
from typing import List, Set


class DataBaseManager:
    DATABASES = {
        "t_si_kv": """
        CREATE TABLE IF NOT EXISTS t_si_kv (
        id INTEGER PRIMARY KEY,
        key TEXT NOT NULL ,
        value INTEGER
        );
        """,
        "t_ss_kv": """
            CREATE TABLE IF NOT EXISTS t_ss_kv (
            id INTEGER PRIMARY KEY,
            key TEXT NOT NULL,
            value TEXT
            );
        """,
    }

    DEBUG = True

    def __init__(self):
        self._connect = sqlite3.connect("./test_sql_project.sqlite3")
        self._created_tables: Set[str] = set()

    def get_connect(self):
        return self._connect

    @contextlib.contextmanager
    def get_auto_commit_connect_contextmanager(self):
        yield self._connect
        self._connect.commit()

    def create_table(self, table_name: str):
        # if self.DEBUG:
        #     self._connect.execute("DROP TABLE IF EXISTS " + table_name)
        self._created_tables.add(table_name)
        self._connect.execute(self.fetch_table_creation_sql(table_name))

    # ---------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def fetch_table_creation_sql(table_name: str):
        res = DataBaseManager.DATABASES.get(table_name)
        assert res is not None
        return res


def main():
    manager = DataBaseManager()

    for table_name in manager.DATABASES.keys():
        manager.create_table(table_name)

    with manager.get_auto_commit_connect_contextmanager() as connect:
        cursor = connect.execute("SELECT id from t_si_kv WHERE key = ?", "a")
        res = cursor.fetchall()
        if not res:
            connect.execute("INSERT INTO t_si_kv (key, value) VALUES ('a', 1)")
        else:
            connect.execute("UPDATE t_si_kv SET value = value + 1 WHERE key = ?", "a")
        print(connect.execute("SELECT * from t_si_kv").fetchall())

    # TODO: 牛客网刷 sql


if __name__ == '__main__':
    main()
