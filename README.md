# JetCat Comms Project

Created Repo on 11/11/2022

## Setup Help

    sudo apt-get install python-dev libxml2-dev libxslt-dev

Ubuntu also required dev tools for c to be installed for CFFI to work. Run

    sudo apt-get update && sudo apt-get install build-essential

To save Matplotlib animations you must install ffmpeg in ubuntu terminal

    sudo apt install ffmpeg

Other modules included in `requirements.txt`

    pip install -r requirements.txt

## jetcat_comms.py

This is the main python script to use when running the engine. This script will send engine RPM commands, timestamp and save PRO-Interface data to `.bin` and `.csv` files, and create live animations of a few important measurements that should be watched during testing. You should not have to use `throttle_cmd_2.py` or `make_csvs.sh` anymore with this script.

Setup a throttle command text file that follows the example below. You can insert expressions for time and RPM or percent for the throttle. The engine will always shut off at the last time stamp no matter what the RPM command is at that time. You must point to the path of this throttle curve file when calling the script at the terminal.

    Time, Throttle_RPM
    90, 40000
    90+5, 90%
    2*60, 50000
    4*60, 0

The script will save PRO-Interface data to a `.bin` and a `.csv` file. The `.bin` will be the raw, unprocessed data from the interface, while the `.csv` will be processed data that does not include any corrupted data packets. The live animation shown while running the test is created from the processed data that is eventually put into the `.csv`.

## throttle_cmd_2.py

This program is for sending throttle commands to the PRO-Interface while also logging all the data from the serial port. The commands are received through a .txt file. You can enter times as an expression, like 60+40, and throttle commands can be entered as rpm or % of maximum rpm. An example curve text file:

    Time, Throttle_RPM
    0,35000
    90, 40000
    90+5, 80000
    90+10, 40000
    90+15, 81%
    90+20, 34000
    90+80, 0

Put at least a 90 after startup so that the engine has time to idle

The program will create a binary file to save PRO-Interface data, and a text file to save the throttle curve and output commands. If a samsung T7 is plugged into your computer it will back up the files to your external ssd. Believe this script should be ran as sudo, but it works without it sometimes. Just run as sudo.


## make_csvs.sh

Bash script to take all of the PRO-Interface, E-TC, and USB-6210 data in a folder and convert to `.csv` and `.pickle` files. It will save the .csv's in the same folder they were found in, and it searches all the subdirectories inside a folder. Don't use with any bin files that are empty. Double check it works. An example run is:

    bash ./src/make_csvs.sh ~/Documents/2023-02-22_JetCat_Test/
    Processing file: ./interface/2023-02-22_T121427_data.bin
    Processing file: ./interface/2023-02-22_T132715_data.bin
    Processing file: ./interface/2023-02-22_T114204_data.bin
    Processing file: ./interface/2023-02-22_T131842_data.bin
    Processing file: ./interface/2023-02-22_T132509_data.bin
    Processing file: ./signal_express/02222023_110927_AM/Voltage.tdms
    Processing file: ./signal_express/02222023_105658_AM/Voltage.tdms
    Processing file: ./signal_express/02222023_110441_AM/Voltage.tdms
    Processing file: ./signal_express/02222023_012732_PM/Voltage.tdms
    Processing file: ./signal_express/02222023_110020_AM/Voltage.tdms
    Processing file: ./signal_express/02222023_110704_AM/Voltage.tdms
    Processing file: ./signal_express/02222023_114909_AM/Voltage.tdms
    Processing file: ./signal_express/02222023_121544_PM/Voltage.tdms
    Processing file: ./signal_express/02222023_011948_PM/Voltage.tdms


## make_plots.sh

Bash script to take all the PRO-Interface, E-TC, and USB-6210 csv's in a folder and plot. This can only be ran after `make_csvs.sh` is ran. The .png files are saved in the same location as the data. Run the script with the full path to the directory, `bash ./src/make_plots.sh ~/Documents/GitHub/JetCat_Comms/data/2023-02-22_JetCat_Test/`


## make_calibration_curve.sh

