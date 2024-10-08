"""
calibration_curve.py

Created by Colton Wright on 3/1/2023

Point to the YYYY-MM-DD_Calibration_Data directory and get the calibration curve
"""

import numpy as np
import pandas as pd
import sys
import os
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

folder_path = sys.argv[1] # Full path to file
files = []
frames = []
weights_used = []
val_weights = []

# Change this when you actually measure the weights
values = {"40aF": 40.001,
          "40bF": 39.999,
          "35aF": 35.001,
          "40aR": -40.001,
          "40bR": -39.999,
          "35aR": -35.001
          }

for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)
    if os.path.isfile(file_path):
        files.append(file_path)

# Sort files according to the first number of their name
sorted_files = sorted(files, key=lambda x: int(x.split('\\')[-1].split('_')[0]))
print(sorted_files)
for file in sorted_files:
    frames.append(pd.read_csv(file))
    name = file.split('/')[-1].split('.')[0]
    w = name.split('_')[1:]
    w = '_'.join(w)
    w = w.replace('_', '+')
    weights_used.append(w)


for expr in weights_used:
    for var, val in values.items():
        expr = expr.replace(var, str(val))
        # print(expr)
    value = eval(expr)
    val_weights.append(value)
# print(val_weights)



x = np.array([frame["Voltage [V]"].mean() for frame in frames])
y = np.array(val_weights)

# We have the data points now. Just get linear least squares of the data:

A = np.vstack([x, np.ones(len(x))]).T
slope, constant = np.linalg.lstsq(A, y, rcond=None)[0]
y_predict = slope*x+constant

MSE = np.square(np.subtract(y, y_predict)).mean() # Take mean of square of difference
# Print to terminal. Print so that we can figure out if the data is okay
np.set_printoptions(suppress=True)
print("Value of weights hung from load cell in order:", np.round(y, decimals=6))
print("Mean Voltage read from load cell for those weights:", np.round(x, decimals=6))

print("Line of best fit: y="+str(slope)+"x+"+str(constant))
print("Mean Squared Error (MSE) of best fit:", MSE)


labels = range(1, len(val_weights)+1)
fig, ax = plt.subplots()
ax.plot(x, y, 'bo', label="Data Points")
for i, txt in enumerate(labels):
    ax.annotate(txt, (x[i], y[i]))
plt.xlabel("Voltage [V]")
plt.ylabel("Weight [lb]")
plt.title("Calibration Curve")
plt.grid(True)
plt.plot(x, slope*x+constant, 'r-', label="Fitted Line")
plt.legend()
save_fig2(folder_path, "Calibration_Curve")
# plt.show()



