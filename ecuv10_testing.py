import serial
import time
import codecs
with serial.Serial('COM3', 9600) as ser:

    # This will get engine type, ECU version, last run time, etc.
    ser.write(bytes.fromhex('0d 0d 0d 31 2c 52 54 59 2c 31 0d 31 2c 52 53 4e 2c 31 0d'))
    time.sleep(.1)
    print(ser.read_all())

    # This will get engine data.
    ser.write(bytes.fromhex('31 2c 52 41 43 2c 31 0d'))
    time.sleep(.1)
    print(ser.read_all())

    # This is another command sent while getting engine data
    ser.write(bytes.fromhex('31 2c 52 41 49 2c 30 0d'))
    time.sleep(.1)
    print(ser.read_all())

    # This is yet another command sent while getting engine data
    ser.write(bytes.fromhex('31 2c 52 46 49 2c 30 0d'))
    time.sleep(.1)
    print(ser.read_all())

    # This does not work and is why the jetcat_comms_ECU code does not work.
    ser.write(b'1,RAC,1\r') # Read actual values command
    time.sleep(.1)
    print(ser.read_all())
    # print('1,RAC,1\n'.encode('hex_codec'))

print(codecs.decode('0d0d0d312c5254592c310d312c52534e2c310d', 'hex').decode('utf-8'))
print(codecs.decode('312c5241432c310d', 'hex').decode('utf-8'))
print(codecs.decode('312c5241492c300d', 'hex').decode('utf-8'))
print(codecs.decode('312c5246492c300d', 'hex').decode('utf-8'))
# print(b'1,tco,1\r'.hex())
print("Below are my hex prints:")
print(b"1,RSN,1\r".hex())
print(b'1,RAC,1\r'.hex())
# print()
# print('1,tco,1\r')
# print(time.time())