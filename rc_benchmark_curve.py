import numpy as np
import pandas as pd
import sys
import os
import scipy
from scipy.linalg import lstsq
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

folder_path = r"C:\Users\colto\Documents\GitHub\JetCat_Comms\data\RC_Benchmark\Log_2023-03-16_160024\Log_2023-03-16_160024.csv" # Full path to file
parent_directory = os.path.dirname(folder_path)
f1 = pd.read_csv(folder_path, delimiter=',', on_bad_lines='skip')

f1 = f1.interpolate(method='linear')
# print(f1)

f1["dThrust"] = f1["Thrust (kgf)"].diff()
f1["dThrust peaks"] = f1["dThrust"][f1["dThrust"] > 0.005]
f1["dThrust valleys"] = f1["dThrust"][f1["dThrust"] < -0.005]
f1.fillna(0, inplace=True)
f1["dThrust spikes"] = f1["dThrust peaks"] + f1["dThrust valleys"]
f1["dThrust spikes"] = abs(f1["dThrust spikes"])
f1.fillna(0, inplace=True)

# extrema_index = argrelextrema(f1["dThrust spikes"].values, np.greater, order=2)[0]
# extrema_rows = f1.iloc[extrema_index]
# # print(extrema_rows)

f1.plot(x="Time (s)", y="Thrust (kgf)", grid=True)
save_fig2(parent_directory, "Thrust")
f1.plot(x="Time (s)", y="Torque (N·m)", grid=True)
save_fig2(parent_directory, "Torque")
# # f1.plot(x="Time (s)", y="dThrust")
# # f1.plot(x ="Time (s)", y="dThrust peaks")
# # f1.plot(x ="Time (s)", y="dThrust valleys")
# # f1.plot(x ="Time (s)", y="dThrust spikes")
f1.plot(x ="Time (s)", y="Motor Optical Speed (RPM)", grid=True)
save_fig2(parent_directory, "RPM")

# # Get slices of dataframe for each step the motor is taking

slice_1 = f1.iloc[563:723]
slice_2 = f1.iloc[803:964]
slice_3 = f1.iloc[1024:1204]
slice_4 = f1.iloc[1244:1443]
slice_5 = f1.iloc[1484:1685]
slice_6 = f1.iloc[1726:1927]
slice_7 = f1.iloc[1967:2167]
slice_8 = f1.iloc[2247:2407]
slice_9 = f1.iloc[2447:2647]
slice_10 = f1.iloc[2687:2887]
slice_11 = f1.iloc[2927:3127]
slice_12 = f1.iloc[3167:3367]
slice_13 = f1.iloc[3407:3607]
slice_14 = f1.iloc[3647:3847]
slice_15 = f1.iloc[3887:4087]
slice_16 = f1.iloc[4127:4327]
slice_17 = f1.iloc[4367:4567]
slice_18 = f1.iloc[4607:7967]

slices = [slice_1, slice_2, slice_3, slice_4, slice_5,
          slice_6, slice_7, slice_8, slice_9, slice_10,
          slice_11, slice_12, slice_13, slice_14, slice_15,
          slice_16, slice_17, slice_18]
rpm = np.zeros(len(slices))
thrust = np.zeros(len(slices))
torque = np.zeros(len(slices))

for sl, i in zip(slices, range(len(slices))):
    # sl.plot(x ="Time (s)", y="Motor Optical Speed (RPM)", grid=True)
    rpm[i] = sl["Motor Optical Speed (RPM)"].mean()
    thrust[i] = sl["Thrust (kgf)"].mean()
    torque[i] = sl["Torque (N·m)"].mean()

n = 3
rpmA = np.vander(rpm, n+1, increasing=True)
tr_coeffs, tr_residuals, tr_rank, tr_s = lstsq(rpmA, thrust)
to_coeffs, to_residuals, to_rank, to_s = lstsq(rpmA, torque)
# print(tr_coeffs)
# print(to_coeffs)
# rpmA = np.vstack([rpm, np.ones(len(rpm))]).T
# thrust_slope, thrust_constant = np.linalg.lstsq(rpmA, thrust, rcond=None)[0]
# thrust_lstsq = np.linalg.lstsq(rpmA, thrust, rcond=None)
# print(thrust_lstsq)
# print(thrust_slope)
# print(thrust_constant)
# thrust_predict = thrust_slope*rpm+thrust_constant

# torque_slope, torque_constant = np.linalg.lstsq(rpmA, torque, rcond=None)[0]
# torque_predict = torque_slope*rpm+torque_constant


x = np.linspace(rpm[0], rpm[-1], 1000)
plt.figure()
plt.plot(rpm, thrust, 'bo', label='Data Points')
plt.plot(x, tr_coeffs[3]*x**3+tr_coeffs[2]*x**2+tr_coeffs[1]*x+tr_coeffs[0], 'r-', label=("Fitted Line"))#+str(format(thrust_slope, '.4e'))+"x+"+str(format(thrust_constant, '.4e'))))
plt.legend()
plt.grid(True)
plt.title("Thrust v RPM")
plt.xlabel("Time [s]")
plt.ylabel("Thrust (kgf)")
save_fig2(parent_directory, "thrust_curve")
print("Thrust v RPM:")
print(str(format(tr_coeffs[3], '.4e'))+"x^3+"+str(format(tr_coeffs[2], '.4e'))+"x^2+"+str(format(tr_coeffs[1], '.4e'))+"x+"+str(format(tr_coeffs[0], '.4e')))

plt.figure()
plt.plot(rpm, torque, 'bo', label='Data Points')
plt.plot(x, to_coeffs[3]*x**3+to_coeffs[2]*x**2+to_coeffs[1]*x+to_coeffs[0], 'r-', label=("Fitted Line"))#+str(format(torque_slope, '.4e'))+"x+"+str(format(torque_slope, '.4e'))))
plt.legend()
plt.grid(True)
plt.title("Torque v RPM")
plt.xlabel("Time [s]")
plt.ylabel("Torque (N m)")
save_fig2(parent_directory, "torque_curve")
print("Torque vs RPM:")
print(str(format(to_coeffs[3], '.4e'))+"x^3+"+str(format(to_coeffs[2], '.4e'))+"x^2+"+str(format(to_coeffs[1], '.4e'))+"x+"+str(format(to_coeffs[0], '.4e')))


plt.show()