import pyautogui
import os
import keyboard


def take_shot():

    username = os.getlogin()
    file_path = f"C:/Users/{username}/AppData/count.txt"
    saved_pic = "c:/Users/sxxve/Pictures"

    count = 0

    if not os.path.exists(file_path):
        with open(file_path, "w") as fp:
            fp.write(str(count))


    with open(file_path, "r") as file:
        num = file.read()
        num = int(num) + 1

    count = num

    with open(file_path, "w") as f:
        f.write(str(count))
        count = int(count) + 1

    count = num


    pyautogui.screenshot(f"{saved_pic}/screenshot_{count}.PNG")


def take_screenshot():
    if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift') and keyboard.is_pressed('S'):
        # subprocess.run(["python", "screenshot.py"])
        take_shot()