import numpy as np
import pandas as pd
import sys
import os
import scipy
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt

print("Input:", sys.argv[1])

folder_path = str(sys.argv[1]) # Full path to file

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
print(extrema_rows)

f1.plot(x="Time (s)", y="Thrust (kgf)")
f1.plot(x="Time (s)", y="dThrust")
f1.plot(x ="Time (s)", y="dThrust peaks")
f1.plot(x ="Time (s)", y="dThrust valleys")
f1.plot(x ="Time (s)", y="dThrust spikes")



plt.show()