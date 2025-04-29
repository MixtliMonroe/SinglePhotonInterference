try:
        import QuTAG_MC
except:
        print("Time Tagger wrapper QuTAG.py is not in the search path / same folder.")

import numpy as np
import time
import matplotlib.pyplot as plt
import scipy as sci
import keyboard

def printDeviceSettings(qutag):
        # Get the calibration state of the device
        calibState = qutag.getCalibrationState()
        print("getCalibrationState: ", calibState)

        # Get the timebase (the resolution) from the quTAG. It is used as time unit by many other functions.
        timebase = qutag.getTimebase()
        print("Device timebase:", timebase, "s")

        time.sleep(1)
        data,updates = qutag.getCoincCounters()
        print("Updates since last call: ", updates, "| Data: ", data)

        # Read back device parameters: coincidence window in bins (bin width is timebase) and exposuretime in ms
        na, coincWin, expTime = qutag.getDeviceParams()
        print("Coincidence window", coincWin, "bins, exposure time",expTime, "ms")

        enabledchannels = qutag.getChannelsEnabled()
        print("Enabled channels: ", enabledchannels)

        # Get status of external clock"
        clockState = qutag.getClockState()
        print("Clock State: locked ", clockState[0], ", uplink ", clockState[1])

def livePlot(qutag, channels):
        # Read back device parameters: coincidence window in bins (bin width corresponds to timebase) and exposuretime in ms
        # We use the exposure time for the y-axis in the plot 
        na, coincWin, expTime = qutag.getDeviceParams()
        print("Coincidence window",coincWin, "bins, exposure time",expTime, "ms")

        
        # Init plotting with matplotlib 
        fig = plt.figure()
        fig.set_size_inches(10,7)
        subplt = fig.add_subplot(1,1,1)

        # Arrays for saving data for plotting
        x = []
        y = [[] for _ in channels]
        

        # Increment in loop for plotting when new data comes from quTAG
        newdata = 0

        while True:
                if keyboard.is_pressed('esc'):
                        print("Quitting...")
                        break
                time.sleep(0.1)
                # Get the data from quTAG.
                data,updates = qutag.getCoincCounters()
                print("Data: ", data)
                # updates	Output: Number of data updates by the device since the last call. Pointer may be NULL.
                # data	        Output: Counter Values. The array must have at least 31 elements.
                #                       The Counters come in the following channel order with single counts and coincidences:
                #                       0(5), 1, 2, 3, 4, 1/2, 1/3, 2/3, 1/4, 2/4, 3/4, 1/5, 2/5, 3/5, 4/5, 1/2/3, 1/2/4, 1/3/4, 2/3/4, 1/2/5, 1/3/5, 2/3/5, 1/4/5, 2/4/5, 3/4/5, 1/2/3/4, 1/2/3/5, 1/2/4/5, 1/3/4/5, 2/3/4/5, 1/2/3/4/5 
                ### see 'tdcbase.h' file reference for more info: function TDC_getCoincCounters(Int32 *data, Int32 *updates)

                
                if (updates == 0):
                        # No new data...
                        print("waiting for new data...")
                else:
                        # Push the countrates of channel 1 & 2 in arrays for plotting...
                        newdata += 1
                        x.append(newdata*expTime/500)
                        for i, channel in enumerate(channels):
                                y[i].append(data[channel])
                        # Plotting...
                        plt.cla()
                        subplt.set_title('quTAG count rates')
                        plt.xlabel('Time [s]')
                        plt.ylabel('Countrate [1/' + str(expTime/1000) +'s]')
                        
                        # Let's remove old data from the plotting array, so only e.g. the last 30 datapoints are plotted
                        if (len(x) > 30):
                                x.pop(0)
                                for i in range(len(channels)):
                                        y[i].pop(0)

                        # Plot the data
                        for i, channel in enumerate(channels):
                                plt.plot(x, y[i], '-', label="Ch " + str(channel))
                        plt.legend()
                        plt.pause(0.01)