from termcolor import colored
from pynput.keyboard import Key

KEYBOARD_DICT = {"w": ["L_STICK", 0, -1],
                 "a": ["L_STICK", -1, 0],
                 "s": ["L_STICK", 0, 1],
                 "d": ["L_STICK", 1, 0],
                 "i": ["R_STICK", 0, -1],
                 "j": ["R_STICK", -1, 0],
                 "k": ["R_STICK", 0, 1],
                 "l": ["R_STICK", 1, 0],
                 "v": ["A", 0],
                 "b": ["B", 0],
                 "n": ["X", 0],
                 "x": ["X", 0],
                 "m": ["Y", 0],
                 "y": ["Y", 0],
                 "1": ["HOME", 0],
                 "0": ["CAPTURE", 0],

                 "`": ["B"],
                 Key.backspace: ["B"],
                 "'": ["B"],
                 "\\": ["B"],

                 Key.space: ["B"],

                 Key.ctrl_l: ["ZR"],
                 Key.ctrl_r: ["ZR"],

                 "/": ["RCLICK"],
                 ".": ["LCLICK"],

                 "q": ["L"],
                 "o": ["R"],

                 Key.shift_l: ["ZL"],
                 Key.shift_r: ["ZL"],
                 "=": ["PLUS"],
                 "-": ["MINUS"],
                 Key.enter: ["A"],
                 Key.up: ["DPAD_U"],
                 Key.down: ["DPAD_D"],
                 Key.right: ["DPAD_R"],
                 Key.left: ["DPAD_L"],
                 Key.tab: ["HOME"],

                 1: ["ZR"],
                 2: ["A"],
                 3: ["R"]
                 }


class AKey:
    """A key"""
    identifier: str
    is_pressed: bool
    is_directional = False
    is_l = False
    is_r = False
    x: int
    y: int

    def __init__(self, identifier, joycon_button: str, x: int = 0, y: int = 0):
        self.identifier = identifier
        self.joycon_button = joycon_button
        self.is_pressed = False
        self.x = x
        self.y = y
        if "L_STICK" == joycon_button:
            self.is_l = True
            self.is_directional = True
        elif "R_STICK" == joycon_button:
            self.is_r = True
            self.is_directional = True

    def update(self, joycon_button: str, x: int = 0, y: int = 0):
        self.joycon_button = joycon_button
        self.is_pressed = False
        self.x = x
        self.y = y
        self.is_directional = True
        if x == y == 0:
            self.is_directional = False

    def press(self) -> bool:
        if not self.is_pressed:
            print(colored(f"[{self.identifier}] pressed", "white"))
            self.is_pressed = True
            return True
        return False

    def release(self) -> bool:
        if self.is_pressed:
            self.is_pressed = False
            print(
                colored(f"[{self.identifier}] released", "blue"))
            return True
        return False


class KeyboardMouseManager:
    """Keyboard and Mouse Manager"""

    def __init__(self, joycon):
        self.keys = {}
        self.joycon = joycon
        self.add_list()
        self.enable_keyboard = True
        self.enable_mouse = False

    def toggle_mouse(self):
        self.enable_mouse = not self.enable_mouse
        self.refresh()

    def press(self, key):
        if not self.enable_keyboard:
            return
        if key in self.keys:
            self.keys[key].press()
            self.timer()

    def release(self, key):
        if not self.enable_keyboard:
            return
        if key in self.keys:
            if self.keys[key].release():
                self.joycon.release(self.keys[key].joycon_button)
                self.timer()

    def add_list(self):
        for key, value in KEYBOARD_DICT.items():
            if len(value) > 2:
                self.keys[key] = AKey(key, value[0], value[1], value[2])
            else:
                self.keys[key] = AKey(key, value[0])

    def refresh(self):
        if self.enable_mouse:
            self.keys["i"].update("X")
            self.keys["j"].update("Y")
            self.keys["k"].update("B")
            self.keys["l"].update("A")
        else:
            self.keys["i"].update("R_STICK", 0, -1)
            self.keys["j"].update("R_STICK", -1, 0)
            self.keys["k"].update("R_STICK", 0, 1)
            self.keys["l"].update("R_STICK", 1, 0)

    def timer(self):
        if not self.enable_keyboard:
            return
        l_x = l_y = r_x = r_y = 0
        for index, key in self.keys.items():
            if not key.is_pressed:
                continue
            if not key.is_directional:
                self.joycon.fake_press(key.joycon_button)
            elif key.is_l:
                l_x += key.x
                l_y += key.y
            elif key.is_r:
                r_x += key.x
                r_y += key.y
        if not l_x == l_y == 0:
            self.joycon.fake_press("L_STICK", l_x, l_y)
        if not r_x == r_y == 0:
            self.joycon.fake_press("R_STICK", r_x, r_y)
        self.joycon.send_command_combination()


def mouse_relative(rel):
    max_number = max(abs(rel[0]), abs(rel[1]))

    if max_number == 0:
        return False

    if max_number == abs(rel[0]):
        return_tuple = (rel[0] / max_number, rel[1] / max_number)
    else:
        return_tuple = (rel[0] / max_number, rel[1] / max_number)
    print(colored(f"X: {return_tuple[0]} Y: {return_tuple[1]}", "blue"))
    return return_tuple
