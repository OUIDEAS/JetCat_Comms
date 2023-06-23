
import numpy as np
import pandas as pd
import serial
import os
import sys
import time
import datetime
import crc

COM_PORT = 'COM3'
def main():

    config = crc.Configuration(
        width=16,
        polynomial=0x1021,
        init_value=0x00,
        final_xor_value=0x00,
        reverse_input=True,
        reverse_output=True,
    )
    crc_calculator = crc.Calculator(config)

    log_filename = make_filename()
    cmd_file_path = sys.argv[1]
    cmd_array = read_throttle_rpm_cmds(cmd_file_path)
    TEST_DURATION = cmd_array[-1, 0]
    start_input = input("Are you ready to start the engine? [y/n]: ")
    if start_input.lower() == "y":
        start_countdown()
        START_TIME = time.time()
    with serial.Serial(COM_PORT, baudrate=115200, timeout=.1) as ser, \
    open(log_filename, 'a') as log_file:
        print("Starting engine...")
        start_engine(ser)
        cmd_counter = 0
        while True:

            now = time.time()
            # If enough time has elapsed, send a throttle command
            if now > (START_TIME + cmd_array[cmd_counter, 0]):
                send_throttle_rpm(ser, log_file, cmd_array[cmd_counter, 1], cmd_counter, crc_calculator)
                log_file.write(("Sent cmd at:" + str(now)) + "\n")
                log_file.write(("Time:" + str(cmd_array[cmd_counter, 0])) + "\n")
                log_file.write(("Throttle_RPM:" + str(cmd_array[cmd_counter, 1])) + "\n")
                log_file.write("\n")
                cmd_counter = cmd_counter + 1

            if now > START_TIME + TEST_DURATION:
                stop_engine(ser)
                break

def make_filename():
    # Create directory & filename for the log file
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    now_more = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
    FILE_PATH = os.path.join(".", "data", now, now_more )
    os.makedirs(FILE_PATH, exist_ok=True)
    log = os.path.join(FILE_PATH, (now_more + "_log.txt"))
    return log
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
def start_engine(ser):
    # I am just going to hard code this message, even though I have to make 
    # a function that calculates it anyways. This message is the same every
    # time. The sequence number will be 1 after this command is sent.

    # Command to start the P300-PRO with binary serial interface:
    print(ser)
    print("Sent")
    ser.write(b"\x7E\x01\x01\x01\x01\x02\x00\x01\x28\x30\x7E")
def send_throttle_rpm(ser, log_file, throttle_rpm, sequence_no, crc_calculator):
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

    rpm_to_send = throttle_rpm // 10 # Truncate off decimal place
    rpm_bytes = (rpm_to_send.item()).to_bytes(2, 'big')

    sequence_no_bytes = sequence_no.to_bytes(1, 'big')

    # header without stuffing or crc16
    header_basic = b'\x01\x01\x02' + sequence_no_bytes + b'\x02' + rpm_bytes

    # Calculate the crc16 from the basic header
    crc16_calc = crc_calculator.checksum(header_basic)
    print("CRC of engine RPM bytes: ", crc16_calc)
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
def stop_engine(ser):
    ser.write(b"\x7E\x01\x01\x01\x01\x02\x00\x00\x39\xB9\x7E")
if __name__ == '__main__':
    main()