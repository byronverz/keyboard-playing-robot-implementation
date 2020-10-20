import qwiic_vl53l1x
import time
import numpy as np

mySensor = qwiic_vl53l1x.QwiicVL53L1X(address = 0x29)
mySensor.sensor_init()
mySensor.set_distance_mode(1)
mySensor.set_roi(8,8)
mySensor.set_offset(23)
mySensor.set_inter_measurement_in_ms(250)
mySensor.set_timing_budget_in_ms(150)

key_measures = []
for k in range(25):
    ready = input("Measuring distance for key {}: ".format(k))
    if ready == 'y':
        distances = []
        for n in range(50):
            mySensor.start_ranging()
            time.sleep(.01)
            distance = mySensor.get_distance()
            time.sleep(.01)
            mySensor.stop_ranging()
            distances.append(distance)
    key_measures.append(np.mean(distances))

print(key_measures)    
x = np.arange(0,25)
z = np.polyfit(x,key_measures,1)    
y2 = x*(z[0])+z[1]

print("Key distance function: \n d(k) = {}k+{}".format(z[0],z[1])) 