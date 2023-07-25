import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


data_file = input("Put file path here: ")
frame1 = pd.read_csv(data_file, names=["Time", "x", "y", "z"], skiprows=1, sep=' ', index_col=False)
print(frame1)

plt.figure()
plt.plot(frame1['Time'])
plt.title("Time")

plt.figure()
plt.plot(frame1['x'])
plt.title("X axis")

plt.figure()
plt.plot(frame1['y'])
plt.title("Y axis")

plt.figure()
plt.plot(frame1['z'])
plt.title("Z axis")

plt.show()