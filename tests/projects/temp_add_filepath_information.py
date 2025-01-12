"""
### 控制流图（CFG）
flowchart TD
    A[开始] --> B{剪切板内容是否变化}
    B -->|是| C[重置超时计时器]
    C --> D[保存新内容]
    D --> E[打印新内容]
    E --> F[继续循环]
    B -->|否| G[检测是否超时]
    G -->|是| H[触发超时回调]
    H --> I[保存数据]
    I --> J[终止进程]
    G -->|否| F
    F --

### 注意事项
1. 存在超时终止机制
2. 两种方法，第一种使用了远程 http 接口，第二种使用了 sqlite3 的 :memory: 连接
   > 注意事项：在使用 sqlite3 的 :memory: 时，我发现，connect.close() 后 :memory: 将不再存在。而不是进程结束才不存在。
3.

### Usage



### Code Grave
```python
    def _timeout_trigger(self, trigger_callback):
        # class Local 使用方式参考，虽然在 Python 里面有点别扭。没有 __init__ 需要 @staticmethod 修饰...
        class Local:
            def __init__(self, source):
                # 【待定】
                # 我认为，Local 不建议闭包，因为 Local 只是暂时的，最终还是要抽出去的。
                # 需要闭包进来的内容可以初始化的时候传递进来！
                self._source = source

            def clear_anchor_time(self):
                self._source._anchor_time = None

        loc = Local(self)

        self._timeout_sending_count += 1
        print(f"超时发送机制触发第 {self._timeout_sending_count} 次")
        trigger_callback()

        if self._up_to_max_trigger_count():
            # 这意味着不再进行操作了
            self._timeout_sending_count = 0

            self._save_data_to_file("memory_filepaths")

            print("超时发送触发次数达到上限，进程终止")
            sys.exit(1)
        else:
            self._anchor_time = None
```
"""
import sqlite3
import sys
import time
from typing import List, Tuple

import pyperclip
import requests

connect = sqlite3.connect(":memory:")
# NOTE: 我认为数据库定义语言 DDL、数据库操作语言 DML、数据库控制语言 DCL 这三种 sql 语言应当完全分离，放在三个地方执行，不要放在一块执行。
connect.execute("""
CREATE TABLE IF NOT EXISTS filepaths(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filepath TEXT NOT NULL
);
""")

TIMEOUT_SENDING_MAX_TIME_INTERVAL = 5


# TODO: 此处有机会练习数据分析的只是

class FilePathCacher:
    def __init__(self, max_len: int = 10):
        self._max_len = max_len

        self._filepaths: List[str] = []

    # ---------------------------------------------------------------------------------------------------------------- #
    def _is_up_to_upper_limit(self):
        return len(self._filepaths) >= self._max_len

    def __save_filepaths_1(self):
        filepaths = self._filepaths
        if not filepaths:
            return
        url = "http://127.0.0.1:8888/api/tool/temp_add_filepath_information"
        response = requests.post(url, json=filepaths)
        if response.status_code == 200:
            print(f"Success, inserted_count: {response.json().get('inserted_count', -1)}")

    def __save_filepaths_2(self):
        cnt = 0
        for filepath in self._filepaths:
            cursor = connect.execute("SELECT id FROM filepaths WHERE filepath=?;", (filepath,))
            if cursor.fetchone() is None:
                cnt += 1
                connect.execute("INSERT INTO filepaths(filepath) VALUES(?);", (filepath,))
        connect.commit()
        print(f"Success, inserted_count: {cnt}")

    def _save_filepaths(self):
        # 函数式编程的一点涉及开闭原则的思想？按道理，变化来到的时候，这种类不应该修改，通过构造函数注入等方式创建新的子类应对变化比较好
        self.__save_filepaths_2()

    def append(self, value, invoke=False):
        if self._is_up_to_upper_limit() or invoke:
            self._save_filepaths()
            self._filepaths.clear()
        self._filepaths.append(value)

    # ---------------------------------------------------------------------------------------------------------------- #


