"""
### 需求分析
- 定义一个目标目录路径常量，记 target_path
- 输入 -> 待转移目录的路径，记 source_path
  执行结果 -> source_path 整个目录的文件转移至 target_path 中
- source_path 转移前需要根据 modinfo.lua 中的 version 变量的值来创建目录，如果版本号目录已经存在，则转移失败


"""
import configparser
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

def main():
    config = configparser.ConfigParser()
    config.read("./mod_release_pre_work.ini")

    # TODO: ini 可以用类序列化然后操作的
    local_mod_dir_path = config.get("BASE_SETTINGS", "LOCAL_MOD_DIR_PATH")
    mod_dir_name = config.get("VARIABLE_SETTINGS", "MOD_DIR_NAME")

    context = dict(
        mod_source_dir=config.get("SETTINGS", "MOD_SOURCE_DIR")
    )

    for code in get_sequential_lua_codes(context):
        lua.execute(code)

    # add = lua_global.add # TypeError: 'NoneType' object is not callable
    # add2 = lua_global.add2
    # print(add(1, 2))
    # print(add2(1, 2))


if __name__ == '__main__':
    main()
