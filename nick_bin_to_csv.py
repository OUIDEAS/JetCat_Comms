"""
bin_to_csv.py

Created by Colton Wright on 2/27/2023

Takes binary data file from PRO-Interface and converts to a CSV
"""

import pandas as pd
import struct
import os
import pickle
import sys
import crc

def main():
    file_path = sys.argv[1] # Full path to file

    frame = bin_to_frame(file_path)

    base_path, extension = os.path.splitext(file_path)
    frame.to_csv(base_path + ".csv", index=False) # Write csv to same location


    with open (base_path+'.pickle', 'wb') as handle:
        pickle.dump(frame, handle, protocol=pickle.HIGHEST_PROTOCOL)


def bin_to_frame(data_file_path):
    config = crc.Configuration(
        width=16,
        polynomial=0x1021,
        init_value=0x00,
        final_xor_value=0x00,
        reverse_input=True,
        reverse_output=True,
    )
    crc_calculator = crc.Calculator(config)
    with open(data_file_path, 'rb',) as file:
        my_bytes = file.read()

        list_of_list = []
        data_packet = bytearray() # initialize byte array
        i = 0
        while i < len(my_bytes)-1:

            if (my_bytes[i] == 0x7E and my_bytes[i+1] == 0x7E):
                # Two 7E in a row, new data packet starts at i+1
                j = my_bytes.find(bytes([0x7E]), i+2)
                if (j == -1): # Break if it cannot find 0x7E anywhere
                    print("Break")
                    break
                data_packet = my_bytes[i+2:j] # This is a data packet with no framing bytes
                data_packet = bytearray(data_packet)

                # CRC16 calculation:
                datastring = bytes(data_packet)
                # print("Datastring: ", datastring)
                # print("len(datastring)", len(datastring))
                datastring_no_crc = datastring[:-2] # Clip off crc number for the crc checksum
                crc16_calc = crc_calculator.checksum(datastring_no_crc)

                # Unstuff the data packet for processing
                # print(i)

                unstuffed_line = byte_unstuffing(data_packet)

                # print("unstuffed_line: ", unstuffed_line)
                # print("len(unstuffed_line): ", len(unstuffed_line))

                if len(unstuffed_line) == 33:
                    decoded_numbers = decode_line(unstuffed_line)
                    decoded_numbers.append(crc16_calc)
                    list_of_list.append(decoded_numbers)
                # else:
                    # print("Error, wrong length at i =", i)
                    # print("Broken packet: ", unstuffed_line)
                i=j

            else:
                i = i+1

        # We have now looped through all bytes in putty log, and have a list of all
        # the data. Save interpreted data into a data frame.
        data_columns = ["Engine_Address", "Message_Descriptor", "Sequence_Number",
        "Data_Byte_Count", "RPM_(setpoint)", "RPM_(setpoint%)", "RPM_(actual)", 
        "RPM_(actual%)", "EGT", "Pump_Volts_(setpoint)", "Pump_Volts_(actual)", 
        "State", "Battery_Volts", "Battery_Volt_Level%", "Battery_Current", 
        "Airspeed", "PWM-THR", "PWM-AUX","CRC16_Given","CRC16_Calculated"]
        frame = pd.DataFrame(list_of_list, columns=data_columns)

    return frame

def byte_unstuffing(byte_array):
    """
    byte_unstuffing takes the byte_array and decodes any stuffing that might
    have happened. 
    """
    # TODO: Test this function. If it does not work, engine data will become
    # corrupted.

    i = 0
    while i < len(byte_array)-1:

        # "If 0x7D should be transmitted, transmit two bytes: 0x7D and 0x5D"
        # This is from JetCat documentation
        if(byte_array[i]==0x7D and byte_array[i+1]==0x5D):
            # print("Unstuff!")
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
            # print("Unstuff")
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

    # print("decoded_packet: ", decoded_packet)
    # print("values        : ", values)
    return values



if __name__ == '__main__':
    main()