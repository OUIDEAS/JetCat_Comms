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
# from _crc.lib import get_crc16z


COM_PORT = 'COM3'
START_TIME = time.time()

def main():

    TEST_DURATION = 30

    data_filename, log_filename, csv_filename = make_filenames()
    queue1 = Queue(maxsize=0) # queue size is infinite
    queue2 = Queue(maxsize=0) # queue size is infinite

    cmd_array = read_throttle_rpm_cmds("curve1.txt")
    TEST_DURATION = cmd_array[-1, 0]
    start_input = input("Are you ready to start the engine? [y/n]: ")
    if start_input.lower() == "y":
        start_countdown()
        START_TIME = time.time()

        # Create threads
        thread1_args = (queue1, data_filename, log_filename, START_TIME, TEST_DURATION, cmd_array,)
        thread1 = threading.Thread(target=interface_port_thread_func, args=thread1_args)
        thread2_args = (queue1, queue2, csv_filename, START_TIME, TEST_DURATION,)
        thread2 = threading.Thread(target=csv_thread_func, args=thread2_args)

        thread1.start()
        time.sleep(.1)
        thread2.start()

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
    else:
        print("Not starting engine...")














def interface_port_thread_func(queue1, bin_file_path, log_file_path,  START_TIME, TEST_DURATION, cmd_array):
    """
    Read the serial port of the PRO-Interface and save to a bin file. Push the
    data packets into the queue so that it can be processed in real time.

    TODO: Add sending RPM commands
    """
    with serial.Serial(COM_PORT, baudrate=115200, timeout=.1) as ser, \
    open(bin_file_path, 'ab') as dat_file, \
    open(log_file_path, 'a') as log_file:
        start_engine(ser)

        while True:
            data_packet = ser.read_until(b'\x7E\x7E')
            dat_file.write(data_packet)
            queue1.put(data_packet)
            now = time.time()



            cmd_counter = 0
            # If enough time has elapsed, send a throttle command
            if now > (START_TIME + cmd_array[cmd_counter, 0]):

                send_throttle_rpm(ser, log_file, cmd_array[cmd_counter, 1], cmd_counter)
                log_file.write(("Sent cmd at:" + str(now)) + "\n")
                log_file.write(("Time:" + str(cmd_array[cmd_counter, 0])) + "\n")
                log_file.write(("Throttle_RPM:" + str(cmd_array[cmd_counter, 1])) + "\n")
                log_file.write("\n")
                cmd_counter = cmd_counter + 1






            if now > START_TIME + TEST_DURATION:
                stop_engine(ser)
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


def start_countdown():
    print("STARTING ENGINE IN 10...")
    # time.sleep(1)
    print("STARTING ENGINE IN 9...")
    # time.sleep(1)
    print("STARTING ENGINE IN 8...")
    # time.sleep(1)
    print("STARTING ENGINE IN 7...")
    # time.sleep(1)
    print("STARTING ENGINE IN 6...")
    # time.sleep(1)
    print("STARTING ENGINE IN 5...")
    # time.sleep(1)
    print("STARTING ENGINE IN 4...")
    # time.sleep(1)
    print("STARTING ENGINE IN 3...")
    # time.sleep(1)
    print("STARTING ENGINE IN 2...")
    # time.sleep(1)
    print("STARTING ENGINE IN 1...")
    time.sleep(1)
    print("STARTING ENGINE!")


def start_engine(ser):
    # I am just going to hard code this message, even though I have to make 
    # a function that calculates it anyways. This message is the same every
    # time. The sequence number will be 1 after this command is sent.

    # Command to start the P300-PRO with binary serial interface:
    ser.write(b"\x7E\x01\x01\x01\x01\x02\x00\x01\x28\x30\x7E")


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


def read_throttle_rpm_cmds(file_path):
    # Read the throttle commands out of a text file.
    # Column 1 is time, column 2 is throttle %.
    print("Reading Command file...")
    frame = pd.read_csv(file_path)
    # Allow for expressions in the text file e.g. 25+60
    frame = frame.applymap(modify_value)
    cmd_array = frame.to_numpy(dtype='i')
    return cmd_array

