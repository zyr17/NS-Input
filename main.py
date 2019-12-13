import time
import codec
import joycon
import pc_input
from constants import *
import math
import os
import sys
from pynput import keyboard, mouse
from config import joycon_config, resource_path
import win32gui
from termcolor import colored

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg


def on_release(key):
    try:
        key = str.lower(key.char)
    except AttributeError:
        pass
    if obs_focused:
        keyboard_manager.release(key)


def on_press(key):
    global running
    try:
        key = str.lower(key.char)
        if GIRL_MODE == NORMAL:
            keyboard_manager.enable_keyboard = True
            if key == "5":
                if not enable_gamepad:
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    joycon_config.refresh_gamepad_pointer(gamepads)
            elif key == "4":
                if not enable_gamepad:
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    joycon_config.refresh_gamepad_pointer(gamepads, True)
            elif key == "7":
                keyboard_manager.toggle_mouse()
                if not keyboard_manager.enable_mouse:
                    win32gui.MoveWindow(hwnd, CENTER_X - WIDTH,
                                        CENTER_Y - HEIGHT, WIDTH,
                                        HEIGHT, True)
                else:
                    win32gui.MoveWindow(hwnd, int(MOUSE_CENTER_X - WIDTH / 2),
                                        int(MOUSE_CENTER_Y - HEIGHT / 2), WIDTH,
                                        HEIGHT, True)
        if key == "6":
            running = False
    except AttributeError:
        keyboard_manager.enable_keyboard = True
    if obs_focused:
        keyboard_manager.press(key)


def quit_me():
    codec.close()
    joycon.close()
    keyboard_listener.stop()
    pg.quit()
    sys.exit()


def perform_a_press(button):
    for _ in range(5):
        joycon.press(button)
    joycon.release(button)


def run_pointer_line(line):
    button_event = line[0]
    button = line[1]
    if button_event == "DELAY":
        pass
    elif button_event == "PRESS":
        joycon.press(button, line[2], line[3])
    else:
        joycon.release(button)


def run_auto_py():
    if GIRL_MODE == REPLAY:
        global pointer_line, time_elapsed, base_time, script_repeat
        keyboard_manager.enable_keyboard = False
        line = lines[pointer_line]
        if len(line) < 4:
            expected_time = line[2]
        else:
            expected_time = line[4]
        if time_elapsed >= expected_time:
            pointer_line += 1
            if pointer_line > len(lines) - 1:
                pointer_line = 0
                script_repeat += 1
                print('script has run %d times' % script_repeat)
            if script_repeat < joycon_config.script_repeat:
                run_pointer_line(lines[pointer_line])
            time_elapsed = 0


def refresh_focused_window():
    global obs_focused
    focused_window_name = str.lower(
        win32gui.GetWindowText(win32gui.GetForegroundWindow()))
    am_i_allowed = False
    for a in joycon_config.allowed_apps:
        if str.lower(a) in focused_window_name:
            am_i_allowed = True
    if am_i_allowed:
        if not obs_focused:
            print(colored("OBS Focused", "green"))
            obs_focused = True
    elif obs_focused:
        print(colored("OBS DeFocused", "red"))
        obs_focused = False


vec = pg.math.Vector2
os.system('color')

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
pg.joystick.init()
pg.display.set_caption('[Ponyo] Mapping-Switch')
gamepads = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]

icon = pg.image.load(resource_path('app.ico'))
pg.display.set_icon(icon)

hwnd = win32gui.FindWindow(None, "[Ponyo] Mapping-Switch")
win32gui.MoveWindow(hwnd, CENTER_X - WIDTH, CENTER_Y - HEIGHT, WIDTH,
                    HEIGHT, True)

enable_gamepad = True
if len(gamepads) == 0:
    enable_gamepad = False
    print(colored("No Gamepad Connected, Only Run Keyboard / Mouse", "red"))

deadzone_stick = 0.1
deadzone_trigger = 0.01
stick_l = vec(0, 0)
stick_r = vec(0, 0)
dpad = vec(0, 0)

if enable_gamepad:
    if joycon_config.gamepad_pointer >= len(gamepads):
        joycon_config.update_gamepad_pointer(0)
    print(
        f"Connected Gamepads: {len(gamepads)}  |  GamePad Pointer: {joycon_config.gamepad_pointer}")

    gamepads[joycon_config.gamepad_pointer].init()
    name = gamepads[joycon_config.gamepad_pointer].get_name()
    buttons = gamepads[joycon_config.gamepad_pointer].get_numbuttons()
    axes = gamepads[joycon_config.gamepad_pointer].get_numaxes()
    dpads = gamepads[joycon_config.gamepad_pointer].get_numhats()

