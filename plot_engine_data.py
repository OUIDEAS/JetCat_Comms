"""

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



file_path = sys.argv[1] # Full path to file
frame = pd.read_csv(file_path)
base_path, extension = os.path.splitext(file_path)
# print(base_path)
parent_directory = os.path.dirname(file_path)

for col in frame.columns:
    frame.plot(y=col, use_index=True, style='o')
    print(col)
    save_fig2(parent_directory, col)

# Check if the given CRC == calculated CRC
is_crc_equal = np.zeros((len(frame),1))
for i in range(len(frame)):
    if frame.iloc[i]["CRC16_Given"] == frame.iloc[i]["CRC16_Calculated"]:
        is_crc_equal[i] = True
    else:
        is_crc_equal[i] = False

plt.figure()
plt.plot(frame.index, is_crc_equal, label='CRC Equal')
plt.legend()
save_fig2(parent_directory, 'CRC Equal')

plt.show()