"""
Make some plots for p100 data to go into a paper

5/15/2023

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

thrust_4 = pd.read_csv("thrust_run4.csv", skiprows=3)
egt_4 = pd.read_csv("exhaust_run4.csv", skiprows=3)
print(thrust_4)
print(egt_4)

plt.figure()
plt.plot(thrust_4['Unit'], thrust_4['V'])
plt.show()