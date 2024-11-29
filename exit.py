import keyboard

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

exit_buttons = config.get('Appearance', 'exitShortcut').split(', ')


class Exit:
    @staticmethod
    def exit():
        return all(keyboard.is_pressed(key) for key in exit_buttons)
