try:
        import QuTAG_MC
except:
        print("Time Tagger wrapper QuTAG.py is not in the search path / same folder.")

import numpy as np
import time
import matplotlib.pyplot as plt
import scipy as sci
import keyboard

def nstotimesteps(qutag, nseconds):
        # Get the timebase of the quTAG.
        timebase = qutag.getTimebase()
        timesteps = int(nseconds / (1e9 * timebase)) # convert nanoseconds to timesteps
        return timesteps

def printDeviceSettings(qutag):
        '''
        Print some device settings to the console.
        '''
        # Get the calibration state of the device
        calibState = qutag.getCalibrationState()
        print("getCalibrationState: ", calibState)

        # Get the timebase (the resolution) from the quTAG. It is used as time unit by many other functions.
        timebase = qutag.getTimebase()
        print("Device timebase:", timebase, "s")

        # Get the buffer size for the timestamps
        print("buffer size: ", qutag.getBufferSize())

        # Read back device parameters: coincidence window in bins (bin width is timebase) and exposuretime in ms
        na, coincWin, expTime = qutag.getDeviceParams()
        print("Coincidence window", coincWin, "bins, exposure time",expTime, "ms")

        enabledchannels = qutag.getChannelsEnabled()
        print("Enabled channels: ", enabledchannels)

        # Get status of external clock"
        clockState = qutag.getClockState()
        print("Clock State: locked ", clockState[0], ", uplink ", clockState[1])

def livePlot(qutag, channels, buffer=30, coincWindow=1000):
        '''
        Show a live plot of the count rates of the channels in the list 'channels'.
        '''
        qutag.setExposureTime(100)
        qutag.setCoincidenceWindow(nstotimesteps(coincWindow))
        
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
                data, updates = qutag.getCoincCounters()
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
                        x.append(newdata*.1)
                        for i, channel in enumerate(channels):
                                y[i].append(10*np.array(data[channel]))
                        # Plotting...
                        plt.cla()
                        subplt.set_title('quTAG count rates')
                        plt.xlabel('Time s')
                        plt.ylabel('Countrate Hz')
                        
                        # Let's remove old data from the plotting array, so only e.g. the last 30 datapoints are plotted
                        if (len(x) > buffer):
                                x.pop(0)
                                for i in range(len(channels)):
                                        y[i].pop(0)

                        # Plot the data
                        for i, channel in enumerate(channels):
                                plt.plot(x, y[i], '-', label="Ch " + str(channel))
                        plt.legend()
                        plt.pause(0.001)

def liveG2Plot(qutag, channel1, channel2, histogramWidth = 1, binCount=256):
        # Read back device parameters: coincidence window in bins (bin width corresponds to timebase) and exposuretime in us
        print("histogram width: ", histogramWidth, "us, bin count: ", binCount)

        binWidth = histogramWidth/(1e6*binCount*qutag.getTimebase())

        # Init the HBT function
        qutag.enableHBT(True)
        qutag.setHBTParams(binWidth=binWidth, binCount=binCount)
        qutag.setHBTInput(channel1,channel2)
        hbtfunc = qutag.createHBTFunction()

        # Init plotting with matplotlib 
        fig = plt.figure()
        fig.set_size_inches(10,7)
        subplt = fig.add_subplot(1,1,1)

        # Array for data for plotting
        x = -np.arange(1, 2*binCount)

        while True:
                if keyboard.is_pressed('esc'):
                        print("Quitting...")
                        break
                time.sleep(0.1)

                # Get the update data from quTAG.
                _,updates = qutag.getCoincCounters()

                if (updates == 0):
                        # No new data...
                        print("waiting for new data...")
                else:
                        # get HBT function data
                        print("Integration time", qutag.getHBTIntegrationTime())
                        qutag.getHBTCorrelations(forward=0, hbtfunction=hbtfunc)
                        (capacity_value,size_value,binWidth_value, iOffset_value,values) = qutag.analyzeHBTFunction(hbtfunc)

                        # Plotting...
                        plt.cla()
                        subplt.set_title('HBT function')
                        plt.xlabel('Time??? [bins]')
                        plt.ylabel('g2?')
                        plt.plot(x, values, '-', label="Ch " + str(channel1) + " & " + str(channel2))
                        plt.legend()
                        plt.pause(0.01)

def getData(qutag, exposureTime, coincidenceWindow):
        '''
        Get the data from the quTAG device given the exposure time and coincidence window.
        '''
        # Set the exposure time (or integration time) of the internal coincidence counters in milliseconds, range = 0...65535
        qutag.setExposureTime(exposureTime*1e3)

        qutag.setCoincidenceWindow(coincidenceWindow)

        # Give some time to accumulate data
        time.sleep(exposureTime)

        # The coincidence counters are not accumulated, i.e. the counter values for the last exposure (see setExposureTime ) are returned.
        counts, updates = qutag.getCoincCounters()

        # Array for 
        CoincCounter_names = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','1/2','1/3','2/3','1/4','2/4','3/4','1/5','2/5','3/5','4/5','1/2/3','1/2/4','1/3/4','2/3/4','1/2/5','1/3/5','2/3/5','1/4/5','2/4/5','3/4/5','1/2/3/4','1/2/3/5','1/2/4/5','1/3/4/5','2/3/4/5','1/2/3/4/5']

        print("Channel/Coincidence : Counts ")
        for i in range(len(CoincCounter_names)):
                print(CoincCounter_names[i], ": ", counts[i])
        
        print("Updates: ", updates)

        dataloss = qutag.getDataLost()
        print("Data loss: ", dataloss)

        timestamps_data, timestamps_channels, valid_entries = qutag.getLastTimestamps(False)
        print("Valid timestamp entries: ", valid_entries)
        timestamps_data = timestamps_data[0:valid_entries]
        timestamps_channels = timestamps_channels[0:valid_entries]

        return counts, timestamps_data, timestamps_channels

def getDataHBT(qutag, histogramWidth, binCount, channel1, channel2, exposureTime):
        #Enable HBT mode and set parameters
        qutag.enableHBT(True)
        qutag.setHBTParams(binWidth=histogramWidth/(1e6*binCount*qutag.getTimebase()), binCount=binCount)
        qutag.setHBTInput(channel1,channel2)
        # Wait exposure time to accumulate data
        time.sleep(exposureTime)
        # Initialize the HBT function and print the integration time
        hbtfunc = qutag.createHBTFunction()
        integrationTime = qutag.getHBTIntegrationTime()
        print("Integration time: ", integrationTime)
        # Extract HBT data and return the values
        qutag.getHBTCorrelations(forward=1, hbtfunction=hbtfunc)
        cap, size, bw, offset, values = qutag.analyzeHBTFunction(hbtfunc)
        print("Capacity: ", cap, "Size: ", size, "Bin width: ", bw, "Offset: ", offset)
        return values


if __name__ == "__main__":
        #Initialize the quTAG device
        qutag = QuTAG_MC.QuTAG()

        # Deinitialize the quTAG device when done
        qutag.deInitialize()