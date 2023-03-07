"""
ztest_thread2.py

Created by Colton Wright on 3/7/2023

Attempt to read PRO-Interface serial port, save data to .bin & .csv, with a live plot
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import serial
import cffi
import time
import os
import multiprocessing
import threading

from queue import Queue # Allow easy, safe exchange of data between threads

import modules.m3 as m3

# Data to simulate for testing!
bin_file_path = r"/home/colton/Documents/GitHub/OUIDEAS/JetCat_Comms/data/2023-02-22_T121427_data.bin"

print(b'\x7E')

# For simulating a PRO-Interface on the serial port
thread1 = threading.Thread(target=m3.write_file_to_port, args=(bin_file_path,))
thread1.start()
thread2 = threading.Thread(target=m3.read_port, args=())
thread2.start()

