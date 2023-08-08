

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
import csv
import struct
import crc
import pro_micro1 as pm1


COM_PORT = 'COM8'
PRO_MICRO_COM_PORT = 'COM7'
START_DATETIME = datetime.datetime.now()

def main():

    bin_proto_data_filename, ascii_proto_data_filename, cmd_log_filename, engine_csv_filename, acc_data_filename = make_filenames(START_DATETIME)
    queue1 = Queue(maxsize=0) # queue size is infinite
    queue2 = Queue(maxsize=0) # queue size is infinite
    acc_queue = Queue(maxsize=0) # queue size is infinite
    config = crc.Configuration(
        width=16,
        polynomial=0x1021,
        init_value=0x00,
        final_xor_value=0x00,
        reverse_input=True,
        reverse_output=True,
    )
    crc_calculator = crc.Calculator(config)

    cmd_file_path = sys.argv[1]
    cmd_array = read_throttle_rpm_cmds(cmd_file_path)
    TEST_DURATION = cmd_array[-1, 0]
    # Get user input for several questions
    comms_protocol = get_user_input_bin_ascii("Are you using binary or ascii protocol? [binary/ascii]: ")
    pro_micro_c_used = get_user_input_y_n("Are you using the SparkFun Pro Micro & ISM330DHCX sensor system? [y/n]: ")
    using_live_plotting = get_user_input_y_n("Plot live engine data? [y/n]: ")
    samsung_t7_autosave = get_user_input_y_n("Are you using the Samsung T7 for backup? [y/n]: ")
    start_input = get_user_input_y_n("Are you ready to start the engine? [y/n]: ")

    if start_input.lower() == "y":
        start_countdown()
        START_TIME = time.time()

        if comms_protocol.lower() == "binary":
            # Create threads
            thread1_args = (queue1, bin_proto_data_filename, cmd_log_filename, START_TIME, TEST_DURATION, cmd_array, crc_calculator,)
            thread1 = threading.Thread(target=interface_port_thread_func, args=thread1_args)
            thread2_args = (queue1, queue2, engine_csv_filename, START_TIME, TEST_DURATION, crc_calculator,)
            thread2 = threading.Thread(target=csv_thread_func, args=thread2_args)

            thread1.start()
            time.sleep(.1)
            thread2.start()

        elif comms_protocol.lower() == "ascii":
            # Create threads
            thread1_args_ascii = (queue1, data_filename, log_filename, START_TIME, TEST_DURATION, cmd_array,crc_calculator,)
            thread1_ascii = threading.Thread(target=interface_port_thread_func_ascii, args=thread1_args_ascii)
            thread2_args_ascii = (queue1, queue2, csv_filename, START_TIME, TEST_DURATION, crc_calculator,)
            thread2_ascii = threading.Thread(target=csv_thread_func_ascii, args=thread2_args_ascii)

            thread1.start()
            time.sleep(.1)
            thread2.start()

        if pro_micro_c_used.lower() == 'y':
            # Spawn pro micro thread
            acc_data_file = pm1.make_pm1_filename(START_DATETIME)
            thread3_args = (PRO_MICRO_COM_PORT, acc_queue, acc_data_file, START_TIME, TEST_DURATION)
            thread3 = threading.Thread(target=pm1.pro_micro_thread_func(), args=thread3_args)
            thread3.start()

        if using_live_plotting.lower() == 'y':
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

        if samsung_t7_autosave.lower() == 'y':
            # We are using the T7, plotting window just closed, backup all the data to the T7
            pass
    else:
        print("Not starting engine...")



def start_countdown():
    print("STARTING ENGINE IN 10...")
    time.sleep(1)
    print("STARTING ENGINE IN 9...")
    time.sleep(1)
    print("STARTING ENGINE IN 8...")
    time.sleep(1)
    print("STARTING ENGINE IN 7...")
    time.sleep(1)
    print("STARTING ENGINE IN 6...")
    time.sleep(1)
    print("STARTING ENGINE IN 5...")
    time.sleep(1)
    print("STARTING ENGINE IN 4...")
    time.sleep(1)
    print("STARTING ENGINE IN 3...")
    time.sleep(1)
    print("STARTING ENGINE IN 2...")
    time.sleep(1)
    print("STARTING ENGINE IN 1...")
    time.sleep(1)
    print("STARTING ENGINE!")


def interface_port_thread_func(queue1, bin_file_path, log_file_path,  START_TIME, TEST_DURATION, cmd_array, crc_calculator):
    """
    Read the serial port of the PRO-Interface and save to a bin file. Push the
    data packets into the queue so that it can be processed in real time.
    """
    with serial.Serial(COM_PORT, baudrate=115200, timeout=.1) as ser, \
    open(bin_file_path, 'ab') as dat_file, \
    open(log_file_path, 'a') as log_file:
        # print("Start engine")
        # start_engine(ser)

        # stop_flag = True
        # cmd_counter = 0
        while True:
            data_packet = ser.read_until(b'\x7E\x7E')
            dat_file.write(data_packet)
            # queue1.put(data_packet)
            # now = time.time()


            # # If enough time has elapsed, send a throttle command
            # if now > (START_TIME + cmd_array[cmd_counter, 0]) and stop_flag:

            #     send_throttle_rpm(ser, log_file, cmd_array[cmd_counter, 1], cmd_counter, crc_calculator)
            #     log_file.write(("Sent cmd at:" + str(now)) + "\n")
            #     log_file.write(("Time:" + str(cmd_array[cmd_counter, 0])) + "\n")
            #     log_file.write(("Throttle_RPM:" + str(cmd_array[cmd_counter, 1])) + "\n")
            #     log_file.write("\n")
            #     cmd_counter = cmd_counter + 1






            # if now > START_TIME + TEST_DURATION and stop_flag:
            #     stop_engine(ser)
            #     stop_flag = False
            #     cmd_counter = 0
            # if now > START_TIME + TEST_DURATION+15:
            #     break

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
            
        else:
            value = eval(value)

    return value

def make_filenames(file_date_time):
    # Create directory & filename for the log file
    now = file_date_time.strftime("%Y-%m-%d")
    now_more = file_date_time.strftime("%Y-%m-%dT%H%M%S")
    FILE_PATH = os.path.join(".", "data", now, now_more )
    os.makedirs(FILE_PATH, exist_ok=True)
    bin_proto_data = os.path.join(FILE_PATH, (now_more + "_binary_protocol_raw_data.bin" ))
    ascii_proto_data = os.path.join(FILE_PATH, (now_more + "_ascii_protocol_raw_data.bin" ))
    cmd_log = os.path.join(FILE_PATH, (now_more + "_command_log.txt"))
    engine_csv = os.path.join(FILE_PATH, (now_more + "_engine_data.csv"))
    acc_data = os.path.join(FILE_PATH, (now_more + "_ISM330DHCX_data.txt" ))

    return bin_proto_data, ascii_proto_data, cmd_log, engine_csv, acc_data

def get_user_input_y_n(prompt):

    while True:
        response = input(prompt)
        if response.lower not in ('y', 'n'):
            print("Invalid response.")
            continue
        else:
            break
    return response

def get_user_input_bin_ascii(prompt):
    while True:
        response = input(prompt)
        if response.lower not in ('binary', 'ascii'):
            print("Invalid response.")
            continue
        else:
            break
    return response

if __name__ == '__main__':
    main()