class TimeoutSendingMonitor:
    def __init__(self, timeout_sending_max_time_interval=TIMEOUT_SENDING_MAX_TIME_INTERVAL):
        self._timeout_sending_max_time_interval = timeout_sending_max_time_interval

        self._anchor_time = None

    # ---------------------------------------------------------------------------------------------------------------- #
    def ___save_data_to_file_1(self, dbname):
        # Question: _ __ ___ ____ _____ ______ 这种命名法如何？但是注意事不过三原则，最多三个下划线就应该考虑其他方式了。

        this = self

        # TEST
        print("------------------------------")
        cursor = connect.execute("SELECT * FROM filepaths;")
        for row in cursor.fetchall():
            print(row)
        print("------------------------------")
        # 此处体现了
        pass

    def __save_data_to_file(self, dbname):
        self.___save_data_to_file_1(dbname)

    def _timeout_trigger(self, timeout_triggering_callback, cb_args: Tuple = ()):

        print("检测到长时间未使用，执行后置操作，并将进程终止")

        timeout_triggering_callback(*cb_args)

        self.__save_data_to_file("memory_filepaths")

        sys.exit(1)

    # ---------------------------------------------------------------------------------------------------------------- #
    def _is_timeout(self):
        return time.time() - self._anchor_time > self._timeout_sending_max_time_interval

    def probing(self, timeout_triggering_callback, cb_args: Tuple = ()):
        if self._anchor_time is None:
            self._anchor_time = time.time()
        elif self._is_timeout():
            self._timeout_trigger(timeout_triggering_callback, cb_args=cb_args)

    # ---------------------------------------------------------------------------------------------------------------- #

    def clear_anchor_time(self):
        self._anchor_time = None


"""
### 关于决策过程
将决策过程记录下来是很重要的，不管是会议笔录、视频、博客文章，还是任何的其他形式，
只要能够留下来一些，能够让后人知其然，同时知其所以然的线索。就是一个巨大的进步！
> 音乐家需要听音乐，导演需要看电影，但是程序员需要的不是看代码，而是解题思路！  <br>
> 大家以后看到别人的代码，记得多问 why 即为什么这样写！  <br>

### Know-how 和 Know-why
#### Know-how
- **定义**：Know-how 指的是“技能知识”或“操作知识”，**即能够执行某项具体任务或解决特定问题的能力和技能。**
  这种知识通常是通过实践、经验和培训获得的。
- **特点**：
  - 具体实用：know-how 更侧重于如何去做事情，例如使用某个工具、完成某个项目或执行某个工作流程。
  - 经验性：这种知识往往是隐性或暗示的，难以通过书面形式完全表达，而是需要通过实际操作、观察和模仿来学习。
- **示例**：会计人员的记账技巧、厨师的烹饪方法、工程师的编程技巧等。
#### Know-why
- **定义**：Know-why 指的是“理论知识”或“原理知识”，**即对某个现象、过程或工具背后原因的理解。**
  这种知识关注的是理解事物 如何运作的原因和原理。
- **特点**：
  - 理论性：know-why 更注重理论、原理和因果关系，帮助人们理解为什么某些事情以特定方式进行或某种方法会有效。
  - 易于传递：这种知识通常可以通过书籍、资料和讲解等形式更容易地传播和传授。
- **示例**：物理学中关于重力的原理、化学反应的机制、经济学中的供需关系等。
#### 两者的关系
- **互补性**：在许多情况下，know-how 和 know-why 是相辅相成的。具备 know-how 可以让人们有效地完成任务，而了解 know-why  可以为这些任务提供理论基础和更深入的理解。
- **应用场景**：在实际工作中，专业人员通常需要同时具备这两种知识。例如，一个软件开发工程师不仅需要能够编写代码（know-how），而且还需要理解算法和数据结构背后的理论（know-why）。
#### 总结
简而言之，"know-how" 是关于如何做的技术和技能，而 "know-why" 则是关于为什么这样做的理论和原因。两者在学习、工作和专业发 展中都扮演着重要的角色。

"""


def run():
    # 这两个应该算作是协作类
    filepath_cacher = FilePathCacher()
    timeout_sending_monitor = TimeoutSendingMonitor()

    def timeout_triggering_callback(clipboard_content):
        filepath_cacher.append(clipboard_content, invoke=True)

    pre_clipboard_content = None

    while True:
        time.sleep(0.05)

        cur_clipboard_content = pyperclip.paste()

        if pre_clipboard_content == cur_clipboard_content:
            # 大概做的事情：30s 后，如果剪切板内容没变化，则调用超时触发回调函数，并进程终止
            timeout_sending_monitor.probing(timeout_triggering_callback, (cur_clipboard_content,))
            continue

        timeout_sending_monitor.clear_anchor_time()

        pre_clipboard_content = cur_clipboard_content

        filepath_cacher.append(cur_clipboard_content)

        print(cur_clipboard_content)


if __name__ == '__main__':
    run()
