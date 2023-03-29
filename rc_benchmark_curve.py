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


print("Input:", sys.argv[1])

folder_path = str(sys.argv[1])

# folder_path = "/home/colton/Documents/GitHub/OUIDEAS/JetCat_Comms/data/RC_Benchmark/2023-03-20/Log_2023-03-20_114941/Log_2023-03-20_114941.csv" # Full path to file
parent_directory = os.path.dirname(folder_path)
f1 = pd.read_csv(folder_path, delimiter=',', on_bad_lines='skip')
f1 = f1.interpolate(method='linear')
f1.plot(x ="Time (s)", y="Motor Optical Speed (RPM)", grid=True)
save_fig2(parent_directory, "RPM_raw")

first_nonzero_rpm_index = f1["Motor Optical Speed (RPM)"].ne(0).idxmax() + 3
start_time_motor = f1["Time (s)"][first_nonzero_rpm_index]
f2 = f1[first_nonzero_rpm_index:].copy()
f2["Time (s)"] = f2["Time (s)"].sub(start_time_motor)

f2.plot(x ="Time (s)", y="Motor Optical Speed (RPM)", grid=True)
save_fig2(parent_directory, "RPM")
f2.plot(x="Time (s)", y="Torque (N·m)", grid=True)
save_fig2(parent_directory, "Torque")
f2.plot(x="Time (s)", y="Thrust (kgf)", grid=True)
save_fig2(parent_directory, "Thrust")

n_data_points = 35
time_segment = np.arange(0, 82, 3) + 0.5
time_segment_end = time_segment + 2
rpm = np.zeros(len(time_segment))
thrust = np.zeros(len(time_segment))
torque = np.zeros(len(time_segment))

for i in range(len(time_segment)):

    slice_start_index = (f2["Time (s)"] - (time_segment[i])).apply(abs).idxmin()
    slice_stop_index = (f2["Time (s)"] - time_segment_end[i]).apply(abs).idxmin()
    # print("Start: ", slice_start_index)
    # print("Stop: ", slice_stop_index)
    frame_slice = f2[slice_start_index:slice_stop_index]
    rpm[i] = frame_slice["Motor Optical Speed (RPM)"].mean()
    thrust[i] = frame_slice["Thrust (kgf)"].mean()
    torque[i] = frame_slice["Torque (N·m)"].mean()
    # frame_slice.plot(x ="Time (s)", y="Motor Optical Speed (RPM)", grid=True)

# Plot RPM to see if it's sliced okay...
plt.figure()
plt.plot(f2["Time (s)"], f2["Motor Optical Speed (RPM)"])
plt.grid(True)
plt.xlabel("Time (s)")
plt.ylabel("Motor Optical Speed (RPM)")
for time, time_end in zip(time_segment, time_segment_end):
    plt.axvline(x=time, color='r')
    plt.axvline(x=time_end, color='tab:orange')
save_fig2(parent_directory, "Slices")



n = 3
rpmA = np.vander(rpm, n+1, increasing=True)
thrust_coeffs, thrust_residuals, thrust_rank, thrust_s = lstsq(rpmA, thrust)
torque_coeffs, torque_residuals, torque_rank, torque_s = lstsq(rpmA, torque)

# print("Thrust curve:")
# print(np.poly1d(np.flip(thrust_coeffs)))
# print("Torque curve:")
# print(np.poly1d(np.flip(torque_coeffs)))

# print("Thrust residual:", thrust_residuals)
# print("Torque residual:", torque_residuals)

x = np.linspace(rpm[0], rpm[-1], 1000)

plt.figure()
plt.plot(rpm, thrust, 'bo', label='Data Points')
plt.plot(x, thrust_coeffs[3]*x**3+thrust_coeffs[2]*x**2+thrust_coeffs[1]*x+thrust_coeffs[0], 'r-', label=("Fitted Line"))
plt.legend()
plt.grid(True)
plt.title("Thrust v RPM")
plt.xlabel("RPM")
plt.ylabel("Thrust (kgf)")
save_fig2(parent_directory, "thrust_curve")

plt.figure()
plt.plot(rpm, torque, 'bo', label='Data Points')
plt.plot(x, torque_coeffs[3]*x**3+torque_coeffs[2]*x**2+torque_coeffs[1]*x+torque_coeffs[0], 'r-', label=("Fitted Line"))
plt.legend()
plt.grid(True)
plt.title("Torque v RPM")
plt.xlabel("RPM")
plt.ylabel("Torque (N m)")
save_fig2(parent_directory, "torque_curve")

os.path.join(parent_directory, "README.txt")
np.set_printoptions(precision=12)

with open(os.path.join(parent_directory, "README.txt"), 'w') as f:
    f.write("Thrust curve:\n\n")
    f.write(str(np.poly1d(np.flip(thrust_coeffs))))
    f.write("\n\n")
    f.write("Torque curve:\n\n")
    f.write(str(np.poly1d(np.flip(torque_coeffs))))
    f.write("\n\n\n")

    f.write("Thrust coefficients:\n")
    f.write(str(np.flip(thrust_coeffs)))
    f.write("\n")
    f.write("Torque coefficients:\n")
    f.write(str(np.flip(torque_coeffs)))
    f.write("\n\n\n")

    f.write("Thrust residual:\n")
    f.write(str(thrust_residuals))
    f.write("\n")
    f.write("Torque residual:\n")
    f.write(str(torque_residuals))
    f.write("\n\n\n")


plt.show()