Bash script to generate calibration curve from cal data. Point to a folder that has the calibration data stored inside. Any number of calibration points can be used as long as the data is saved in the correct format. Example run:

    bash ./src/make_calibration_curve.sh ~/Documents/GitHub/JetCat_Comms/data/2023-02-22_Calibration_Data/
    Value of weights hung from load cell in order: [ 40.001 -40.001  -0.002  75.     39.999]
    Mean Voltage read from load cell for those weights: [ 3.552042 -3.872265 -0.70692   4.662902  4.345449]
    Line of best fit: y=11.374741681747047x+4.842564866216753
    Mean Squared Error (MSE) of best fit: 107.01666638376491
    Saving plots to  /home/colton/Documents/GitHub/JetCat_Comms/data/2023-02-22_Calibration_Data/images/Calibration_Curve.png
    Runtime: .961804197 seconds

 The folder you are pointing to will look like this:

    ./data/2023-02-22_Calibration_Data/
    ├── 1_40aF.csv
    ├── 2_40aR.csv
    ├── 3_40aR_40bF.csv
    ├── 4_40bF_35aF.csv
    ├── 5_40bF.csv
    └── images
        └── Calibration_Curve.png

## calibrate_load_cell.py

Run this program to recieve prompts on what weights to hang from the load cell for calibration, tell the computer when the weights are hung, and automatically sample the load cell for a certain period of time, saving the files together in the correct format so that calibration_curve.py can generate the curves for you right after calibration.

ONLY RUNS ON WINDOWS!

You have to download NIDAQmxBASE, NIDAQmx, and run `pip install nidaqmx` for this to work.

- Install: [NIDAQmx](https://www.ni.com/en-us/support/downloads/drivers/download.ni-daq-mx.html#477807)
- Install: [NIDAQmx Base](https://www.ni.com/en-us/support/downloads/drivers/download.ni-daqmx-base.html#326059)
- Python API: `pip install nidaqmx`

Will save the samples as csv files in this format:

    ./data/YYY-MM-DD_THHMMSS_Calibration_Data
    ├── 1_40aF.csv
    ├── 2_40aR.csv
    ├── 3_40aR_40bF.csv
    ├── 4_40bF_35aF.csv
    ├── 5_40bF.csv

## Virtual serial port for testing

To test the throttle command program, you should open a virtual serial port to make sure the proper commands are being sent. To create a virtual serial port, open a terminal and enter

    socat -d -d pty,raw,echo=0 pty,raw,echo=0

This will return something like:

    2023/01/06 16:09:03 socat[40084] N PTY is /dev/pts/4
    2023/01/06 16:09:03 socat[40084] N PTY is /dev/pts/5
    2023/01/06 16:09:03 socat[40084] N starting data transfer loop with FDs [5,5] and [7,7]


Then open a new terminal and type

    cat < /dev/pts/4

Python can then connect to /dev/pts/5 and any commands sent over this port will be received on your terminal. You can also not run the cat command above, run the python program so that the serial write data is saved into the buffer, and then use the command:

    cat < /dev/pts/4 | hexdump -C

To see the serial command data in binary.

These instructions come from [stack overflow](https://stackoverflow.com/questions/52187/virtual-serial-port-for-linux)


## throttle_cmd_1.py *DEPRECATED*

This program is for sending throttle commands to the PRO-Interface while also logging all the data from the serial port. The commands are received through a .txt file that follows this format:

    Time, Throttle_RPM
    0,0
    45,34000
    100,100000
    120,34000
    180,0


### throttle_cmd_1.py Run Tips

You need at least ~40-45 seconds between your START command and the first set engine RPM command. I tested the program with the simulate engine mode and it works. If you change the RPM on the GSU, the next RPM command just overwrites your change. If you shut the engine down on the GSU, it will remain off while new RPM commands are being sent.

The engine should be primed with the GSU before this program is ran so that it has fuel and quickly allows RPM commands.


### throttle_cmd_1.py General Notes

Byte stuffing is totally done. Timing used to be bad because I had `ser.read(100)` set, with a timeout of 2 seconds, so the program would just halt at the read statement and wait for 100 bytes for 2 seconds. Fixed this with `ser.read(ser.in_waiting)`.

## CFFI *DEPRECATED*

To run cffi, you need to run `main.py` inside the main `JetCat_Comms` directory for some reason. This will compile the library you need to include inside of any program that requires crc16 calcs.

This is a bit of a mess right now. Run `main.py` to create the python .so library, then put that library in the same folder as the source code you're going to run, `import _crc.lib`

The cffi library is currently only working on Linux. Not sure how to get it to work on windows, but it's something to do with the compiler.

TODO:

Send Dr. W two scripts:

- One that sends commands to the PRO-interface from the throttle curve files. Does not record data from the PRO-Interface.

- Another that turns PRO-Interface .bin files into .csv files 