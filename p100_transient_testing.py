import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import sys
import os

path = sys.argv[1]

csv_files = glob.glob(os.path.join(path, "*.csv"))
list_of_frames = []

for i, file_path in enumerate(csv_files):
    print(file_path)
    list_of_frames.append(pd.read_csv(file_path, skiprows=4))
    plt.figure()
    plt.plot(list_of_frames[i].iloc[:,0], list_of_frames[i].iloc[:,1])
    plt.title(os.path.basename(file_path))

plt.show()