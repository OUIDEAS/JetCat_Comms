"""
ztest_thread2.py

Created by Colton Wright on 3/7/2023

Attempt to read PRO-Interface serial port, save data to .bin & .csv, with a live plot
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import threading
from queue import Queue # Allow easy, safe exchange of data between threads

import modules.m3 as m3



# Data to simulate for testing!
bin_file_path = r"/home/colton/Documents/GitHub/OUIDEAS/JetCat_Comms/data/2023-02-22_T121427_data.bin"
data_filename, log_filename, csv_filename = m3.make_filenames()
queue1 = Queue(maxsize=0) # queue size is infinite

# Create threads
thread1_args = (queue1, data_filename, log_filename, True,)
thread1 = threading.Thread(target=m3.read_port, args=thread1_args)
test_thread = threading.Thread(target=m3.write_file_to_port, args=(bin_file_path,))
csv_thread = threading.Thread(target=m3.csv_thread_func, args=(queue1, csv_filename,))



thread1.start()
time.sleep(.1)
test_thread.start() # For simulating a PRO-Interface on the serial port
csv_thread.start()

# CSV is being written to, let's plot...
time.sleep(.5)
fig = plt.figure()
ax = fig.add_subplot(2,2,1)
ax2 = fig.add_subplot(2,2,2)
ax3 = fig.add_subplot(2,2,3)
ax4 = fig.add_subplot(2,2,4)

ax.grid(True)
ani = animation.FuncAnimation(fig, m3.update, fargs=(csv_filename, ax,ax2,ax3,ax4), interval = 100, blit=False, save_count=10)
fig.tight_layout()
plt.show()