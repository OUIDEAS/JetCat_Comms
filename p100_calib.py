"""
p100_calib1.py

Created by Colton Wright on 4/10/2023

Point to the YYYY-MM-DD_Calibration_Data directory and get the calibration curve
"""

import numpy as np
import pandas as pd
import sys
import os
import matplotlib.pyplot as plt

def main():
        
    folder_path = sys.argv[1] # Full path to file
    files = []
    frames = []
    weights_used = []
    val_weights = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            files.append(file_path)

    # Sort files according to the first number of their name
    sorted_files = sorted(files, key=get_integer)

    for i, file in zip(range(len(sorted_files)), sorted_files):
        frames.append(pd.read_csv(file, skiprows=3))
        print(frames[i])
        name = file.split('/')[-1].split('.')[0]
        w = name.split('_')[1:]
        w = '_'.join(w)
        w = w.replace('_', '+')
        weights_used.append(w)


    
    x = np.array([frame["V"].mean() for frame in frames])
    y = np.array([0, -2.5, 2.5, -7.5, 7.5, -10, 10, -15, -17.5, 17.5, -25, 25])
    print(x)
    print(y)

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
    ax.plot(x, y, 'bo', label="Data Points", markersize=4)
    for i, txt in enumerate(labels):
        ax.annotate(txt, (x[i], y[i]))
    plt.xlabel("Voltage [V]")
    plt.ylabel("Weight [lb]")
    plt.title("Calibration Curve")
    plt.grid(True)
    plt.plot(x, slope*x+constant, 'r-', label="Fitted Line")
    plt.gca().text(.99, .07,  f"y={slope:.3f}x+{constant:.3f}",
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax.transAxes, fontsize=15)
    plt.gca().text(.99, 0.01,  f"MSE: {MSE:.3f}",
    verticalalignment='bottom', horizontalalignment='right',
    transform=ax.transAxes, fontsize=15)
    plt.legend()
    save_fig2(folder_path, "Calibration_Curve")
    # plt.show()

















def get_integer(path):
    # split the path by '\\' and get the last element
    filename = path.split('\\')[-1]
    # split the filename by 'lb' and get the first element
    lb_value = filename.split('lb')[0]
    # convert the lb value to float and then to int
    return int(float(lb_value))

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