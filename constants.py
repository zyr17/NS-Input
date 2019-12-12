from config import joycon_config

TICK = int(joycon_config.get_config("Girlfriend", "tick"))

SENSITIVITY_X = int(joycon_config.get_config("Mouse", "x_sensitivity"))
SENSITIVITY_Y = int(joycon_config.get_config("Mouse", "y_sensitivity"))

MOUSE_CENTER_Y = int(joycon_config.get_config("Position", "mouse_center_y"))
MOUSE_CENTER_X = int(joycon_config.get_config("Position", "mouse_center_x"))

CENTER_X = int(joycon_config.get_config("Position", "window_x"))
CENTER_Y = int(joycon_config.get_config("Position", "window_y"))

NORMAL = 0
RECORD = 1
REPLAY = 2
GIRL_MODE = int(joycon_config.mode)
MOUSE_DEADZONE = 2
if GIRL_MODE == RECORD:
    TICK = 100
if GIRL_MODE == REPLAY:
    TICK = 200

STICK_FULL_TRIGGER = float(joycon_config.get_config("Gamepad", "stick_full_threshold"))
WIDTH = int(joycon_config.get_config("Position", "window_width"))
HEIGHT = int(joycon_config.get_config("Position", "window_height"))
