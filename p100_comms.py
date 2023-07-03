
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import serial
import time
import os
import datetime


COM_PORT = 'COM4'
START_TIME = time.time()

def main():
    bin_file_path, log_file, csv_file = make_filenames()
    with serial.Serial(COM_PORT, baudrate=115200, timeout=10) as ser, \
        open(bin_file_path, 'ab') as dat_file:

        data = ser.read(10)
        start_engine(ser)
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

def start_engine(ser):
    # I am just going to hard code this message, even though I have to make 
    # a function that calculates it anyways. This message is the same every
    # time. The sequence number will be 1 after this command is sent.

    # Command to start the P300-PRO with binary serial interface:
    print(ser)
    print("Sent")
    ser.write(b"\x7E\x01\x01\x01\x01\x02\x00\x01\x28\x30\x7E")




if __name__ == '__main__':
    main()

