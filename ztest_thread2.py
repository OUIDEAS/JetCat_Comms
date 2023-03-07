"""
ztest_thread2.py

Created by Colton Wright on 3/7/2023

Attempt to read PRO-Interface serial port, save data to .bin & .csv, with a live plot
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import serial
import cffi
import time
import os
import multiprocessing
import threading

from queue import Queue # Allow easy, safe exchange of data between threads


