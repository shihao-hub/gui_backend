import keyboard


def collect_input():
    print("Type your input (Press Enter to finish):")

    lines = []
    current_line = ""

    while True:
        event = keyboard.read_event()  # 等待用户按下键

        if event.event_type == keyboard.KEY_DOWN:  # 只处理按下事件
            if event.name == 'enter':
                # 当用户按下 Enter 键时，结束并存储当前行
                if current_line:  # 如果当前行不为空则添加到列表中
                    lines.append(current_line)
                break  # 跳出循环
            elif event.name == 'backspace':
                # 处理退格键
                current_line = current_line[:-1]
                print("\r" + " " * (len(current_line) + 1) + "\r", end='')  # 清除行
                print(current_line, end='')  # 重新打印当前行
            else:
                current_line += event.name + " "  # 将按下的键添加到当前行
                print("\r" + " " * (len(current_line) + 1) + "\r", end='')  # 清除行
                print(current_line, end='')  # 重新打印当前行

    return '\n'.join(lines)


if __name__ == "__main__":
    user_input = collect_input()
    print("\nYou entered:\n", user_input)
