"""
### 需求分析
- 定义一个目标目录路径常量，记 target_path
- 输入 -> 待转移目录的路径，记 source_path
  执行结果 -> source_path 整个目录的文件转移至 target_path 中
- source_path 转移前需要根据 modinfo.lua 中的 version 变量的值来创建目录，如果版本号目录已经存在，则转移失败


"""
import configparser
import sqlite3
from typing import List, Dict

import tqdm
from lupa import lua51

lua = lua51.LuaRuntime()
lua_global = lua.globals()


class ModReleasePreWork:
    pass


def get_sequential_lua_codes(context: Dict = None) -> List[str]:
    context = context or {}  # context if context else {}

    preload = """
    package.path = package.path .. ";{mod_source_dir}\\\\?.lua"
    
    print(package.path)
    local inspect = require("moreitems.lib.thirdparty.__init__").inspect
    local utils = require("moreitems.main").shihao.utils
    print(inspect.inspect(utils))
    """.format(**context)

    return [preload]


# 2025-01-12-19:36，先去更新模组


def config_with_sqlite3(config):
    # 2025-01-13：这也太复杂了吧？
    local_mod_dir_path = config.get("BASE_SETTINGS", "LOCAL_MOD_DIR_PATH")
    mod_dir_name = config.get("VARIABLE_SETTINGS", "MOD_DIR_NAME")

    connect = sqlite3.connect("./mod_release_pre_work.sqlite3")

    connect.execute("CREATE TABLE IF NOT EXISTS local_mod_dir_path (id INTEGER PRIMARY KEY, value TEXT NOT NULL);")
    if connect.execute("SELECT COUNT(*) FROM local_mod_dir_path;").fetchone()[0] == 0:
        connect.execute("INSERT INTO local_mod_dir_path(value) VALUES(?)", (local_mod_dir_path,))
    connect.commit()

    connect.execute("CREATE TABLE IF NOT EXISTS mod_dir_name (id INTEGER PRIMARY KEY, value TEXT NOT NULL);")
    if connect.execute("SELECT COUNT(*) FROM mod_dir_name;").fetchone()[0] == 0:
        connect.execute("INSERT INTO mod_dir_name(value) VALUES(?)", (mod_dir_name,))
    connect.commit()

    connect.close()


def main():
    config = configparser.ConfigParser()
    config.read("./mod_release_pre_work.ini")

    # TODO: 用数据库管理配置
    config_with_sqlite3(config)

    # TODO: ini 可以用类序列化然后操作的
    local_mod_dir_path = config.get("BASE_SETTINGS", "LOCAL_MOD_DIR_PATH")
    mod_dir_name = config.get("VARIABLE_SETTINGS", "MOD_DIR_NAME")

    context = dict(
        mod_source_dir=local_mod_dir_path + rf"\\{mod_dir_name}\\scripts"
    )

    for code in get_sequential_lua_codes(context):
        lua.execute(code)

    # add = lua_global.add # TypeError: 'NoneType' object is not callable
    # add2 = lua_global.add2
    # print(add(1, 2))
    # print(add2(1, 2))


if __name__ == '__main__':
    main()
