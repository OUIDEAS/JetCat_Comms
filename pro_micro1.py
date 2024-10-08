import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
import time
import datetime
import os
from queue import Queue # Allow easy, safe exchange of data between threads
import threading

PRO_MICRO_COM_PORT = 'COM7'
START_TIME = time.time()
TEST_DURATION = 10
END_TIME = START_TIME + TEST_DURATION
START_DATETIME = datetime.datetime.now()

def main():




    data_file_path = make_pm1_filename(START_DATETIME)
    # with serial.Serial(PRO_MICRO_COM_PORT, baudrate=115200, timeout=.1) as ser, \
    #     open(data_file_path, 'ab') as dat_file:
    #     print("Serial port opened")
    #     while (END_TIME > time.time()):
    #         data = ser.read(100)
    #         dat_file.write(data)
    #         print(data)

    queue1 = Queue(maxsize=0) # queue size is infinite
    PMT_vars = (PRO_MICRO_COM_PORT, queue1, data_file_path, START_TIME, TEST_DURATION)
    thread1 = threading.Thread(target=pro_micro_thread_func, args=PMT_vars)
    thread1.start()

    while time.time() < END_TIME:
        print(time.time()-START_TIME)
        time.sleep(1)

    # # CSV is being written to, let's plot...
    # time.sleep(.5)
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)
    # ax2 = fig.add_subplot(2,2,2)
    # ax3 = fig.add_subplot(2,2,3)
    # ax4 = fig.add_subplot(2,2,4)

    # x = []
    # y = []
    # z = []
    # ani_args = (x,y,z, queue1, ax,ax2,ax3, START_TIME, TEST_DURATION)
    # ani = animation.FuncAnimation(fig, update_anim, fargs=ani_args, interval = 100, blit=False, save_count=10)
    # fig.tight_layout()
    # plt.show()




def make_pm1_filename(file_date_time):
    # Create directory & filename for the log file
    now = file_date_time.strftime("%Y-%m-%d")
    now_more = file_date_time.strftime("%Y-%m-%dT%H%M%S")
    FILE_PATH = os.path.join(".", "data", now, now_more )
    os.makedirs(FILE_PATH, exist_ok=True)
    acc_data = os.path.join(FILE_PATH, (now_more + "_data.txt" ))
    return acc_data

def pro_micro_thread_func(ser_port, queue1, data_file_path,  START_TIME, TEST_DURATION):

    with serial.Serial(ser_port, baudrate=115200, timeout=0.1) as ser, \
    open(data_file_path, 'ab') as data_file:
        while time.time() < START_TIME + TEST_DURATION:
            data = ser.read(100)
            data_str = data.decode('utf-8')
            stamp = time.time()
            data_with_timestamp = data_str.replace('\r\n', f'\r\n{stamp} ')
            byte_data_with_timestamp = data_with_timestamp.encode('utf-8')
            data_file.write(byte_data_with_timestamp)
            queue1.put(data_with_timestamp)

            # print(data)

def update_anim(frame, x,y,z, queue1, ax, ax2, ax3, START_TIME, TEST_DURATION):
    while not queue1.empty():
        new_data = queue1.get()
        # print(new_data)
        time.sleep(.2)
        new_data_str = new_data.decode('utf-8')
        # print(new_data_str)
        new_data_list = parse_string_to_floats(new_data_str)
        new_data_list = np.array(new_data_list)
        # print(new_data_list)
        x_values = new_data_list[0][:]
        y_values = new_data_list[:][1]
        z_values = new_data_list[:][2]

        x.append(x_values)
        y.append(y_values)
        z.append(z_values)
        print("Numpy:")
        print(new_data_list)
        print("X")
        print(x_values)
        # print(x)
        
        ax.clear()
        ax.plot(range(len(x)),x)
        ax.grid(True)
        ax.set_xlabel("points")
        ax.set_ylabel("X_val")
        ax.set_ylim([0, 1000])

# Function to parse the string and convert to a list of floats, filtering out incomplete rows
def parse_string_to_floats(input_str):
    lines = input_str.strip().split('\n')
    float_list = []
    for line in lines:
        values = line.split()
        if len(values) == 3:
            float_list.append([float(value) for value in values])
    return float_list

if __name__ == '__main__':
    main()


# Idea

"""
import datetime

# Assuming you have the series of bytes stored in a variable called 'byte_data'
# For demonstration purposes, I'll create an example bytes object here
byte_data = b'87.60 -38.55 995.03\r87.60 -38.55 995.15\r87.60 -38.55 995.03\r87.72 -38.55 995.03\r87.84 -3'

# Convert bytes to a string
data_str = byte_data.decode('utf-8')

# Get the current timestamp
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Add the timestamp after each \r
data_with_timestamp = data_str.replace('\r', f'\r{timestamp} ')

# Convert the string back to bytes
byte_data_with_timestamp = data_with_timestamp.encode('utf-8')

# Now, 'byte_data_with_timestamp' contains the original data with timestamps after each \r
print(byte_data_with_timestamp)
"""