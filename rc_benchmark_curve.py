import numpy as np
import pandas as pd
import sys
import os
import scipy
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt

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
# print("Input:", sys.argv[1])

folder_path = "/home/colton/Documents/GitHub/OUIDEAS/JetCat_Comms/data/RC_Benchmark/Log_2023-03-16_121238/Log_2023-03-16_121238.csv" # Full path to file
parent_directory = os.path.dirname(folder_path)
f1 = pd.read_csv(folder_path, delimiter=',', on_bad_lines='skip')

f1 = f1.interpolate(method='linear')


f1["dThrust"] = f1["Thrust (kgf)"].diff()
f1["dThrust peaks"] = f1["dThrust"][f1["dThrust"] > 0.005]
f1["dThrust valleys"] = f1["dThrust"][f1["dThrust"] < -0.005]
f1.fillna(0, inplace=True)
f1["dThrust spikes"] = f1["dThrust peaks"] + f1["dThrust valleys"]
f1["dThrust spikes"] = abs(f1["dThrust spikes"])
f1.fillna(0, inplace=True)

extrema_index = argrelextrema(f1["dThrust spikes"].values, np.greater, order=2)[0]
extrema_rows = f1.iloc[extrema_index]
# print(extrema_rows)

f1.plot(x="Time (s)", y="Thrust (kgf)", grid=True)
save_fig2(parent_directory, "Thrust")
f1.plot(x="Time (s)", y="Torque (N·m)", grid=True)
save_fig2(parent_directory, "Torque")
# f1.plot(x="Time (s)", y="dThrust")
# f1.plot(x ="Time (s)", y="dThrust peaks")
# f1.plot(x ="Time (s)", y="dThrust valleys")
# f1.plot(x ="Time (s)", y="dThrust spikes")
f1.plot(x ="Time (s)", y="Motor Optical Speed (RPM)", grid=True)
save_fig2(parent_directory, "RPM")

# Get slices of dataframe for each step the motor is taking

slice_22 = f1.iloc[884:1043]
slice_27 = f1.iloc[1083:1283]
slice_33 = f1.iloc[1324:2484]
slice_63 = f1.iloc[2524:2723]

slices = [slice_22, slice_27, slice_33, slice_63]
rpm = np.zeros(len(slices))
thrust = np.zeros(len(slices))
torque = np.zeros(len(slices))

for sl, i in zip(slices, range(len(slices))):
    rpm[i] = sl["Motor Optical Speed (RPM)"].mean()
    thrust[i] = sl["Thrust (kgf)"].mean()
    torque[i] = sl["Torque (N·m)"].mean()

rpmA = np.vstack([rpm, np.ones(len(rpm))]).T
thrust_slope, thrust_constant = np.linalg.lstsq(rpmA, thrust, rcond=None)[0]
thrust_predict = thrust_slope*rpm+thrust_constant

torque_slope, torque_constant = np.linalg.lstsq(rpmA, torque, rcond=None)[0]
torque_predict = torque_slope*rpm+torque_constant



plt.figure()
plt.plot(rpm, thrust, 'bo', label='Data Points')
plt.plot(rpm, thrust_predict, 'r-', label=("Fitted Line, y="+str(format(thrust_slope, '.4e'))+"x+"+str(format(thrust_constant, '.4e'))))
plt.legend()
plt.grid(True)
plt.title("Thrust v RPM")
save_fig2(parent_directory, "thrust_curve")

plt.figure()
plt.plot(rpm, torque, 'bo', label='Data Points')
plt.plot(rpm, torque_predict, 'r-', label=("Fitted Line, y="+str(format(torque_slope, '.4e'))+"x+"+str(format(torque_slope, '.4e'))))
plt.legend()
plt.grid(True)
plt.title("Torque v RPM")
save_fig2(parent_directory, "torque_curve")


plt.show()