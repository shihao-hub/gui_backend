import pyaudio
import wave

# 设置录音参数
FORMAT = pyaudio.paInt16  # 16位采样
CHANNELS = 2  # 声道数（立体声）
RATE = 44100  # 采样率
CHUNK = 1024  # 每个缓冲区的采样点数
RECORD_SECONDS = 5  # 录音时长（秒）
WAVE_OUTPUT_FILENAME = "recording.wav"  # 输出文件名


def main():
    # 初始化 PyAudio
    audio = pyaudio.PyAudio()
    # 打开输入流
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("开始录音...")
    frames = []
    # 进行录音
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("录音结束.")

    # 停止和关闭流
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 保存录音为 WAV 文件
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"录音已保存为 {WAVE_OUTPUT_FILENAME}")


if __name__ == '__main__':
    main()
