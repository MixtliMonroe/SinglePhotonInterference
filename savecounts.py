try:
        import QuTAG_MC
except:
        print("Time Tagger wrapper QuTAG.py is not in the search path / same folder.")

import numpy as np
from main import getCountData

#Initialize the quTAG device
qutag = QuTAG_MC.QuTAG()

# Choose diffeent coincidence windows to test (in nanoseconds)
coincWindow = np.array([1,5,10,15,20,25,30,35,40,45,50])
# Choose 20 seconds exposure time for all measurements
Exposure = 20

# Save the data for different coincidence windows
for Cwin in coincWindow:
        print("Cwin: ", Cwin)
        with open("coincWin_" + str(int(Cwin)) + "ns.txt", "w") as f:
                counts, timestamps_data, timestamps_channels = getCountData(qutag, Exposure, int(Cwin*1e3))
                f.write(str(counts.tolist()) + "\n")
                f.write(str(timestamps_data.tolist()) + "\n")
                f.write(str(timestamps_channels.tolist()) + "\n")

# Deinitialize the quTAG device when done
qutag.deInitialize()