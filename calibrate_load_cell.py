"""
calibrate_load_cell.py
Created by Colton Wright on 3/3/2023

Run this program to recieve prompts on what weights to hang from the load
cell for calibration, tell the computer when the weights are hung, and
automatically sample the load cell for a certain period of time, saving the
files together in the correct format so that calibration_curve.py can generate
the curves for you right after calibration.

ONLY RUNS ON WINDOWS 10
"""

import numpy as np
import pandas as pd
import datetime
import nidaqmx
import time
import os


def main():

    # Change this when you actually measure the weights
    values = {"40aF": 40.001,
            "40bF": 39.999,
            "35aF": 35.001,
            "40aR": -40.001,
            "40bR": -39.999,
            "35aR": -35.001
            }
    now_more = datetime.datetime.today().strftime("%Y-%m-%dT%H%M%S")
    weight_order = ("1_40aF", "2_40aR", "3_40aR_40bF", "4_40bF_35aF", "5_40bF")
    frames = []
    for i in range(len(weight_order)):
        print("Hello")
        is_ready = prompt_weight(weight_order[i])
        if is_ready == 'y':
            print("Collecting samples...")
            frames.append(collect_samples())
            save_frame(frames[i], weight_order[i], now_more)
        else:
            break
        print(i)



def collect_samples():
    """
    Collect the samples for the current weight that is hanging off of the cell.
    Returns a data frame
    """

    n_samples = 100000 # Take 100k samples for each weight hanging
    sampling_rate = 10000 # USB-6210 peaks at 250000 kS/s
    data = np.array([])
    sample_times = np.linspace(0,n_samples/sampling_rate,n_samples)
    with nidaqmx.Task() as task:

        task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
        task.timing.cfg_samp_clk_timing(sampling_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

        n_samples_per_loop = 5000 # You cannot just shove 100k samples into a list
        n_loops = int(n_samples/n_samples_per_loop)
        for i in range(n_loops):
            reading = task.read(n_samples_per_loop, timeout=nidaqmx.constants.WAIT_INFINITELY)
            data = np.append(data, reading)
        full_data = np.vstack((sample_times, data)).transpose()
        frame = pd.DataFrame(full_data, columns=["Time [s]", "Voltage [V]"])
    print("Done")
    return frame

def prompt_weight(input_string):
    """
    Prompt the user to hang the appropriate weights off of the load cell
    """
    substrings = input_string.split("_")
    weights_to_hang = []
    which_side = []
    for sub in substrings:
        # print(sub)
        weights_to_hang.append(sub[:-1])
        which_side.append(sub[-1])

    which_side_long = []
    for el in which_side:
        if el == 'R':
            which_side_long.append("Rear")
        elif el == 'F':
            which_side_long.append("Front")
    
    # print(weights_to_hang)
    # print(which_side_long)
    print(which_side)
    print(which_side_long)
    print(weights_to_hang)

    for i in range(0, len(weights_to_hang)-1):
        print(i)
        if i == 0:
            print("Please hang weight " + weights_to_hang[i+1] + " off the " + which_side_long[i] + " side of the load cell")
        else:
            print("Also hang " +  weights_to_hang[i+1] + " off the " + which_side_long[i])
    is_ready = input("Are you ready to collect samples? [y/n]: ")

    return is_ready




def save_frame(frame, weight, now):
    parent_directory = "."
    csv_path = os.path.join(parent_directory, "data", now)
    os.makedirs(csv_path, exist_ok=True)
    path = os.path.join(csv_path, weight)
    frame.to_csv(path, index=False)

if __name__ == '__main__':
    main()