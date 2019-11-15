import configparser
from termcolor import colored
import os
import sys


class JoyconConfig:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('gamepad.ini')

        self.section = self.config["Girlfriend"]["config"]
        self.current_config = self.config[self.section]

        self.allowed_apps = self.config["Girlfriend"]["keyboard_apps"].split(
            ",")
        self.gamepad_pointer = int(self.config["Girlfriend"]["gamepad_pointer"])
        self.port = self.config["Girlfriend"]["port"]

    def get_config(self, section: str, key: str):
        return self.config[section][key]

    def update_gamepad_pointer(self, gamepad_pointer):
        self.config["Girlfriend"]["gamepad_pointer"] = str(gamepad_pointer)
        with open('gamepad.ini', 'w') as configfile:
            self.config.write(configfile)
        self.gamepad_pointer = int(self.config["Girlfriend"]["gamepad_pointer"])

    def get_config_button(self, gamepad_button):
        if gamepad_button in self.current_config:
            return self.current_config[gamepad_button]
        else:
            return self.config["DEFAULT"][gamepad_button]

    def refresh_gamepad_pointer(self, current_gamepads, update_pointer=False):
        if update_pointer:
            print(colored(
                f"Update Gamepads From: {len(current_gamepads)}"))
            self.update_gamepad_pointer(self.gamepad_pointer + 1)
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            print(colored(
                f"Update Gamepads From: {len(current_gamepads)}"))
            self.update_gamepad_pointer(0)
            os.execl(sys.executable, sys.executable, *sys.argv)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


joycon_config = JoyconConfig()
