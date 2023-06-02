"""
Make some plots for p100 data to go into a paper

5/15/2023

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

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

csv_path = sys.argv[1]
base_path, extension = os.path.splitext(csv_path)
parent_directory = os.path.dirname(base_path)
thrust_4 = pd.read_csv(csv_path, skiprows=0)
print(thrust_4)
thrust_4['Thrust [N]'] = -(10.65333140211067*thrust_4['Voltage']+1.9284045823237697)
print(thrust_4)




plt.figure()
plt.plot(thrust_4['Time [s]'], thrust_4['Voltage'])
plt.xlabel("Time [s]")
plt.ylabel("Voltage [V]")
save_fig2(parent_directory, "Voltage_plot")

plt.figure()
plt.plot(thrust_4['Time [s]'], thrust_4['Thrust [N]'], linewidth=.8)
plt.xlabel("Time [s]")
plt.ylabel("Thrust [N]")
save_fig2(parent_directory, "Thrust_plot")

plt.show()