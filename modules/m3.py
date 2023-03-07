import serial

def write_file_to_port(file_path):
    """
    Writes PRO-Interface .bin data file to the serial port so that it can be
    read later. Useful for simulating a run of the engine.
    """
    f = open(file_path, 'rb')
    to_write = f.read()
    # print(to_write)
    # print(type(to_write))
    with serial.Serial('/dev/pts/5', baudrate=115200, timeout=.25) as ser:
        ser.write(to_write)

def read_port():
    with serial.Serial('/dev/pts/4', baudrate=115200, timeout=.25) as ser:
        while True:
            bytes = ser.read_until(b'\x7E')
            print(bytes)
            print("Y")