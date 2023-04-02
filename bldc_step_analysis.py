"""
bldc_step_analysis.py

Created by Colton Wright on 3/29/2023

Script used to look at the data from the bldc_step_daq.py script and the
RC_Benchmark data. The sampling rate of the NIdaq is 10000, and that is used for
many things in this script. If you change the sampling rate later you will have
to edit this script for it to work.

"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

def main():

    folder_path = str(sys.argv[1]) # Folder containing NIdaq and RC_Benchmark data

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    for f in files:
        if "NIdaq" in f:
            NI_frame = pd.read_csv(os.path.join(folder_path, f))
        else:
            RC_frame = pd.read_csv(os.path.join(folder_path, f))


    # Get time for motor start and stop signal Negative is the trigger start
    # right now because I have wires inverted
    idx_negative, idx_positive = get_trigger_indexes(NI_frame)

    avg_peak_thrust = NI_frame[idx_negative+25000:idx_positive-25000]["Voltage [V]"].mean()
    print("Average peak thrust:", avg_peak_thrust, "[V]")

    rise_time_index = get_rise_time(NI_frame, idx_negative, avg_peak_thrust)
    print("Rise time:", NI_frame.loc[rise_time_index]["Time [s]"] - NI_frame.loc[idx_negative]["Time [s]"], "[s]")
    


    plt.figure()
    plt.plot(NI_frame["Time [s]"], NI_frame["Voltage [V]"], label="Load cell voltage")
    plt.plot(NI_frame["Time [s]"], NI_frame["Trigger [V]"], label="Trigger")
    plt.legend()
    plt.ylim(-.35, 0)
    plt.grid(True)

    save_fig2(folder_path, "rpm_time")

    plt.show()

#----------------------------------------------------------------------------

def get_trigger_indexes(df):
    """
    Pass the NIdaq frame to this function and return the indexes where the
    5V signal is triggered.
    """
    # define threshold value
    threshold = -2.5
    # Clip off noise at the beginning of the frame from the 
    df = df.iloc[50000:]
    diff = df["Trigger [V]"].diff()
    # calculate the rolling mean of signal values
    rolling_mean = df["Trigger [V]"].rolling(window=3, center=True).mean()
    # create boolean masks for when the signal crosses the threshold values
    crosses_neg = (rolling_mean < threshold) & (rolling_mean.shift(1) >= threshold)
    crosses_pos = (rolling_mean > threshold) & (rolling_mean.shift(1) <= threshold)

    # find the index of the first True value in each mask
    idx_neg = crosses_neg.idxmax()
    idx_pos = crosses_pos.idxmax()

    return idx_neg, idx_pos


def get_rise_time(df, trigger_index, peak_thrust):
    # create boolean mask to select rows with timestamps >= trigger timestamp and thrust values >= average thrust    
    mask = (df[trigger_index:]["Voltage [V]"] >= peak_thrust)

    # find the index of the first row that satisfies the boolean mask
    index = mask.idxmax()
    # print(df)
    # print(mask.loc[(index-5):(index+5)])
    return index

def save_fig2(parent_directory, file_name, tight_layout=True,\
    fig_extension="png", resolution=600):
    """
    Saves the figure inside a folder where the .csv file was found
    """
    IMAGES_PATH = os.path.join(parent_directory, "images")
    os.makedirs(IMAGES_PATH, exist_ok=True)
    path = os.path.join(IMAGES_PATH, file_name+"."+fig_extension)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)
    print("Saving plots to ", path)

if __name__ == '__main__':
    main()