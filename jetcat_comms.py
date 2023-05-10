"""
jetcat_comms.py

Created by Colton Wright on 5/10/2023

Read PRO-Interface serial port, save data to .bin & .csv, with a live animation
of data. Must also be able to send throttle commands to the engine.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import serial
import threading
from queue import Queue # Allow easy, safe exchange of data between threads
import os
import sys
import time
import datetime
import cffi
import csv
import struct

COM_PORT = 'COM3'
START_TIME = time.time()

def main():

    START_TIME = time.time()
    TEST_DURATION = 120

    data_filename, log_filename, csv_filename = make_filenames()
    queue1 = Queue(maxsize=0) # queue size is infinite
    queue2 = Queue(maxsize=0) # queue size is infinite

    # Create threads
    thread1_args = (queue1, data_filename, log_filename, START_TIME, TEST_DURATION,)
    thread1 = threading.Thread(target=interface_port_thread_func, args=thread1_args)
    thread2_args = (queue1, queue2, csv_filename, START_TIME, TEST_DURATION,)
    thread2 = threading.Thread(target=csv_thread_func, args=thread2_args)

    thread1.start()
    time.sleep(.1)
    thread2.start()



    # thread1.join()
    # thread2.join()


    # CSV is being written to, let's plot...
    time.sleep(.5)
    fig = plt.figure()
    ax = fig.add_subplot(2,2,1)
    ax2 = fig.add_subplot(2,2,2)
    ax3 = fig.add_subplot(2,2,3)
    ax4 = fig.add_subplot(2,2,4)

    data = []
    ani_args = (data, queue2, ax,ax2,ax3,ax4, START_TIME, TEST_DURATION)
    ani = animation.FuncAnimation(fig, update_anim, fargs=ani_args, interval = 100, blit=False, save_count=10)
    fig.tight_layout()
    plt.show()
    print("Hello")















def interface_port_thread_func(queue1, bin_file_path, log_file_path,  START_TIME, TEST_DURATION):
    """
    Read the serial port of the PRO-Interface and save to a bin file. Push the
    data packets into the queue so that it can be processed in real time.

    TODO: Add sending RPM commands
    """
    with serial.Serial(COM_PORT, baudrate=115200, timeout=.25) as ser, \
    open(bin_file_path, 'ab') as dat_file, \
    open(log_file_path, 'a') as log_file:
        while True:
            data_packet = ser.read_until(b'\x7E\x7E')
            dat_file.write(data_packet)
            queue1.put(data_packet)
            if time.time() > START_TIME + TEST_DURATION:
                break


# csv processing
def csv_thread_func(queue1, queue2, csv_filename, START_TIME, TEST_DURATION):
    # Open csv for writing packets:
    with open(csv_filename, 'w', newline='') as csv_file:
        cw_writer = csv.writer(csv_file, delimiter=',')
        cw_writer.writerow(["Time", "Engine_Address", "Message_Descriptor",
            "Sequence_Number", "Data_Byte_Count", "RPM_(setpoint)",
            "RPM_(setpoint%)", "RPM_(actual)", "RPM_(actual%)", "EGT",
            "Pump_Volts_(setpoint)", "Pump_Volts_(actual)", "State",
            "Battery_Volts", "Battery_Volt_Level%", "Battery_Current", 
            "Airspeed", "PWM-THR", "PWM-AUX","CRC16_Given","CRC16_Calculated"])
        while True:
            # Process the queue. Pull, process, timestamp, save to csv, animate.
            data_packet = queue1.get()
            packet_to_csv(queue2, data_packet, cw_writer, START_TIME)
            if time.time() > START_TIME + TEST_DURATION:
                break


def packet_to_csv(queue2, data_packet, csv_writer, START_TIME):
    # print(data_packet)
    data_packet = data_packet[:-2] # Clip off the framing bytes
    # print(data_packet)
    data_packet = bytearray(data_packet)

    # CRC16 calculation:
    datastring = bytes(data_packet)
    # TODO: CRC Checksum
    # data = ffibuilder.new("char[]", datastring)
    # crc16_calculation = get_crc16z(data, len(datastring)-2)

    # Unstuff the data packet for processing
    unstuffed_line = byte_unstuffing(data_packet)

    if len(unstuffed_line) == 33:
        processed_packet = decode_line(unstuffed_line)
        # processed_packet.append(crc16_calculation)
        processed_packet.insert(0, time.time()-START_TIME) # Put a timestamp at [0]
        # print(processed_packet, end='')
        csv_writer.writerow(processed_packet)
        queue2.put(processed_packet)
        # print(processed_packet)

        # return processed_packet


def byte_unstuffing(byte_array):
    """
    byte_unstuffing takes the byte_array and decodes any stuffing that might
    have happened. 
    """
    i = 0
    while i < len(byte_array)-1:

        # "If 0x7D should be transmitted, transmit two bytes: 0x7D and 0x5D"
        # This is from JetCat documentation
        if(byte_array[i]==0x7D and byte_array[i+1]==0x5D):
            # Delete the extra byte if not at the end of the array
            if i+2 < len(byte_array):
                byte_array.pop(i+1)
            else:
                byte_array.pop(i+1)
                break
            i -= 1  # decrement i to re-check the current byte

        # "If 0x7E should be transmitted, transmit two bytes: 0x7D and 0x5E"
        # This is from JetCat documentation
        elif(byte_array[i]==0x7D and byte_array[i+1]==0x5E):
            # Replace two bytes with 0x7E
            byte_array[i] = 0x7E
            # Delete the extra byte if not at the end of the array
            if i+2 < len(byte_array):
                byte_array.pop(i+1)
            else:
                byte_array.pop(i+1)
                break
            i -= 1  # decrement i to re-check the current byte

        i += 1

    return byte_array


def decode_line(byte_array):
    """
    decode_line Decodes a line of bytes with the framing bytes included. Has
    nothing built in for byte stuffing or checksum yet.

    :param byte_array: byte_array is <class 'bytearray'>. Has no framing
    bytes included
    :return: Returns a Series of the processed data in order of JetCat
    documentation
    """

    byte_format = ">BHBB HHHHHHHBHBHHHH H"
    values = struct.unpack(byte_format, byte_array)
    values = list(values)

    # Apply scaling factors to the appropriate fields
    values[4] *= 10  # setpoint_rpm
    values[5] *= 0.01  # setpoint_rpm_percent
    values[6] *= 10  # actual_rpm
    values[7] *= 0.01  # actual_rpm_percent
    values[8] *= 0.1  # exhaust_gas_temp
    values[9] *= 0.01  # setpoint_pump_volts
    values[10] *= 0.01  # actual_pump_volts
    values[12] *= 0.01 # Battery Volts
    values[13] *= 0.5 # Battery avolt level %
    values[14] *= 0.01 # Battery current
    values[15] *= 0.1 # Airspeed
    values[16] *= 0.1 # PWM-THR Channel
    values[17] *= 0.1 # PWM-AUX Channel

    return values


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


# Plotting
def update_anim(frame, data_list, queue2, ax, ax2, ax3, ax4, START_TIME, TEST_DURATION):
    while not queue2.empty():
        data_list.append(queue2.get())
    # print(data_list)
    data = np.array(data_list)
    if data.any() == True:
        x = data[:, 0]
        y = data[:, 5]
        y2 = data[:, 7]
        y3 = data[:, 11]
        y4 = data[:, 9]
        # print("y::", y)
        ax.clear()
        ax.plot(x,y)
        ax.grid(True)
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("RPM_(setpoint)")
        ax.set_ylim([0, 105000])
        ax2.clear()
        ax2.plot(x,y2)
        ax2.grid(True)
        ax2.set_xlabel("Time [s]")
        ax2.set_ylabel("RPM_(actual)")
        ax2.set_ylim([0, 105000])

        ax3.clear()
        ax3.plot(x,y3)
        ax3.grid(True)
        ax3.set_xlabel("Time [s]")
        ax3.set_ylabel("Pump_Volts_(actual)")
        ax3.set_ylim([0, 5.5])
        ax4.clear()
        ax4.plot(x,y4)
        ax4.grid(True)
        ax4.set_xlabel("Time [s]")
        ax4.set_ylabel("EGT")
        ax4.set_ylim([0, 800])
        if time.time() > START_TIME + TEST_DURATION:
            plt.close()


if __name__ == '__main__':
    main()
    print("Runtime:", time.time()-START_TIME)