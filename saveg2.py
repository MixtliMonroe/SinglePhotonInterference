try:
        import QuTAG_MC
except:
        print("Time Tagger wrapper QuTAG.py is not in the search path / same folder.")

import numpy as np
import matplotlib.pyplot as plt
import time
# 4pm
#Initialize the quTAG device
qutag = QuTAG_MC.QuTAG()

binWidth = 12 # in timebase units
binCount = 256
waitTime= 5 # in seconds

qutag.enableHg2(True)
qutag.setHg2Input(idler=1, channel1=2, channel2=3)
qutag.setHg2Params(binCount=binCount, binWidth=binWidth)

time.sleep(waitTime)

g2 = qutag.calcHg2G2(0)

with open("HeraldedG2.txt", "w") as f:
        f.write(str(g2.tolist()))

plt.plot(np.arange(2*binCount-1), g2)
plt.title(f"Integration time ~ {waitTime}s")
plt.xlabel("Bin")
plt.ylabel(r"$g^{()2}$")
plt.show()