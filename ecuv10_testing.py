import serial
import time
import codecs
with serial.Serial('COM8', 9600) as ser:

    # This will get engine type, ECU version, last run time, etc.
    ser.write(bytes.fromhex('0d 0d 0d 31 2c 52 54 59 2c 31 0d 31 2c 52 53 4e 2c 31 0d'))
    time.sleep(1)
    print(ser.read_all())

    # This will get engine data.
    ser.write(bytes.fromhex('31 2c 52 41 43 2c 31 0d'))
    time.sleep(1)
    print(ser.read_all())

    # This is another command sent while getting engine data
    ser.write(bytes.fromhex('31 2c 52 41 49 2c 30 0d'))
    time.sleep(1)
    print(ser.read_all())

    # This is yet another command sent while getting engine data
    ser.write(bytes.fromhex('31 2c 52 46 49 2c 30 0d'))
    time.sleep(1)
    print(ser.read_all())


print(codecs.decode('0d0d0d312c5254592c310d312c52534e2c310d', 'hex').decode('utf-8'))
print(codecs.decode('312c5241432c310d', 'hex').decode('utf-8'))
print(codecs.decode('312c5241492c300d', 'hex').decode('utf-8'))
print(codecs.decode('312c5246492c300d', 'hex').decode('utf-8'))