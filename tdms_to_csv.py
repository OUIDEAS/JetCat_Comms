"""
tdms_to_csv.py

Created by Colton Wright on 2/27/2023

Takes binary TDMS data file from NI USB-6210 and MCCDaq E-TC and converts to a CSV
"""

import os
import pickle
import sys
import pandas as pd
from nptdms import TdmsFile
from nptdms import tdms
import matplotlib.pyplot as plt

def tdms_to_frame(file_path):
    tdms_data = TdmsFile.read(file_path)

    for group in tdms_data.groups():
        # Determine if this is a thermocouple (MCCDAQ) or Load Cell (NI DAQ) TDMSVoltage.tdms
        if group.name == "Analog":
            file_type = "MCC"
        else:
            file_type = "NI"

    if file_type == "MCC":
        # print("MCCDAQ TDMS file found...")
        mcc_group1 = tdms_data["Analog"]
        mcc_timechannel = mcc_group1["TimeStamps"]
        mcc_tempchannel1 = mcc_group1["AI0"]
        mcc_tempchannel2 = mcc_group1["AI1"]
        mcc_tempchannel3 = mcc_group1["AI2"]
        # These are numpy ndarrays
        mcc_time = mcc_timechannel[:]
        mcc_temp1 = mcc_tempchannel1[:]
        mcc_temp2 = mcc_tempchannel2[:]
        mcc_temp3 = mcc_tempchannel3[:]
        frame = pd.DataFrame({'Time [s]': mcc_time,
                              'AI0': mcc_temp1,
                              'AI1': mcc_temp2,
                              'AI2': mcc_temp3})
        return frame

    elif file_type == "NI":
        # print("NI TDMS file found...")
        
        ni_groups = tdms_data.groups()
        group_names = []
        for group in ni_groups:
            group_names.append(group.name)
        print("NI group names: ")
        print(group_names, "\n")

        ni_group1 = tdms_data[group_names[0]]
        ni_g1_allchannels = ni_group1.channels()
        channel_names = []
        for channel in ni_g1_allchannels:
            channel_names.append(channel.name)
        print("NI channel names: ")
        print(channel_names, "\n")
        ni_g1_chan1 = ni_group1[channel_names[0]]
        ni_g1_chan2 = ni_group1[channel_names[1]]

        # These are numpy ndarrays
        ni_g1_ai0_time = ni_g1_chan1.time_track()
        ni_g1_ai0_v = ni_g1_chan1[:]
        ni_g1_ai1_v = ni_g1_chan2[:]
        frame = pd.DataFrame({'Time [s]': ni_g1_ai0_time,
                              'Voltage': ni_g1_ai0_v,
                              'Voltage_ai1' : ni_g1_ai1_v})
        return frame

file_path = sys.argv[1] # Full path to file

frame = tdms_to_frame(file_path)

base_path, extension = os.path.splitext(file_path)
frame.to_csv(base_path + ".csv", index=False) # Write csv to same location


with open (base_path+'.pickle', 'wb') as handle:
    pickle.dump(frame, handle, protocol=pickle.HIGHEST_PROTOCOL)

plt.figure()
plt.plot(frame["Time [s]"], frame["Voltage"])

plt.figure()
plt.plot(frame["Time [s]"], frame["Voltage_ai1"])

plt.show()