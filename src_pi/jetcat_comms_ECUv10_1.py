# This script will run on a RPi 4 model B. The pi will send throttle commands
# to the ECU over a PWM pin.

import RPi.GPIO as GPIO
import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import serial
import threading
from queue import Queue # Allow easy, safe exchange of data between threads
import os
import sys
import time
import datetime
import csv
import struct
import crc
import pro_micro1 as pm1
import jetcat_comms as jcc


def main():
    GPIO.setmode(GPIO.BOARD)

    thr_ch_pin = 12

    GPIO.setup(thr_ch_pin, GPIO.OUT)
    GPIO.setwarnings(False)
    thr_ch_pwm = GPIO.PWM(thr_ch_pin, 1000)
    thr_ch_pwm.start(0)

    cmd_file_path = sys.argv[1]

    cmd_array = jcc.read_throttle_rpm_cmds(cmd_file_path)
    TEST_DURATION = cmd_array[-1, 0]
    start_input = input("Are you ready to start the engine? [y/n]: ")
    if start_input.lower() == "y":
        jcc.start_countdown()
        START_TIME = time.time()
        ECUv10_start_engine()
        stop_flag = True

        while time.time() < START_TIME + TEST_DURATION:
            # If enough time has elapsed, send a throttle command
            now = time.time()
            if now > (START_TIME + cmd_array[cmd_counter, 0]) and stop_flag:

                # send_throttle_rpm(ser, log_file, cmd_array[cmd_counter, 1], cmd_counter, crc_calculator)
                rpm_command = cmd_array[cmd_counter, 1]
                duty = RPM_to_PWM_map(rpm_command)
                thr_ch_pwm.ChangeDutyCycle(duty)
                # log_file.write(("Sent cmd at:" + str(now)) + "\n")
                # log_file.write(("Time:" + str(cmd_array[cmd_counter, 0])) + "\n")
                # log_file.write(("Throttle_RPM:" + str(cmd_array[cmd_counter, 1])) + "\n")
                # log_file.write("\n")
                cmd_counter = cmd_counter + 1






            if now > START_TIME + TEST_DURATION and stop_flag:
                ECUv10_stop_engine(ser)
                stop_flag = False
                cmd_counter = 0
            if now > START_TIME + TEST_DURATION+15:
                break

def ECUv10_start_engine():
    # You're going to have to shutoff throttle, go to max, then back down...
    pass

def ECUv10_stop_engine():

    pass

def RPM_to_PWM_map(rpm_value):
    max_duty = 75
    min_duty = 15
    max_rpm = 150000
    min_rpm = 50000
    duty_cycle = (max_duty-min_duty)/(max_rpm-min_rpm)*rpm_value-15
    return duty_cycle

# while True:
#     for duty in range(0,101,1):
#         pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 0-100
#         time.sleep(0.01)
#     time.sleep(0.5)
#     for duty in range(100,-1,-1):
#         pi_pwm.ChangeDutyCycle(duty)
#         time.sleep(0.01)
#     time.sleep(0.5)

if __name__ == '__main__':
    main()