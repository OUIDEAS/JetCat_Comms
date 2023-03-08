"""
ztest_thread2.py

Created by Colton Wright on 3/7/2023

Attempt to read PRO-Interface serial port, save data to .bin & .csv, with a live plot
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
import cffi
import time
import os
import multiprocessing
import csv
import threading


from queue import Queue # Allow easy, safe exchange of data between threads

import modules.m3 as m3

def animate(i, values):
    


# Data to simulate for testing!
bin_file_path = r"/home/colton/Documents/GitHub/OUIDEAS/JetCat_Comms/data/2023-02-22_T121427_data.bin"
data_filename, log_filename, csv_filename = m3.make_filenames()
queue1 = Queue(maxsize=0) # queue size is infinite

fig, ax = plt.subplots()

# Important thread, reads data, saves data, send data to main
thread1_args = (queue1, data_filename, log_filename, True,)
thread1 = threading.Thread(target=m3.read_port, args=thread1_args)
thread1.start()

time.sleep(.1)
# For simulating a PRO-Interface on the serial port
test_thread = threading.Thread(target=m3.write_file_to_port, args=(bin_file_path,))
test_thread.start()



# Open csv for writing packets:
with open(csv_filename, 'a') as csv_file:
    cw_writer = csv.writer(csv_file, delimiter=',')
    cw_writer.writerow(["Time", "Engine_Address", "Message_Descriptor", "Sequence_Number",
        "Data_Byte_Count", "RPM_(setpoint)", "RPM_(setpoint%)", "RPM_(actual)", 
        "RPM_(actual%)", "EGT", "Pump_Volts_(setpoint)", "Pump_Volts_(actual)", 
        "State", "Battery_Volts", "Battery_Volt_Level%", "Battery_Current", 
        "Airspeed", "PWM-THR", "PWM-AUX","CRC16_Given","CRC16_Calculated"])
    while True:
        # Process the queue. Pull, process, timestamp, save to csv, animate.
        data_packet = queue1.get()
        processed_packet = m3.packet_to_csv(data_packet, cw_writer)
        print(processed_packet)
        # m3.make_anim(processed_packet)
