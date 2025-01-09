"""
## 享元模式
> 享元模式（Flyweight）是一种结构型设计模式，它通过共享对象来尽可能减少内存使用和对象数量。在享元模式中，存在两种对象：
> 内部状态（Intrinsic State）和外部状态（Extrinsic State）。内部状态指对象的共享部分，不随环境改变而改变；外部状态指对象的非共享部分，会随环境改变而改变。

### 实现思路：
享元模式的核心思想是尽量重用已经存在的对象，减少对象的创建和销毁，从而提高性能和节省内存。
它通常适用于需要大量创建对象的场景，但又不能因为对象过多而导致内存不足或性能降低的情况。

### 要点解析
1. 关于“但又不能因为对象过多而导致内存不足或性能降低的情况”这句话，需要好好思考一下。
   类比 Lua DST 的 fn 与 prefab 从多对一改为一对一，也是这个类似的思想。
"""


"""
    下面是一个简单的享元模式的示例，假设我们有一个字符工厂，它可以创建不同的字符对象。
    在实现字符对象时，我们发现有一些字符会被频繁使用，而且它们的状态是不变的，例如空格、逗号、句号等标点符号。
    因此，我们可以将这些字符设计为享元对象，通过共享来节省内存。
"""

class Character:
    def __init__(self, character):
        self.character = character

    def render(self, font):
        print(f"Rendering character {self.character} in font {font}")


class CharacterFactory:
    """
        这不就是缓存机制？这个例子太简单了吧
    """

    def __init__(self):
        self.characters = {}

    def get_character(self, character):
        if character in self.characters:
            return self.characters[character]
        else:
            new_character = Character(character)
            self.characters[character] = new_character
            return new_character


if __name__ == '__main__':
    # 创建字符工厂
    factory = CharacterFactory()

    # 获取不同的字符
    char1 = factory.get_character("A")
    char2 = factory.get_character("B")
    char3 = factory.get_character(" ")
    char4 = factory.get_character(",")
    char5 = factory.get_character(" ")
    char6 = factory.get_character(".")

    # 渲染不同的字符
    char1.render("Arial")
    char2.render("Times New Roman")
    char3.render("Arial")
    char4.render("Times New Roman")
    char5.render("Arial")
    char6.render("Times New Roman")
