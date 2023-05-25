"""
Make some plots for p100 data to go into a paper

5/15/2023

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

thrust_4 = pd.read_csv(r"C:\Users\Colton W\OneDrive - Ohio University\Research\JetCat\data\P100\data_3-25-22\data_3-25-22\Thrust_run3.csv", skiprows=3)
egt_4 = pd.read_csv(r"C:\Users\Colton W\OneDrive - Ohio University\Research\JetCat\data\P100\data_3-25-22\data_3-25-22\exhaust_run3.csv", skiprows=3)
body_4 = pd.read_csv(r"C:\Users\Colton W\OneDrive - Ohio University\Research\JetCat\data\P100\data_3-25-22\data_3-25-22\Body_run3.csv", skiprows=3)

thrust_4['Thrust [N]'] = -(10.65333140211067*thrust_4['V']+1.9284045823237697)
print(thrust_4)
print(egt_4)

sigma = 2
print(sigma)

print(thrust_4.iloc[(thrust_4['Unit']-118).abs().argsort()[0]])
thrust_4_timeshift = thrust_4[118000:]
print(thrust_4_timeshift)
thrust_4_timeshift['Unit'] = thrust_4_timeshift['Unit'] - thrust_4_timeshift['Unit'].iloc[0]

# Shift the thrust data so it lines on top of EGT for plotting

t_time2 = (thrust_4['Unit'].min(), thrust_4['Unit'].max())
shift = 10
new_time = np.linspace(t_time2[0]+shift, t_time2[1]+shift, len(egt_4['Unit']))


print(len(new_time))
print(len(egt_4['Unit']))

plt.figure()
plt.plot(thrust_4['Unit'], thrust_4['V'])
plt.xlabel("Time [s]")
plt.ylabel("Voltage [V]")

plt.figure()
plt.plot(thrust_4['Unit'], thrust_4['Thrust [N]'], linewidth=.8)
plt.xlabel("Time [s]")
plt.ylabel("Thrust [N]")

plt.figure()
plt.plot(thrust_4_timeshift['Unit'], thrust_4_timeshift['Thrust [N]'], linewidth=.8)
plt.xlabel("Time [s]")
plt.ylabel("Thrust [N]")

plt.figure()
plt.plot(egt_4['Unit'], egt_4['°C'])
plt.xlabel("Time [s]")
plt.ylabel("EGT [°C]")

plt.figure()
plt.plot(body_4['Unit'], body_4['°C'])
plt.xlabel("Time [s]")
plt.ylabel("Body Temp [°C]")

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ln1 = ax1.plot(thrust_4['Unit'], thrust_4['Thrust [N]'], color='tab:blue', linestyle='-', label='Thrust')
ln2 = ax2.plot(new_time, egt_4['°C'], color='tab:green', linestyle='--', label='EGT')



ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Thrust [N]', color='tab:blue')
ax2.set_ylabel('EGT [°C]', color='tab:green')
lns = ln1+ln2
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs)

plt.show()