import Gantry as G
import numpy as np
import Adafruit_BBIO.PWM as PWM
import time

gantry = G.Gantry()
step_test = [10]
step_dist = gantry.distance_to_move_calc(step_test)
dist_results = []
f_results = []
error_results = []
step_input = []

for i in range(10):
    gantry.mySensor.start_ranging()
    time.sleep(0.01)
    distance = gantry.mySensor.get_distance()
    time.sleep(0.01)
    gantry.mySensor.stop_ranging()
    dist_results.append(distance)
    error_results.append(0)
    f_results.append(0)
start = time.time()
d,f, e = gantry.step_function(step_dist[0])
end = time.time()
print("Sampling time for {} samples = {}".format(len(d),end-start))
print("Time per sample = {}".format((end-start)/len(d)))
        
for i in d:
    dist_results.append(i)
for q in f:
    f_results.append(q)
for o in e:
    error_results.append(o)

for i in range(10):
        gantry.mySensor.start_ranging()
        time.sleep(0.01)
        distance = gantry.mySensor.get_distance()
        time.sleep(0.01)
        gantry.mySensor.stop_ranging()
        dist_results.append(distance)
        error_results.append(step_dist[0]-distance)
        f_results.append(0)


dist_results = np.array(dist_results).flatten()
f_results = np.array(f_results).flatten()
error_results = np.array(error_results).flatten()
print(dist_results.flatten())
print(f_results.flatten())
print(error_results.flatten())

with open("step_dist_results.csv",'w') as dist:
    np.savetxt(dist, dist_results, fmt = '%10.3f', delimiter = ',')
    
with open("step_freq_results.csv",'w') as freq:
    np.savetxt(freq, f_results, fmt = '%10.3f', delimiter = ',')

with open("step_error_results.csv",'w') as error:
    np.savetxt(error, error_results, fmt = '%10.3f', delimiter = ',')    