__all__ = ["sqlite_cache"]

import os.path
import pprint
import re
import sqlite3
import warnings
from typing import Union

try:
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured

    print(settings.BASE_DIR)  # 触发 ImproperlyConfigured error
except (ImportError, ImproperlyConfigured,):
    from types import SimpleNamespace
    from pathlib import Path

    settings = SimpleNamespace(BASE_DIR=Path("."))


class SqliteCache:
    class _Helper:

        @staticmethod
        def is_float(s):
            return re.match(r'^-?\d+(?:\.\d+)?$', s) is not None or re.match(r'^-?\d+\.\d+e[+-]?\d+$', s) is not None

        @staticmethod
        def is_int(s):
            return re.match(r'^-?\d+$', s) is not None

        @staticmethod
        def check_key(arg):
            if not isinstance(arg, str):
                raise ValueError("键必须是字符串类型")

        @staticmethod
        def check_value(arg):
            if not isinstance(arg, (int, float, str,)):
                raise ValueError("键值必须是整数或浮点数或字符串类型")

        @staticmethod
        def create_tables(connect: sqlite3.Connection):
            connect.execute("""
            CREATE TABLE IF NOT EXISTS t_cache_kv (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- 使用 `AUTOINCREMENT`，SQLite 会保证不会重用已删除的 `id` 值
                key TEXT NOT NULL,
                value TEXT
            );
            """)
            connect.commit()

    def __init__(self):
        self._connect = sqlite3.connect(str(settings.BASE_DIR / "sqlite_cache.sqlite3"))
        self._helper = self._Helper()

        self._helper.create_tables(self._connect)

    def set(self, key: str, value: Union[int, float, str]):
        self._helper.check_key(key)
        self._helper.check_value(value)

        value = value if isinstance(value, str) else str(value)
        cursor = self._connect.execute("SELECT * FROM t_cache_kv WHERE key = ?", (key,))
        if cursor.fetchall():
            self._connect.execute("UPDATE t_cache_kv SET value = ? WHERE key = ?", (value, key,))
        else:
            self._connect.execute("INSERT INTO t_cache_kv (key, value) VALUES (?, ?)", (key, value,))
        self._connect.commit()

    def get(self, key: str) -> Union[None, int, float, str]:
        self._helper.check_key(key)

        cursor = self._connect.execute("SELECT value FROM t_cache_kv WHERE key = ?", (key,))
        fetched_data = cursor.fetchall()
        if not fetched_data:
            return None

        value = fetched_data[0][0]
        if self._helper.is_int(value):
            value = int(value)
        elif self._helper.is_float(value):
            value = float(value)
        return value


sqlite_cache = SqliteCache()

if __name__ == '__main__':
    def main():
        key = "count"
        val = sqlite_cache.get(key)
        if val is None:
            sqlite_cache.set(key, 1)
        else:
            sqlite_cache.set(key, val + 1)
        print(sqlite_cache.get(key))

        cursor = sqlite_cache._connect.execute("SELECT * FROM t_cache_kv")
        pprint.pprint(cursor.fetchall())

        warnings.warn("123")


    main()
