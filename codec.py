import math
import sys
import time
import serial
from codec_constants import *
from config import joycon_config


# Compute x and y based on angle and intensity
def angle(angle_, intensity):
    # y is negative because on the Y input, UP = 0 and DOWN = 255
    x = int((math.cos(math.radians(angle_)) * 0x7F) * intensity / 0xFF) + 0x80
    y = -int((math.sin(math.radians(angle_)) * 0x7F) * intensity / 0xFF) + 0x80
    return x, y


# Precision wait
def p_wait(waitTime):
    t0 = time.perf_counter()
    t1 = t0
    while (t1 - t0 < waitTime):
        t1 = time.perf_counter()


# Wait for data to be available on the serial port
def wait_for_data(timeout=1.0, sleepTime=0.1):
    t0 = time.perf_counter()
    t1 = t0
    inWaiting = ser.in_waiting
    while (t1 - t0 < sleepTime) or (inWaiting == 0):
        time.sleep(sleepTime)
        inWaiting = ser.in_waiting
        t1 = time.perf_counter()
        if t1 - t0 > 3:
            print("Sync Failed")
            sys.exit()


# Read X bytes from the serial port (returns list)
def read_bytes(size):
    bytes_in = ser.read(size)
    return list(bytes_in)


# Read 1 byte from the serial port (returns int)
def read_byte():
    bytes_in = read_bytes(1)
    if len(bytes_in) != 0:
        byte_in = bytes_in[0]
    else:
        byte_in = 0
    return byte_in


# Discard all incoming bytes and read the last (latest) (returns int)
def read_byte_latest():
    inWaiting = ser.in_waiting
    if inWaiting == 0:
        inWaiting = 1
    bytes_in = read_bytes(inWaiting)
    if len(bytes_in) != 0:
        byte_in = bytes_in[0]
    else:
        byte_in = 0
    return byte_in


# Write bytes to the serial port
def write_bytes(bytes_out):
    ser.write(bytearray(bytes_out))
    return


# Write byte to the serial port
def write_byte(byte_out):
    write_bytes([byte_out])
    return


# Compute CRC8
# https://www.microchip.com/webdoc/AVRLibcReferenceManual/group__util__crc_1gab27eaaef6d7fd096bd7d57bf3f9ba083.html
def crc8_ccitt(old_crc, new_data):
    data = old_crc ^ new_data

    for i in range(8):
        if (data & 0x80) != 0:
            data = data << 1
            data = data ^ 0x07
        else:
            data = data << 1
        data = data & 0xff
    return data


# Send a raw packet and wait for a response (CRC will be added automatically)
def send_packet(packet=[0x00, 0x00, 0x08, 0x80, 0x80, 0x80, 0x80, 0x00],
                debug=False):
    if not debug:
        bytes_out = []
        bytes_out.extend(packet)

        # Compute CRC
        crc = 0
        for d in packet:
            crc = crc8_ccitt(crc, d)
        bytes_out.append(crc)
        write_bytes(bytes_out)
        # print(bytes_out)

        # Wait for USB ACK or UPDATE NACK
        byte_in = read_byte()
        #print(byte_in, bytes_out)
        commandSuccess = (byte_in == RESP_USB_ACK)
    else:
        commandSuccess = True
    return commandSuccess


# Convert CMD to a packet
def cmd_to_packet(command, x=None, y=None):
    cmdCopy = command
    low = (cmdCopy & 0xFF)
    cmdCopy = cmdCopy >> 8
    high = (cmdCopy & 0xFF)
    cmdCopy = cmdCopy >> 8
    dpad = (cmdCopy & 0xFF)
    cmdCopy = cmdCopy >> 8
    lstick_intensity = (cmdCopy & 0xFF)
    cmdCopy = cmdCopy >> 8
    lstick_angle = (cmdCopy & 0xFFF)
    cmdCopy = cmdCopy >> 12
    rstick_intensity = (cmdCopy & 0xFF)
    cmdCopy = cmdCopy >> 8
    rstick_angle = (cmdCopy & 0xFFF)
    dpad = decrypt_dpad(dpad)
    left_x, left_y = angle(lstick_angle, lstick_intensity)
    right_x, right_y = angle(rstick_angle, rstick_intensity)

    packet = [high, low, dpad, left_x, left_y, right_x, right_y, 0x00]
    # print (hex(command), packet, lstick_angle, lstick_intensity, rstick_angle, rstick_intensity)
    return packet


# Send a formatted controller command to the MCU
def send_cmd(command=NO_INPUT):
    commandSuccess = send_packet(cmd_to_packet(command))
    return commandSuccess


# Force MCU to sync
def force_sync():
    # Send 9x 0xFF's to fully flush out buffer on device
    # Device will send back 0xFF (RESP_SYNC_START) when it is ready to sync
    write_bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

    # Wait for serial data and read the last byte sent
    wait_for_data()
    byte_in = read_byte_latest()

    # Begin sync...
    inSync = False
    if byte_in == RESP_SYNC_START:
        write_byte(COMMAND_SYNC_1)
        byte_in = read_byte()
        if byte_in == RESP_SYNC_1:
            write_byte(COMMAND_SYNC_2)
            byte_in = read_byte()
            #print(byte_in)
            if byte_in == RESP_SYNC_OK:
                inSync = True
    return inSync


# Start MCU syncing process
def sync():
    # Try sending a packet
    inSync = send_packet()
    if not inSync:
        # Not in sync: force resync and send a packet
        inSync = force_sync()
        if inSync:
            inSync = send_packet()
    return inSync


# Convert DPAD value to actual DPAD value used by Switch
def decrypt_dpad(dpad):
    if dpad == DIR_U:
        dpadDecrypt = A_DPAD_U
    elif dpad == DIR_R:
        dpadDecrypt = A_DPAD_R
    elif dpad == DIR_D:
        dpadDecrypt = A_DPAD_D
    elif dpad == DIR_L:
        dpadDecrypt = A_DPAD_L
    elif dpad == DIR_U_R:
        dpadDecrypt = A_DPAD_U_R
    elif dpad == DIR_U_L:
        dpadDecrypt = A_DPAD_U_L
    elif dpad == DIR_D_R:
        dpadDecrypt = A_DPAD_D_R
    elif dpad == DIR_D_L:
        dpadDecrypt = A_DPAD_D_L
    else:
        dpadDecrypt = A_DPAD_CENTER
    return dpadDecrypt


def close():
    ser.close()


ser = serial.Serial(port=joycon_config.port, baudrate=19200, timeout=1)
if not sync():
    print('Could not sync!')
else:
    print('Synced!')
