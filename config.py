import configparser
from termcolor import colored
import os
import sys
import argparse

parser = argparse.ArgumentParser('Send commands through UNO R3 to control switch. Arguments in command line will overwrite settings in gamepad.ini, such as mode, port, etc.')
parser.add_argument('-script', type=str, default='record.txt',
    help='which script to run, default is record.txt. see project README for advanced use.')
parser.add_argument('-mode', type=int, default=-1,
    help='choose mode. 0=streaming, 1=record, 2=replay, record will save in record.txt.')
parser.add_argument('-port', type=str, default='',
    help='UART port name')
parser.add_argument('-repeat', type=int, default=1,
    help='how many times to run the script, default is 1.')
parser.add_argument('-delay', type=float, default=0,
    help='seconds to delay before running the script.')
parser.add_argument('-repeat_delay', type=float, default=1,
    help='seconds to delay after running the script. if set -1, you should input "8" to start next round.')

args = parser.parse_args()

print(args)

class JoyconConfig:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('gamepad.ini')

        self.section = self.config["Girlfriend"]["config"]
        self.current_config = self.config[self.section]

        self.allowed_apps = self.config["Girlfriend"]["keyboard_apps"].split(
            ",")
        self.gamepad_pointer = int(self.config["Girlfriend"]["gamepad_pointer"])
        self.port = self.config["Girlfriend"]["port"] if args.port == '' else args.port
        self.script = args.script
        self.mode = self.config["Girlfriend"]["mode"] if args.mode == -1 else args.mode
        self.script_repeat = args.repeat
        self.start_delay = args.delay
        self.repeat_delay = args.repeat_delay

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