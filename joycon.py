import codec
import time
from codec_constants import *
from constants import STICK_FULL_TRIGGER
import math
from typing import Dict, Union
from termcolor import colored


class JoyconButton:
    """A joycon button/stick"""
    identifier: str
    is_pressed: bool
    is_stick = False

    def __init__(self, identifier: str, binary_code: int):
        self.identifier = identifier
        self.binary_code = binary_code
        self.is_pressed = False

    def __str__(self) -> str:
        return self.identifier

    def press(self) -> bool:
        print(colored(f"[{self.identifier}] pressed", "green"))
        if not self.is_pressed:
            self.is_pressed = True
            return True
        return False

    def release(self) -> bool:
        if self.is_pressed:
            self.is_pressed = False
            print(
                colored(f"[{self.identifier}] released", "red"))
            return True
        return False

    def update(self, x: float, y: float):
        return


class JoyconStick(JoyconButton):
    def __init__(self, identifier: str, binary_code: int):
        super().__init__(identifier, binary_code)
        self.binary_code = 0
        if "R" in identifier:
            self.par = 44
        else:
            self.par = 24
        self.is_stick = True

    def stick_angle(self, angle_, intensity):
        return (intensity + (angle_ << 8)) << self.par

    def release(self) -> bool:
        if self.is_pressed:
            if self.par == 44:
                self.binary_code = RSTICK_CENTER
            else:
                self.binary_code = LSTICK_CENTER
            self.press()
            self.is_pressed = False
            print(
                colored(f"[{self.identifier}] released", "red"))
            return True
        return False

    def update(self, x: float, y: float):
        angle_ = 360 - (round(math.atan2(y, x) * (
                180 / math.pi)) + 360) % 360
        length = math.sqrt(pow(x, 2) + pow(y, 2))
        if length > STICK_FULL_TRIGGER:
            force = 0xFF  # full
        else:
            force = 0x80  # partial
        self.binary_code = self.stick_angle(angle_, force)


class JoyconManager:
    girls: Dict[str, Union[JoyconStick, JoyconButton]]

    def __init__(self, mode):
        self.girls = {}
        self.add_list()
        self.girls["R_STICK"] = JoyconStick("R_STICK", 0)
        self.girls["L_STICK"] = JoyconStick("L_STICK", 0)
        self.do_record = int(mode) == 1
        print(self.do_record)
        self.timestamp = time.time()
        self.f_list = []

    def _record_press(self, button: str, x: float, y: float):
        if self.do_record:
            self.f_list.append(
                f"PRESS {button} {x} {y} {round(time.time() - self.timestamp, 5)}\n")
            self.timestamp = time.time()

    def _record_release(self, button: str):
        if self.do_record:
            self.f_list.append(
                f"RELEASE {button} {round(time.time() - self.timestamp, 5)}\n")
            self.timestamp = time.time()

    def press(self, button: str, x: float = 0.0, y: float = 0.0):
        self.girls[button].update(x, y)
        self.send_command_combination()
        self._record_press(button, x, y)
        self.girls[button].press()

    def fake_press(self, button: str, x: float = 0.0, y: float = 0.0):
        self.girls[button].update(x, y)
        self._record_press(button, x, y)
        self.girls[button].press()

    def release(self, button):
        if self.girls[button].release():
            self._record_release(button)
            self.send_command_combination()

    def send_command_combination(self):
        command = 0
        for key, button in self.girls.items():
            if button.is_pressed:
                command += button.binary_code
        codec.send_cmd(command)

    def add_list(self):
        for key, value in JOYCON_DICT.items():
            self.girls[key] = JoyconButton(key, value)

    def close(self):
        if self.do_record:
            f = open("record.txt", "w+")
            for line in self.f_list:
                f.write(line)
            f.close()
