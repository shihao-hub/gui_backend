import traceback

import speech_recognition as sr

# 创建语音识别的识别器实例
recognizer = sr.Recognizer()
# 打开 WAV 文件
with sr.AudioFile("./resources/media/recording.wav") as source:
    audio_data = recognizer.record(source)  # 读取音频文件
# 使用Google Web服务进行识别
try:
    text = recognizer.recognize_google(audio_data, language='zh-CN')  # 中文识别
    print("识别的文本：", text)
except sr.UnknownValueError as e:
    print(f"{e}\n{traceback.format_exc()}")
    print("未能理解音频")
except sr.RequestError as e:
    print(f"无法请求结果，原因：\n{traceback.format_exc()}")
