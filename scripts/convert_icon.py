from PIL import Image
import os

def convert_icon():
    if os.path.exists("icon.jpg"):
        img = Image.open("icon.jpg")
        img.save("icon.ico", format='ICO', sizes=[(256, 256)])
        print("Converted icon.jpg to icon.ico")
    else:
        print("icon.jpg not found")

if __name__ == "__main__":
    convert_icon()
