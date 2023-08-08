

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
            # Create binary protocol threads
            thread1_binary_args = (queue1, bin_proto_data_filename, cmd_log_filename, START_TIME, TEST_DURATION, cmd_array, crc_calculator,)
            thread1_binary = threading.Thread(target=interface_port_thread_func_binary, args=thread1_binary_args)
            thread2_args_binary = (queue1, queue2, engine_csv_filename, START_TIME, TEST_DURATION, crc_calculator,)
            thread2_binary = threading.Thread(target=csv_thread_func_binary, args=thread2_args_binary)

            thread1_binary.start()
            time.sleep(.1)
            thread2_binary.start()

        elif comms_protocol.lower() == "ascii":
            # Create ascii protocol threads
            thread1_args_ascii = (queue1, ascii_proto_data_filename, cmd_log_filename, START_TIME, TEST_DURATION, cmd_array,crc_calculator,)
            thread1_ascii = threading.Thread(target=interface_port_thread_func_ascii, args=thread1_args_ascii)
            # thread2_args_ascii = (queue1, queue2, csv_filename, START_TIME, TEST_DURATION, crc_calculator,)
            # thread2_ascii = threading.Thread(target=csv_thread_func_ascii, args=thread2_args_ascii)

            thread1_ascii.start()
            time.sleep(.1)
            # thread2_ascii.start()

        if pro_micro_c_used.lower() == 'y':
            # Spawn pro micro thread
            thread3_args = (PRO_MICRO_COM_PORT, acc_queue, acc_data_filename, START_TIME, TEST_DURATION)
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
































"""
Thread Functions
"""
def interface_port_thread_func_binary(queue1, bin_file_path, log_file_path,  START_TIME, TEST_DURATION, cmd_array, crc_calculator):
    """
    Read the serial port of the PRO-Interface and save to a bin file. Push the
    data packets into the queue so that it can be processed in real time.
    Also send RPM commands when required.
    """
    with serial.Serial(COM_PORT, baudrate=115200, timeout=.1) as ser, \
    open(bin_file_path, 'ab') as dat_file, \
    open(log_file_path, 'a') as log_file:
        print("Starting engine...")
        start_engine_binary_protocol(ser)

        stop_flag = True
        cmd_counter = 0
        while True:
            data_packet = ser.read_until(b'\x7E\x7E')
            dat_file.write(data_packet)
            queue1.put(data_packet)
            now = time.time()


            # If enough time has elapsed, send a throttle command
            if now > (START_TIME + cmd_array[cmd_counter, 0]) and stop_flag:
                send_throttle_rpm_binary_protocol(ser, log_file, cmd_array, cmd_counter, crc_calculator, now)
                cmd_counter = cmd_counter + 1

            if now > START_TIME + TEST_DURATION and stop_flag:
                stop_engine_binary_protocol(ser)
                stop_flag = False
                cmd_counter = 0

            if now > START_TIME + TEST_DURATION+15:
                break

# csv processing
def csv_thread_func_binary(queue1, queue2, csv_filename, START_TIME, TEST_DURATION, crc_calculator):
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
            packet_to_csv(queue2, data_packet, cw_writer, START_TIME, crc_calculator)
            if time.time() > START_TIME + TEST_DURATION+15:
                break


def interface_port_thread_func_ascii(queue1, bin_file_path, log_file_path,  START_TIME, TEST_DURATION, cmd_array, crc_calculator):
    """
    Read the serial port of the PRO-Interface and save to a bin file. Push the
    data packets into the queue so that it can be processed in real time.
    Also send RPM commands when required. Use jetCat's binary protocol.
    """
    with serial.Serial(COM_PORT, baudrate=115200, timeout=.1) as ser, \
    open(bin_file_path, 'ab') as dat_file, \
    open(log_file_path, 'a') as log_file:
        print("Starting engine...")
        start_engine_ascii_protocol(ser)

        stop_flag = True
        cmd_counter = 0
        while True:
            now = time.time()
            ser.write(b'1,RAC,1\n') # Read actual values command
            ser.write(b'1,RFI,1\n') # Read fuel info command
            data_packet = ser.read(ser.in_waiting)
            dat_file.write(data_packet)
            dat_file.write(now)
            # queue1.put(data_packet)


            # If enough time has elapsed, send a throttle command
            if now > (START_TIME + cmd_array[cmd_counter, 0]) and stop_flag:
                send_throttle_rpm_ascii_protocol(ser, log_file, cmd_array, cmd_counter, now)
                cmd_counter = cmd_counter + 1


            if now > START_TIME + TEST_DURATION and stop_flag:
                stop_engine_ascii_protocol(ser)
                stop_flag = False
                cmd_counter = 0
            if now > START_TIME + TEST_DURATION+15: # Collect data after the engine stops...
                break






























