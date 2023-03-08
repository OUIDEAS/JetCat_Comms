import numpy as np
import serial
import datetime
import os
import time
import struct
import csv
from cffi import FFI
from _crc.lib import get_crc16z

ffibuilder = FFI()


def write_file_to_port(file_path):
    """
    Writes PRO-Interface .bin data file to the serial port so that it can be
    read later. Useful for simulating a run of the engine. This is in a thread
    because it takes forever for this to write the entire .bin file
    """
    f = open(file_path, 'rb')
    to_write = f.read()
    with serial.Serial('/dev/pts/3', baudrate=115200, timeout=.25) as ser:
        ser.write(to_write)

def read_port(queue1, bin_file_path, log_file_path, testing):
    """
    Read the serial port of the PRO-Interface and save to a bin file. Push the
    data packets into the queue so that it can be processed in real time.
    """
    with serial.Serial('/dev/pts/2', baudrate=115200, timeout=.25) as ser, \
    open(bin_file_path, 'ab') as dat_file, \
    open(log_file_path, 'a') as log_file:
        while True:
            data_packet = ser.read_until(b'\x7E\x7E')
            dat_file.write(data_packet)
            queue1.put(data_packet)

            if testing:
                time.sleep(.001) # Slow to 20 Hz for testing readings

def packet_to_csv(data_packet, csv_writer, start_time):
    # print(data_packet)
    data_packet = data_packet[:-2] # Clip off the framing bytes
    # print(data_packet)
    data_packet = bytearray(data_packet)

    # CRC16 calculation:
    datastring = bytes(data_packet)
    data = ffibuilder.new("char[]", datastring)
    crc16_calculation = get_crc16z(data, len(datastring)-2)

    # Unstuff the data packet for processing
    unstuffed_line = byte_unstuffing(data_packet)

    if len(unstuffed_line) == 33:
        processed_packet = decode_line(unstuffed_line)
        processed_packet.append(crc16_calculation)
        processed_packet.insert(0, time.time()-start_time) # Put a timestamp at [0]
        csv_writer.writerow(processed_packet)

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



# csv processing
def csv_thread_func(queue1, csv_filename):
    # Open csv for writing packets:
    start_time = time.time()
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
            packet_to_csv(data_packet, cw_writer, start_time)






# Plotting
def update(frame, csv_filename, ax, ax2, ax3, ax4):
    data = np.genfromtxt(csv_filename, delimiter=',')
    # print(data)
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
    ax2.clear()
    ax2.plot(x,y2)
    ax2.grid(True)
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("RPM_(actual)")
    ax3.clear()
    ax3.plot(x,y3)
    ax3.grid(True)
    ax3.set_xlabel("Time [s]")
    ax3.set_ylabel("Pump_Volts_(actual)")
    ax4.clear()
    ax4.plot(x,y4)
    ax4.grid(True)
    ax4.set_xlabel("Time [s]")
    ax4.set_ylabel("EGT")