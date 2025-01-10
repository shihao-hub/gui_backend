from PIL import ImageGrab, Image


def save_clipboard_image(file_path):
    # 从剪切板获取图片
    image = ImageGrab.grabclipboard()

    if isinstance(image, Image.Image):
        # 保存图片到指定路径
        image.save(file_path)
        print(f"Image saved to {file_path}")
    else:
        print("No image found in clipboard.")


if __name__ == "__main__":
    save_clipboard_image("resources/image/output_image.png")  # 可以指定你想要的文件名
