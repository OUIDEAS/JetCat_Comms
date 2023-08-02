import serial
import time

x = '120'

with serial.Serial('COM5', baudrate=115200, timeout=.1) as ser:
    time.sleep(1)
    ser.write(bytes('220', 'utf-8'))
    time.sleep(2)
    ser.write(bytes('120', 'utf-8'))
    print("Done")
    time.sleep(1)