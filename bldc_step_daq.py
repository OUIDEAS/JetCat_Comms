"""
bldc_step_daq.py Created by Colton Wright on 3/29/2023

Collect load cell data from the NI-USB6210 for testing a BLDC ducted fan.
Recieve load cell data on AI0 and a trigger signal on AI1. Use the trigger
signal to line up RPM curve with motor start signal.


ONLY RUNS ON WINDOWS
"""

import numpy as np
import pandas as pd
import datetime
import nidaqmx
import time
import os

def save_frame(frame, start_time):
    start_time_string = start_time.strftime("%Y-%m-%d_T%H%M%S")
    filename = f'{start_time_string}_NIdaq.csv'
    today_string = datetime.datetime.now().strftime('%Y-%m-%d')
    directory = os.path.join(".","data","RC_Benchmark", today_string)
    os.makedirs(directory, exist_ok=True)
    csv_path = os.path.join(directory, filename)
    frame.to_csv(csv_path, index=False)


RUNTIME = 60
SAMPLING_RATE = 10000 # USB-6210 peaks at 250000 kS/s
N_SAMPLES = RUNTIME*SAMPLING_RATE
N_SAMPLES_PER_LOOP = 5000 # You cannot just shove 100k samples into a list
N_LOOPS = int(N_SAMPLES/N_SAMPLES_PER_LOOP)

data = np.empty((0, 2), dtype=np.float32)

test = np.array([[0, 1], [0,5]])
print(data)
print(data.shape)
print(test.shape)

sample_times = np.linspace(0,N_SAMPLES/SAMPLING_RATE,N_SAMPLES)

start_time = datetime.datetime.now()

with nidaqmx.Task() as task:

    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
    task.timing.cfg_samp_clk_timing(SAMPLING_RATE, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

    for i in range(N_LOOPS):
        reading = task.read(N_SAMPLES_PER_LOOP, timeout=nidaqmx.constants.WAIT_INFINITELY)
        data = np.vstack([data, np.array([reading[0], reading[1]])])
    full_data = np.vstack((sample_times, data)).transpose()
    frame = pd.DataFrame(full_data, columns=["Time [s]", "Voltage [V]"])