"""
Non-threaded functions
"""

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

def start_engine_binary_protocol(ser):
    # I am just going to hard code this message, even though I have to make 
    # a function that calculates it anyways. This message is the same every
    # time. The sequence number will be 1 after this command is sent.

    # Command to start the P300-PRO with binary serial interface:
    ser.write(b"\x7E\x01\x01\x01\x01\x02\x00\x01\x28\x30\x7E")

def start_engine_ascii_protocol(ser):
    ser.write(b'1,tco,1\n')

def stop_engine_binary_protocol(ser):
    ser.write(b"\x7E\x01\x01\x01\x01\x02\x00\x00\x39\xB9\x7E")

def stop_engine_ascii_protocol(ser):
    ser.write(b'1,tco,0\n')

def send_throttle_rpm_binary_protocol(ser, log_file, cmd_array, cmd_counter, crc_calculator, now):
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
    throttle_rpm = cmd_array[cmd_counter, 1]
    rpm_to_send = throttle_rpm // 10 # Truncate off decimal place
    rpm_bytes = (rpm_to_send.item()).to_bytes(2, 'big')
    sequence_no = cmd_counter
    sequence_no_bytes = sequence_no.to_bytes(1, 'big')
    # header without stuffing or crc16
    header_basic = b'\x01\x01\x02' + sequence_no_bytes + b'\x02' + rpm_bytes
    # Calculate the crc16 from the basic header
    crc16_calc = crc_calculator.checksum(header_basic)
    crc16_bytes = crc16_calc.to_bytes(2, 'big')
    # Append the crc16 bytes to the end of the basic header
    header_unstuffed = header_basic + crc16_bytes
    # Need to stuff the header data in case there are any 0x7E or 0x7D bytes
    header_stuffed = stuff_header(header_unstuffed)
    header_send = b'\x7E' + header_stuffed + b'\x7E'

    log_file.write(str(now) + "\n")
    log_file.write(("Time:" + str(cmd_array[cmd_counter, 0])) + "\n")
    log_file.write("RPM sent: " + str(throttle_rpm)+ ', '+ str(rpm_bytes) +"\n")
    log_file.write("CRC16 decimal: " + str(crc16_calc) +"\n")
    log_file.write("CRC16 hex: " + str(crc16_bytes) +"\n")
    log_file.write("Full header send:" +str(header_send)+"\n")
    log_file.write("\n")
    ser.write(header_send)

def send_throttle_rpm_ascii_protocol(ser, log_file, cmd_array, cmd_counter, now):
    throttle_rpm = cmd_array[cmd_counter, 1]
    log_file.write(str(now) + "\n")
    log_file.write(("Time:" + str(cmd_array[cmd_counter, 0])) + "\n")
    log_file.write("RPM sent: " + str(throttle_rpm)+"\n")
    log_file.write("\n")
    ser.write(b'1,wrp,'+bytes(throttle_rpm)+b'\n')



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
            # print("Stuffed the 7D:", byte_array1)

        if byte_array1[i] == 0x7E:
            # Need to stuff 0x7D 0x5E in its place
            del byte_array1[i]
            insert_this = bytearray(b'\x7D\x5E')
            byte_array1[i:i] = insert_this
            # print("Stuffed the 7E:", byte_array1)

        i = i + 1


    stuffed_header = bytes(byte_array1)
    return(stuffed_header)

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


def packet_to_csv(queue2, data_packet, csv_writer, START_TIME, crc_calc):
    # print(data_packet)
    data_packet = data_packet[:-2] # Clip off the framing bytes
    # print(data_packet)
    data_packet = bytearray(data_packet)

    # CRC16 calculation:
    datastring = bytes(data_packet)
    datastring_no_crc = datastring[:-2] # Clip off crc number for the crc checksum
    # TODO: CRC Checksum
    crc16_calc = crc_calc.checksum(datastring_no_crc)
    # print(crc16_calc)
    # crc16_bytes = crc16_calc.to_bytes(2, 'big')
    # Unstuff the data packet for processing
    unstuffed_line = byte_unstuffing(data_packet)

    if len(unstuffed_line) == 33:
        processed_packet = decode_line(unstuffed_line)
        processed_packet.append(crc16_calc)
        processed_packet.insert(0, time.time()-START_TIME) # Put a timestamp at [0]

        # Check if crc16's match, it is corrupt if not
        if processed_packet[-1] == processed_packet[-2]:
            csv_writer.writerow(processed_packet)
            queue2.put(processed_packet)
        # else:
            # print("crc16's are not equal at "+str(time.time()))

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












"""
Main
"""

if __name__ == '__main__':
    main()