def modify_value(value):
    # This function will be applied to each value in the csv file. So check if
    # a % is there, and change it to a RPM command instead of % command.
    # also evaluate expressions so that 25+60 is just 85

    if isinstance(value, str):

        if "%" in value:
            value = float(value.strip('%'))
            value = 700*value + 34000 # Map 0% to 34000rpm, 100% to 104000rpm
            value = round(value)
            value = str(value)
            
        if "+" in value:
            value = eval(value)

    return value


def send_throttle_rpm(ser, log_file, throttle_rpm, sequence_no):
    # Send the P300-PRO any throttle command.

    # Jetcat documentation:
    """
    Command Message for engine Rpm control/demand
    Message Descriptor: 0x0102
    No of data bytes in message: 2
    Data interpretation: uint16_t
    Scale: 10x RPM
    Range: 0-300000 RPM

    If demanded RPM should be out of allowed range of engine, value would
    be automatically limited to possible/allowed range!
    """

    # If you want to send the throttle 100000 to the engine, you actually
    # send the integer 10000, because uint16_t's maximum decimal value is
    # 65535.
    rpm_to_send = throttle_rpm // 10 # Truncate off decimal place
    rpm_bytes = (rpm_to_send.item()).to_bytes(2, 'big')

    sequence_no_bytes = sequence_no.to_bytes(1, 'big')

    # header without stuffing or crc16
    header_basic = b'\x01\x01\x02' + sequence_no_bytes + b'\x02' + rpm_bytes

    # Calculate the crc16 from the basic header
    # header_basic_c = ffibuilder.new("char[]", header_basic)
    # crc16_calc = get_crc16z(header_basic_c, len(header_basic_c)-1)
    crc16_calc = get_crc16z(header_basic,  len(header_basic)-1)
    print(crc16_calc)
    crc16_bytes = crc16_calc.to_bytes(2, 'big')

    # Append the crc16 bytes to the end of the basic header
    header_unstuffed = header_basic + crc16_bytes

    log_file.write("RPM to send: " + str(rpm_bytes) +"\n")
    log_file.write("CRC16 decimal: " + str(crc16_calc) +"\n")
    log_file.write("CRC16 hex: " + str(crc16_bytes) +"\n")

    # Need to stuff the header data in case there are any 0x7E or 0x7D bytes
    header_stuffed = stuff_header(header_unstuffed)
    header_send = b'\x7E' + header_stuffed + b'\x7E'


    print("Full header_send:", header_send)
    log_file.write("Full header send:" +str(header_send)+"\n")
    ser.write(header_send)

def stop_engine(ser):
    ser.write(b"\x7E\x01\x01\x01\x01\x02\x00\x00\x39\xB9\x7E")


def crc16_update(crc, data):
    ret_val = 0
    data ^= crc & 0xFF
    data ^= data << 4
    ret_val = ((((data << 8) | ((crc & 0xFF00) >> 8)) ^ (data >> 4)) ^ (data << 3))
    return ret_val

def get_crc16z(data, length):
    crc16_data = 0
    print("data: ", data, type(data), len(data))
    print("crc16_data: ",crc16_data, type(crc16_data))
    for byte in data:
        print(byte, type(byte))
        crc16_data = crc16_update(crc16_data, byte)
        print("crc16_data: ",crc16_data, type(crc16_data))
    return crc16_data

def stuff_header(header_bytes):
    # Take a header and stuff to fix any 0x7D and 0x7E problems.
    # Using a while loop so that we can update the length of the byte array,
    # that way when the array grows we still index clear to the end of it.


    byte_array1 = bytearray(header_bytes)
    i = 0
    while i < len(byte_array1):

        # You have to check for 7D first. If you don't, it will replace the
        # 0x7D inserted from 0x7E check and break your program!
        if byte_array1[i] == 0x7D:
            # Need to stuff 0x7D 0x5D in its place
            del byte_array1[i]
            insert_this = bytearray(b'\x7D\x5D')
            byte_array1[i:i] = insert_this
            print("Stuffed the 7D:", byte_array1)

        if byte_array1[i] == 0x7E:
            # Need to stuff 0x7D 0x5E in its place
            del byte_array1[i]
            insert_this = bytearray(b'\x7D\x5E')
            byte_array1[i:i] = insert_this
            print("Stuffed the 7E:", byte_array1)

        i = i + 1


    stuffed_header = bytes(byte_array1)
    return(stuffed_header)

if __name__ == '__main__':
    main()
    print("Runtime:", time.time()-START_TIME)