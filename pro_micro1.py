import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import datetime
import os

PRO_MICRO_COM_PORT = 'COM7'
START_TIME = time.time()
END_TIME = START_TIME + 10

def main():


    bin_file_path, log, csv = make_filenames()
    with serial.Serial(PRO_MICRO_COM_PORT, baudrate=115200, timeout=.1) as ser, \
        open(bin_file_path, 'ab') as dat_file:
        print("Serial port opened")
        while (END_TIME > time.time()):
            data = ser.read(100)
            dat_file.write(data)
            print(data)


def make_filenames():
    # Create directory & filename for the log file
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    now_more = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
    FILE_PATH = os.path.join(".", "data", now, now_more )
    os.makedirs(FILE_PATH, exist_ok=True)
    bin_data = os.path.join(FILE_PATH, (now_more + "_data.bin" ))
    log = os.path.join(FILE_PATH, (now_more + "_log.txt"))
    csv = os.path.join(FILE_PATH, (now_more + "_data.csv"))
    return bin_data, log, csv



if __name__ == '__main__':
    main()