running = True
MOUSE = mouse.Controller()
COUNTING = 0

joycon = joycon.JoyconManager(GIRL_MODE)
keyboard_manager = pc_input.KeyboardMouseManager(joycon)

keyboard_listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
keyboard_listener.start()

def expandscript(filename):
    if filename[0] == '/' and filename[-1] == '/':
        lines = filename[1:-1].split('\n')
    else:
        if not os.path.exists(filename):
            print('%s not found!' % filename)
            exit(0)
        folder = filename
        while len(folder) > 0 and folder[-1] != '/' and folder[-1] != '\\':
            folder = folder[:-1]
        #print(folder, filename)
        lines = open(filename).readlines()
    res = []
    for line in lines:
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            pass
        elif line[:7] == 'SCRIPT ':
            repeats = 0
            line = line[7:]
            while line[0] != ' ':
                repeats = repeats * 10 + int(line[0])
                line = line[1:]
            for _ in range(repeats):
                res += expandscript(folder + line[1:])
        elif line[:5] == 'PRESS':
            number = ''
            while line[-1] != ' ':
                number = line[-1] + number
                line = line[:-1]
            number = float(number)
            action_per_second = 25
            for i in range(int(number * action_per_second) - 1):
                res.append(line + '%f' % (1 / action_per_second))
            res.append(line + str(number - int(number * action_per_second - 1) / action_per_second))
        else:
            res.append(line)
    return res

def scriptsplit(lines):
    split = []
    for line in lines:
        line = line.strip().split(' ')
        for i in range(2, len(line)):
            line[i] = float(line[i])
        split.append(line)
    return split

lines = []
for script in joycon_config.script.split(':'):
    try:
        repeat = int(script)
        lines[-1] = lines[-1] * repeat
    except:
        lines.append(expandscript(script))
scripts = []
for script in lines:
    scripts += script
lines = scriptsplit(scripts)
if joycon_config.start_delay != -1:
    lines = [['DELAY', 'DELAY', joycon_config.start_delay]] + lines
if joycon_config.repeat_delay != -1:
    lines += [['DELAY', 'DELAY', joycon_config.repeat_delay]]
'''
lines = []
try:
    f = open("record.txt", "r")
except:
    f = open("record.txt", "w+")
for fi in f:
    lines.append(fi)
f.close()
'''
pointer_line = 0
obs_focused = True
time_elapsed = 0
script_repeat = 0
run_pointer_line(lines[pointer_line])
base_time = time.time()
if enable_gamepad:
    gamepad = gamepads[joycon_config.gamepad_pointer]

if GIRL_MODE != NORMAL:
    keyboard_manager.enable_keyboard = True
    enable_gamepad = False

