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

import modules.m2 as m2

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
    is_ready = m2.prompt_weight(weight_order[i])
    if is_ready == 'y':
        print("Collecting samples...")
        frames.append(m2.collect_samples())
        m2.save_frame(frames[i], weight_order[i], now_more)
    else:
        break
    print(i)

