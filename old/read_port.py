import serial
import datetime
import os

def make_txt_file():
    now = datetime.datetime.today().strftime("%Y-%m-%d")
    now_more = datetime.datetime.today().strftime("%Y-%m-%d_%H%M%S")
    FILE_PATH = os.path.join(".", "data", now )
    os.makedirs(FILE_PATH, exist_ok=True)
    filename = os.path.join(FILE_PATH, (now_more + "_read_port.bin"))
    return filename
    
print("Reading serial port...")
time_to_read = .1 # Time to read the port [min]
print("Test will take ", time_to_read, " minutes...")
# Create file and timing
filename = make_txt_file()
time_to_end = datetime.datetime.today().timestamp() + 60*time_to_read

with serial.Serial('COM3', baudrate=115200, timeout=2) as ser, \
    open(filename, 'wb') as file:

    while datetime.datetime.today().timestamp() < time_to_end:

        a_data_packet = ser.read(ser.inWaiting()) # Read everything in the buffer
        # Do something with this data packet
        file.write(a_data_packet)
