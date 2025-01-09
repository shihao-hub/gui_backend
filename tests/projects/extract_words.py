import pprint
import re


def extract_words_from_file(file_path):
    # 使用集合来存储单词以避免重复
    words = set()

    # 打开文件并读取内容
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 使用正则表达式提取单词
            # \w+ 表示匹配一个或多个字母、数字或下划线
            # line_words = re.findall(r'\w+', line)
            line_words = re.findall(r"\b[a-zA-Z_]+\b", line)
            # 将提取到的单词添加到集合中
            words.update(line_words)

    return words


TEMPLATE = """\
<application>
    <component name="DSTDictionaryState">
        <words>
{words}
        </words>
    </component>
</application>
"""


def main():
    words = extract_words_from_file(
        r"D:\JetBrainsProjects\IdeaProjects\Lua\MoreItems\modmain\PostInit\prefabs\mone_lifeinjector_vb.lua")
    pprint.pprint(words)

    # 排除是英文单词的存在 key value？

    # 写入文件
    with open("./dst-dictionary.xml", "w", encoding="utf-8") as file:
        file.write(TEMPLATE.format(words="\n".join([f"            <w>{e}</w>" for e in words])))


if __name__ == '__main__':
    main()
