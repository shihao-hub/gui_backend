"""
## 外观模式
> 外观模式（Facade）是一种结构型设计模式，它提供了一个简单的接口，隐藏了一个或多个复杂的子系统的复杂性。
> 外观模式可以使得客户端只需要与外观对象进行交互，而不需要与子系统中的每个对象直接交互，从而降低了客户端的复杂性，提高了系统的可维护性。

### 实现思路
外观模式的核心思想是，提供一个简单的接口，包装一个或多个复杂的子系统，隐藏其复杂性，并向客户端提供一个更简单、更易于使用的接口。
在外观模式中，外观对象扮演着客户端和子系统之间的协调者，它负责将客户端的请求转发给子系统中的相应对象，并将其结果返回给客户端。

### 外观模式的优点
- 简化了客户端的使用：外观模式为客户端提供了一个简单的接口，使得客户端不需要了解子系统中的每个对象及其功能，从而降低了客户端的复杂性。
- 隐藏了子系统的复杂性：外观模式将子系统的复杂性隐藏在外观对象之后，使得客户端只需要与外观对象进行交互，从而提高了系统的可维护性。
- 提高了灵活性：由于客户端只与外观对象进行交互，因此可以在不影响客户端的情况下修改或替换子系统中的对象。

### 外观模式的缺点
- 不能完全隐藏子系统的复杂性：外观模式只是将子系统的复杂性隐藏在外观对象之后，但仍然需要客户端了解外观对象的接口和使用方式。
- 可能会引入不必要的复杂性：如果外观对象需要处理复杂的逻辑，就会引入额外的复杂性，从而降低系统的可维护性。

"""
from collections import namedtuple

# 一言以蔽之：将复杂的逻辑/类抽成一个 Facade 类，客户端只使用这个类。举例：之前的 Detail 和 Improve 表内部封装的函数就可以抽到一个 Facade 类中

"""
    以下是一个使用外观模式的示例，假设我们有一个音乐播放器，它可以播放MP3和FLAC两种格式的音乐。
    不同格式的音乐播放需要不同的解码器，同时还需要加载音乐文件和设置音量等操作。
    我们可以使用外观模式封装这些复杂的操作，提供一个简单易用的接口给客户端使用：
"""


class AbstractPlayer:
    def load(self, file_path):
        raise NotImplemented

    def set_volume(self, volume):
        raise NotImplemented

    def play(self):
        raise NotImplemented

    def run(self, file_path, volume):
        # 运用了模板函数法
        self.load(file_path)
        self.set_volume(volume)
        self.play()


class MP3Player(AbstractPlayer):
    def load(self, file_path):
        print(f"Loading MP3 file from {file_path}")

    def set_volume(self, volume):
        print(f"Setting MP3 volume to {volume}")

    def play(self):
        print("Playing MP3 music")


class FLACPlayer(AbstractPlayer):
    def load(self, file_path):
        print(f"Loading FLAC file from {file_path}")

    def set_volume(self, volume):
        print(f"Setting FLAC volume to {volume}")

    def play(self):
        print("Playing FLAC music")


class MusicPlayerFacade:
    """
        MusicPlayer 类是外观类，它封装了 MP3 和 FLAC 播放器对象。
        play_mp3 和 play_flac 方法是外观类中的简单接口，它们将客户端的请求转发给相应的播放器对象。

        客户端只需要使用 MusicPlayer 类就可以进行 MP3 和 FLAC 的播放，而**不需要了解播放器的具体实现**。
        如果需要修改或替换播放器中的对象，**只需要修改外观类的实现即可，而不会影响客户端的使用**。

        当然，类的命名我认为不建议用 Facade，像 Decorator 这种特征明显的设计模式这样命名还可以接受
    """

    def __init__(self):
        self.mp3_player = MP3Player()
        self.flac_player = FLACPlayer()

    def play_mp3(self, file_path, volume):
        self.mp3_player.run(file_path, volume)

    def play_flac(self, file_path, volume):
        self.flac_player.run(file_path, volume)


def main():
    facade = MusicPlayerFacade()
    facade.play_mp3("song.mp3", 10)
    facade.play_flac("song.flac", 20)

    namedtuple


if __name__ == '__main__':
    main()