while running:
    clock.tick(TICK)
    current_time = time.time()
    delta_time = current_time - base_time
    time_elapsed += delta_time
    base_time = current_time
    run_auto_py()
    if script_repeat == joycon_config.script_repeat:
        running = False

    if GIRL_MODE == NORMAL:

        if COUNTING == 25:
            refresh_focused_window()

        if COUNTING == TICK * 3:
            COUNTING = 0
        COUNTING += 1
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if keyboard_manager.enable_mouse:
                if event.type == pg.MOUSEBUTTONDOWN:
                    keyboard_manager.press(event.button)
                if event.type == pg.MOUSEBUTTONUP:
                    keyboard_manager.release(event.button)

    if GIRL_MODE != REPLAY:
        if keyboard_manager.enable_keyboard:
            keyboard_manager.timer()
            if enable_gamepad:
                if gamepad.get_button(0) or gamepad.get_button(
                        1) or gamepad.get_button(2) or gamepad.get_button(3):
                    keyboard_manager.enable_keyboard = False
            if keyboard_manager.enable_mouse:
                x = MOUSE.position[0]
                y = MOUSE.position[1]
                rel = pc_input.mouse_relative(
                    (x - MOUSE_CENTER_X, y - MOUSE_CENTER_Y))
                if isinstance(rel, tuple):
                    joycon.press("R_STICK", rel[0] / SENSITIVITY_X,
                                 rel[1] / SENSITIVITY_Y)
                    MOUSE.position = (MOUSE_CENTER_X, MOUSE_CENTER_Y)
                else:
                    joycon.release("R_STICK")

    if GIRL_MODE == NORMAL and not keyboard_manager.enable_keyboard and enable_gamepad:
        # get gamepad inputs
        for i in range(buttons):
            if i == 0:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("A"))
                else:
                    joycon.release(joycon_config.get_config_button("A"))
            elif i == 1:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("B"))
                else:
                    joycon.release(joycon_config.get_config_button("B"))
            elif i == 2:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("X"))
                else:
                    joycon.release(joycon_config.get_config_button("X"))
            elif i == 3:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("Y"))
                else:
                    joycon.release(joycon_config.get_config_button("Y"))
            elif i == 4:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("L"))
                else:
                    joycon.release(joycon_config.get_config_button("L"))
            elif i == 5:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("R"))
                else:
                    joycon.release(joycon_config.get_config_button("R"))
            elif i == 6:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("MINUS"))
                else:
                    joycon.release(joycon_config.get_config_button("MINUS"))
            elif i == 7:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("PLUS"))
                else:
                    joycon.release(joycon_config.get_config_button("PLUS"))
            elif i == 8:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("LCLICK"))
                    stick_l_pressed = True
                else:
                    joycon.release(joycon_config.get_config_button("LCLICK"))
                    stick_l_pressed = False
            elif i == 9:
                if gamepad.get_button(i):
                    joycon.press(joycon_config.get_config_button("RCLICK"))
                    stick_r_pressed = True
                else:
                    joycon.release(joycon_config.get_config_button("RCLICK"))
                    stick_r_pressed = False

        # get axes values
        for i in range(axes):
            axis = gamepad.get_axis(i)
            if i == 0:
                stick_l.x = axis
            elif i == 1:
                stick_l.y = axis
            elif i == 2:
                if axis > deadzone_trigger:
                    joycon.press(joycon_config.get_config_button("ZL"))
                    joycon.release(joycon_config.get_config_button("ZR"))
                elif abs(axis) > deadzone_trigger:
                    joycon.press(joycon_config.get_config_button("ZR"))
                    joycon.release(joycon_config.get_config_button("ZL"))
                else:
                    joycon.release(joycon_config.get_config_button("ZL"))
                    joycon.release(joycon_config.get_config_button("ZR"))
            elif i == 3:
                stick_r.y = axis
            elif i == 4:
                stick_r.x = axis

        # get dpad values
        for i in range(dpads):
            dpad.x, dpad.y = gamepad.get_hat(i)
            if dpad.y == 0 and dpad.x == 0:
                joycon.release(joycon_config.get_config_button("DPAD_U"))
                joycon.release(joycon_config.get_config_button("DPAD_D"))
                joycon.release(joycon_config.get_config_button("DPAD_L"))
                joycon.release(joycon_config.get_config_button("DPAD_R"))
                joycon.release(joycon_config.get_config_button("DPAD_U_R"))
                joycon.release(joycon_config.get_config_button("DPAD_U_L"))
                joycon.release(joycon_config.get_config_button("DPAD_D_R"))
                joycon.release(joycon_config.get_config_button("DPAD_D_L"))

            if dpad.y == 1 and dpad.x == 0:
                joycon.press(joycon_config.get_config_button("DPAD_U"))
            if dpad.y == -1 and dpad.x == 0:
                joycon.press(joycon_config.get_config_button("DPAD_D"))
            if dpad.y == 1 and dpad.x == 1:
                joycon.press(joycon_config.get_config_button("DPAD_U_R"))
            if dpad.y == -1 and dpad.x == 1:
                joycon.press(joycon_config.get_config_button("DPAD_D_R"))

            if dpad.x == 1 and dpad.y == 0:
                joycon.press(joycon_config.get_config_button("DPAD_R"))
            if dpad.x == -1 and dpad.y == 0:
                joycon.press(joycon_config.get_config_button("DPAD_L"))
            if dpad.y == 1 and dpad.x == -1:
                joycon.press(joycon_config.get_config_button("DPAD_U_L"))
            if dpad.y == -1 and dpad.x == -1:
                joycon.press(joycon_config.get_config_button("DPAD_D_L"))

        # left stick
        if stick_l.length_squared() != 0:

            if stick_l.length() < deadzone_stick:
                stick_l.scale_to_length(0)
                joycon.release(joycon_config.get_config_button("L_STICK"))
            else:
                joycon.press(joycon_config.get_config_button("L_STICK"),
                             stick_l.x,
                             stick_l.y)
                stick_l /= math.sqrt(abs(stick_l.x) + abs(stick_l.y))

        # right stick
        if stick_r.length_squared() != 0:
            if stick_r.length() < deadzone_stick:
                stick_r.scale_to_length(0)
                joycon.release(joycon_config.get_config_button("R_STICK"))
            else:
                joycon.press(joycon_config.get_config_button("R_STICK"),
                             stick_r.x,
                             stick_r.y)
                stick_r /= math.sqrt(abs(stick_r.x) + abs(stick_r.y))
quit_me()
